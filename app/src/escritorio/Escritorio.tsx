// Aplicação do escritório, versão mínima do incremento 1: monta a lista de documentos,
// gera o link e o QR code, recebe as fotos cifradas e pede a leitura ao motor local.
// A tela de revisão completa chega no incremento 2.

import { useEffect, useRef, useState } from 'react';
import QRCode from 'qrcode';
import Revisao, { Conferir, type CampoLido, type Conferencia, type Decisao } from './Revisao';
import { DEMO, ITENS_DEMO } from './demo';
import { baixarPacote } from './pacote';
import { apagar, auditar, carregar, deTexto, destruirChaveDoDia, msAteRemocao, paraTexto, salvar, type Perfil } from './armazenamento';
import type { RealtimeChannel } from '@supabase/supabase-js';
import { abrirCanal, enviar, inscrever } from '../compartilhado/canal';
import { decifrar, exportarChave, gerarChave } from '../compartilhado/cripto';
import {
  CATALOGO, EVENTOS, Remontador, VALIDADE_PAREAMENTO_MS, montarLink,
  type DocumentoPedido, type Face, type MsgConcluido, type MsgPareamento, type MsgPedaco, type MsgPendente,
} from '../compartilhado/protocolo';

const URL_CAPTURA = (import.meta.env.VITE_URL_CAPTURA as string) || `${location.origin}/captura.html`;
const URL_MOTOR = (import.meta.env.VITE_URL_MOTOR as string) || '';

type Situacao = 'aguardando' | 'recebendo' | 'lendo' | 'lido' | 'nova-foto' | 'pendente';
interface Item { uid?: string; previa?: string; doc: DocumentoPedido; situacao: Situacao; faces: Partial<Record<Face, string>>; detalhe?: string; tipo?: string; campos?: Record<string, CampoLido>; decisoes?: Record<string, Decisao>; conferencia?: Record<string, Conferencia>; conferido?: boolean; rotacao?: Partial<Record<Face, number>>; arquivos?: Partial<Record<Face, Uint8Array>> }
type Sessao = 'montando' | 'aguardando-celular' | 'expirada' | 'pareada' | 'concluida' | 'recuperada';

/** O que vai cifrado ao Supabase: o documento inteiro, arquivos em base64. */
interface Guardado { docId: string; situacao: Situacao; tipo?: string; detalhe?: string; campos?: Record<string, CampoLido>; decisoes?: Record<string, Decisao>;
  conferencia?: Record<string, Conferencia>; conferido?: boolean; rotacao?: Partial<Record<Face, number>>; arquivos?: Partial<Record<Face, string>>; previa?: string }

export default function Escritorio() {
  const [escritorio, setEscritorio] = useState('Escritório Exemplo');
  const [escolhidos, setEscolhidos] = useState<string[]>(['identidade', 'comprovante', 'fatura']);
  const [sessao, setSessao] = useState<Sessao>(DEMO ? 'concluida' : 'montando');
  const [link, setLink] = useState('');
  const [qr, setQr] = useState('');
  const [itens, setItens] = useState<Item[]>(DEMO ? (ITENS_DEMO as unknown as Item[]) : []);
  const [simularFalha, setSimularFalha] = useState(false);
  const [copiado, setCopiado] = useState(false);
  const [aberto, setAberto] = useState<string | null>(DEMO === 'revisao' ? 'identidade' : null);
  const [conferindo, setConferindo] = useState<string | null>(DEMO === 'conferencia' ? 'comprovante' : null);
  const [perfil, setPerfil] = useState<Perfil>('assistente'); // perfil simulado (RF-29): não é controle de acesso
  const [faltaMs, setFaltaMs] = useState(msAteRemocao());
  const [aviso, setAviso] = useState<string | null>(null);
  const salvos = useRef<Record<string, string>>({});
  const sessaoId = useRef<string>('');
  const canal = useRef<RealtimeChannel | null>(null);
  const falhaRef = useRef(simularFalha);
  falhaRef.current = simularFalha;

  const atualizar = (id: string, mudanca: Partial<Item>) =>
    setItens((xs) => xs.map((x) => (x.doc.id === id ? { ...x, ...mudanca, faces: { ...x.faces, ...mudanca.faces } } : x)));

  async function gerar() {
    const docs = CATALOGO.filter((d) => escolhidos.includes(d.id));
    const id = crypto.randomUUID();
    sessaoId.current = crypto.randomUUID(); // id só para medir tempo; não se liga a nenhuma pessoa
    registrar([{ etapa: 'sessao', sessao: sessaoId.current, evento: 'link_gerado', docs: docs.length }]);
    const chave = await gerarChave();
    const url = montarLink(URL_CAPTURA, { sessao: id, chave: await exportarChave(chave), escritorio, documentos: docs });
    setItens(docs.map((doc) => ({ uid: crypto.randomUUID(), doc, situacao: 'aguardando', faces: {} })));
    setLink(url);
    setQr(await QRCode.toDataURL(url, { margin: 1, width: 280 }));

    const c = await abrirCanal(id);
    canal.current = c;
    let celular: string | null = null;
    const remontador = new Remontador();
    const recebidas = new Map<string, Partial<Record<Face, Uint8Array>>>();
    const expira = setTimeout(() => { if (!celular) { setSessao('expirada'); c.unsubscribe(); } }, VALIDADE_PAREAMENTO_MS);

    c.on('broadcast', { event: EVENTOS.pareamento }, async ({ payload }) => {
      const p = payload as MsgPareamento;
      const aceito = celular === null || celular === p.celular;
      if (aceito && !celular) { celular = p.celular; clearTimeout(expira); setSessao('pareada'); registrar([{ etapa: 'sessao', sessao: sessaoId.current, evento: 'celular_pareado' }]); }
      await enviar(c, EVENTOS.pareado, { celular: p.celular, aceito });
    });

    c.on('broadcast', { event: EVENTOS.pedaco }, async ({ payload }) => {
      const m = payload as MsgPedaco;
      atualizar(m.doc, { situacao: 'recebendo' });
      const pronto = remontador.adicionar(m);
      if (!pronto) return;
      const bytes = await decifrar(chave, { iv: pronto.iv, dados: pronto.dados });
      const faces = { ...recebidas.get(pronto.envio), [pronto.face]: bytes };
      recebidas.set(pronto.envio, faces);
      // guarda o arquivo original (foto ou PDF) só na memória, para o pacote do cliente
      atualizar(pronto.doc, { faces: { [pronto.face]: URL.createObjectURL(new Blob([bytes], { type: 'image/jpeg' })) } });
      setItens((xs) => xs.map((x) => (x.doc.id === pronto.doc ? { ...x, arquivos: { ...x.arquivos, [pronto.face]: bytes } } : x)));

      const doc = docs.find((d) => d.id === pronto.doc)!;
      if (doc.temVerso && !(faces.frente && faces.verso)) return; // espera as duas faces
      recebidas.delete(pronto.envio);
      atualizar(doc.id, { situacao: 'lendo' });
      const t0 = performance.now();
      const r = await ler(doc, faces, falhaRef.current);
      registrar([{ etapa: 'captura', sessao: sessaoId.current, evento: 'documento_lido', doc: doc.id, tipo: r.tipo ?? '', fotos: m.fotos ?? 0,
        faces: Object.keys(faces).length, status: r.status, ms: Math.round(performance.now() - t0) }]);
      if (r.previa) atualizar(doc.id, { faces: { frente: r.previa }, previa: r.previa }); // PDF importado: prévia renderizada pelo motor
      if (r.rotacao) atualizar(doc.id, { rotacao: r.rotacao });
      atualizar(doc.id, { situacao: r.status === 'lido' ? 'lido' : 'nova-foto', detalhe: r.motivo ?? TIPOS[r.tipo ?? ''] ?? r.tipo, tipo: r.tipo, campos: r.campos, decisoes: {} });
      await enviar(c, EVENTOS.resultado, { envio: pronto.envio, doc: doc.id, status: r.status, motivo: r.motivo });
    });

    c.on('broadcast', { event: EVENTOS.pendente }, ({ payload }) => atualizar((payload as MsgPendente).doc, { situacao: 'pendente' }));
    c.on('broadcast', { event: EVENTOS.concluido }, ({ payload }) => {
      (payload as MsgConcluido).pendentes.forEach((d) => atualizar(d, { situacao: 'pendente' }));
      setSessao('concluida');
    });

    await inscrever(c);
    setSessao('aguardando-celular');
  }

  function encerrar() {
    canal.current?.unsubscribe();
    canal.current = null;
    itens.forEach((i) => Object.values(i.faces).forEach((u) => u?.startsWith('blob:') && URL.revokeObjectURL(u)));
    const comDados = itens.filter((i) => i.uid && i.campos);
    if (!DEMO) {
      comDados.forEach((i) => auditar('documento_excluido', perfil, i.uid, i.tipo).catch(() => {}));
      apagar(comDados.map((i) => i.uid!)).catch(() => {}); // apaga também a cópia cifrada no Supabase
    }
    salvos.current = {};
    setItens([]); setLink(''); setQr(''); setSessao('montando');
  }

  useEffect(() => () => { canal.current?.unsubscribe(); }, []);

  // Recupera o cadastro do período, se a página foi atualizada (ADR 0007)
  useEffect(() => {
    if (DEMO) return;
    carregar<Guardado>().then((docs) => {
      if (!docs.length) return;
      setItens(docs.map(({ id, conteudo: g }) => {
        const arquivos = Object.fromEntries(Object.entries(g.arquivos ?? {}).map(([f, t]) => [f, deTexto(t as string)])) as Partial<Record<Face, Uint8Array>>;
        const faces = Object.fromEntries(Object.entries(arquivos).map(([f, b]) => [f, g.previa && f === 'frente' ? g.previa
          : URL.createObjectURL(new Blob([b as BlobPart], { type: 'image/jpeg' }))])) as Partial<Record<Face, string>>;
        salvos.current[id] = JSON.stringify(g).length + ':' + g.situacao + JSON.stringify(g.decisoes ?? {}) + JSON.stringify(g.conferencia ?? {});
        return { ...g, uid: id, doc: CATALOGO.find((d) => d.id === g.docId)!, faces, arquivos };
      }).filter((i) => i.doc));
      setSessao('recuperada');
    }).catch(() => setAviso('Não foi possível recuperar o cadastro salvo.'));
  }, []);

  // Salva cada documento lido, cifrado, sempre que ele muda (decisões, conferência, arquivos)
  useEffect(() => {
    if (DEMO) return;
    const t = setTimeout(() => {
      for (const i of itens) {
        if (!i.uid || !i.campos) continue;
        const g: Guardado = { docId: i.doc.id, situacao: i.situacao, tipo: i.tipo, detalhe: i.detalhe, campos: i.campos, decisoes: i.decisoes,
          conferencia: i.conferencia, conferido: i.conferido, rotacao: i.rotacao, previa: i.previa,
          arquivos: Object.fromEntries(Object.entries(i.arquivos ?? {}).map(([f, b]) => [f, paraTexto(b as Uint8Array)])) };
        const marca = JSON.stringify(g).length + ':' + g.situacao + JSON.stringify(g.decisoes ?? {}) + JSON.stringify(g.conferencia ?? {});
        if (salvos.current[i.uid] === marca) continue;
        salvos.current[i.uid] = marca;
        salvar(i.uid, g).catch(() => setAviso('Não foi possível salvar o cadastro cifrado. Baixe o pacote para não perder os dados.'));
      }
    }, 800);
    return () => clearTimeout(t);
  }, [itens]);

  // Aviso a partir das 17h e remoção às 18h (RF-27; ADR 0007, camada 1 no navegador)
  useEffect(() => {
    const t = setInterval(() => {
      const ms = msAteRemocao();
      setFaltaMs(ms);
      if (ms > 23.9 * 3600_000 && !DEMO) { // acabou de passar das 18h
        destruirChaveDoDia().catch(() => {});
        salvos.current = {};
        setItens([]); setSessao('montando');
        setAviso('São 18h: os cadastros do dia foram removidos e a chave do dia foi destruída.');
      }
    }, 30_000);
    return () => clearInterval(t);
  }, []);

  if (sessao === 'montando') {
    return (
      <main className="escritorio">
        {aviso && <div className="aviso aviso-alerta" role="alert">{aviso}</div>}
        <h1>Novo cadastro</h1>
        <label className="campo">Nome do escritório<input value={escritorio} onChange={(e) => setEscritorio(e.target.value)} /></label>
        <fieldset className="campo">
          <legend>Documentos que o cliente vai enviar</legend>
          {CATALOGO.map((d) => (
            <label key={d.id} className="opcao">
              <input type="checkbox" checked={escolhidos.includes(d.id)}
                onChange={(e) => setEscolhidos((xs) => e.target.checked ? [...xs, d.id] : xs.filter((x) => x !== d.id))} />
              {d.rotulo}
            </label>
          ))}
        </fieldset>
        <button className="btn btn-primario" disabled={!escolhidos.length || !escritorio.trim()} onClick={gerar}>Gerar link de captura</button>
      </main>
    );
  }

  return (
    <main className="escritorio">
      <div className="topo-escritorio">
        <h1>Cadastro em andamento</h1>
        <label className="perfil">Perfil (simulado)
          <select value={perfil} onChange={(e) => setPerfil(e.target.value as Perfil)}>
            <option value="assistente">Assistente</option><option value="advogada">Advogada</option>
          </select>
        </label>
      </div>
      {aviso && <div className="aviso aviso-alerta" role="alert">{aviso}</div>}
      {faltaMs <= 60 * 60_000 && itens.some((i) => i.campos) && (
        <div className="aviso aviso-alerta" role="alert">
          <b>Às 18h, os cadastros do dia serão removidos · faltam {Math.max(1, Math.ceil(faltaMs / 60_000))} min</b>
          Baixe o pacote do cliente para guardar os arquivos e os dados no ambiente do escritório.
        </div>
      )}
      {sessao === 'recuperada' && <div className="aviso aviso-sucesso" role="status"><b>Cadastro recuperado</b>Os documentos estavam guardados cifrados no Supabase e serão removidos às 18h.</div>}
      {sessao === 'aguardando-celular' && (
        <section className="painel">
          <p>Envie o link ao cliente pelo WhatsApp ou peça para ele ler o QR code. O link vale por 5 minutos até ser aberto, e só no primeiro celular.</p>
          <div className="qr-linha">
            {qr && <img src={qr} alt="QR code do link de captura" width={200} height={200} />}
            <div className="link-caixa">
              <code>{link.slice(0, 60)}…</code>
              <button className="btn btn-primario" onClick={async () => { await navigator.clipboard.writeText(link); setCopiado(true); }}>
                {copiado ? 'Link copiado ✓' : 'Copiar link'}
              </button>
            </div>
          </div>
        </section>
      )}
      {sessao === 'expirada' && <div className="aviso aviso-erro"><b>QR expirado</b>Ninguém abriu o link em 5 minutos. <button className="btn btn-texto" onClick={encerrar}>Gerar outro</button></div>}
      {sessao === 'pareada' && <div className="aviso aviso-sucesso" role="status"><b>Celular conectado</b>O cliente está fotografando os documentos.</div>}
      {sessao === 'concluida' && <div className="aviso aviso-sucesso" role="status"><b>Cliente terminou o envio</b>Confira abaixo o que chegou e o que ficou pendente.</div>}

      <label className="opcao simulacao">
        <input type="checkbox" checked={simularFalha} onChange={(e) => setSimularFalha(e.target.checked)} />
        Simular falha de leitura no próximo documento (teste do pedido de nova foto)
      </label>

      <ul className="itens">
        {itens.map((i) => {
          const total = Object.keys(i.campos ?? {}).length;
          const decididos = Object.keys(i.decisoes ?? {}).length;
          const recusados = Object.values(i.decisoes ?? {}).filter((d) => d === 'recusado').length;
          return (
            <li key={i.doc.id} className={`item item-${i.situacao}`}>
              <div className="miniaturas">
                {(['frente', 'verso'] as Face[]).map((f) => i.faces[f] && <img key={f} src={i.faces[f]} alt={`${i.doc.rotulo}, ${f}`} />)}
              </div>
              <div>
                <b>{i.doc.rotulo}</b>
                <span className="situacao">{ROTULOS[i.situacao]}{i.detalhe ? ` · ${i.detalhe}` : ''}</span>
                {total > 0 && (
                  <span className="situacao">
                    {decididos < total ? ` · ${decididos} de ${total} campos revisados` : recusados ? ` · revisado, ${recusados} recusado(s)` : ' · revisado ✓'}
                  </span>
                )}
              </div>
              {total > 0 && (
                <div className="acoes-item">
                  <button className="btn btn-primario" onClick={() => { setAberto(i.doc.id); if (!DEMO) auditar('documento_aberto', perfil, i.uid, i.tipo).catch(() => {}); }}>{decididos < total ? 'Revisar' : 'Ver revisão'}</button>
                  {decididos === total && (
                    <button className="btn btn-secundario" onClick={() => setConferindo(i.doc.id)}>{i.conferido ? 'Conferido ✓' : 'Conferência do cliente'}</button>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {conferindo && (() => {
        const i = itens.find((x) => x.doc.id === conferindo)!;
        return (
          <div className="sobreposicao" role="dialog" aria-modal="true">
            <Conferir titulo={i.doc.rotulo} faces={i.faces} campos={i.campos ?? {}} decisoes={i.decisoes ?? {}} conferencia={i.conferencia ?? {}}
              onFechar={() => setConferindo(null)}
              onConferir={(c) => {
                atualizar(i.doc.id, { conferencia: c, conferido: true });
                registrar(Object.entries(c).map(([campo, resultado]) => ({ etapa: 'conferencia', sessao: sessaoId.current, tipo: i.tipo ?? '', campo,
                  origem: i.campos?.[campo]?.origem, resultado })));
                registrar([{ etapa: 'sessao', sessao: sessaoId.current, evento: 'conferencia_concluida', doc: i.doc.id,
                  erros: Object.values(c).filter((x) => x === 'errado').length }]);
                setConferindo(null);
              }} />
          </div>
        );
      })()}
      {aberto && (() => {
        const i = itens.find((x) => x.doc.id === aberto)!;
        return (
          <div className="sobreposicao" role="dialog" aria-modal="true">
            <Revisao
              titulo={i.doc.rotulo} tipo={TIPOS[i.tipo ?? ''] ?? ''} faces={i.faces} rotacao={i.rotacao} campos={i.campos ?? {}} decisoes={i.decisoes ?? {}}
              onFechar={() => setAberto(null)}
              onDecidir={(novas) => {
                const antes = i.decisoes ?? {};
                atualizar(i.doc.id, { decisoes: novas });
                const mudou = Object.entries(novas).filter(([k, d]) => antes[k] !== d);
                if (mudou.length && !DEMO) registrarRevisao(i.tipo ?? '', mudou, i.campos ?? {}, sessaoId.current);
                const total = Object.keys(i.campos ?? {}).length;
                if (Object.keys(novas).length === total && Object.keys(antes).length < total && !DEMO)
                  registrar([{ etapa: 'sessao', sessao: sessaoId.current, evento: 'revisao_concluida', doc: i.doc.id,
                    sem_edicao: Object.values(novas).every((d) => d === 'confirmado') }]);
              }}
            />
          </div>
        );
      })()}
      {itens.some((i) => i.campos) && (
        <section className="painel pacote">
          <div>
            <b>Pacote do cliente</b>
            <p className="situacao">Arquivos originais e dados, num .zip salvo onde você escolher. {
              itens.some((i) => Object.keys(i.decisoes ?? {}).length < Object.keys(i.campos ?? {}).length)
                ? 'Atenção: há campos ainda não revisados; eles vão marcados como "não revisado".' : 'Todos os campos foram revisados.'}</p>
          </div>
          <button className="btn btn-primario" onClick={() => {
            const docs = itens.filter((i) => i.campos).map((i) => ({ rotulo: i.doc.rotulo, tipo: i.tipo ?? '', arquivos: i.arquivos ?? {}, campos: i.campos ?? {}, decisoes: i.decisoes ?? {} }));
            baixarPacote(docs);
            if (!DEMO) auditar('pacote_baixado', perfil).catch(() => {});
            registrar([{ etapa: 'sessao', sessao: sessaoId.current, evento: 'pacote_baixado', docs: docs.length }]);
          }}>⬇ Baixar pacote do cliente</button>
        </section>
      )}
      <button className="btn btn-texto" onClick={encerrar}>Encerrar sessão (apaga as imagens da tela e da memória)</button>
    </main>
  );
}

const TIPOS: Record<string, string> = { cnh: 'CNH', cin: 'CIN', rg: 'RG antigo', nfe: 'NF-e', boleto: 'Boleto', fatura: 'Fatura', nao_reconhecido: 'Não reconhecido' };

const ROTULOS: Record<Situacao, string> = {
  aguardando: 'Aguardando', recebendo: 'Recebendo…', lendo: 'Lendo…', lido: '✓ Lido',
  'nova-foto': 'Nova foto pedida ao cliente', pendente: '⏸ Cliente não tem agora',
};

/** Registro de revisão (RF-22): só tipo, campo, origem e resultado. Nunca valores nem imagem. */
function registrarRevisao(tipo: string, mudancas: [string, Decisao][], campos: Record<string, CampoLido>, sessao: string) {
  registrar(mudancas.map(([campo, resultado]) => ({ etapa: 'revisao', sessao, tipo, campo, origem: campos[campo]?.origem, validado: campos[campo]?.validado, resultado })));
}

/** Registro local de medição (RF-22): só eventos, contagens e tempos. Nunca valores nem imagens. */
function registrar(eventos: object[]) {
  if (DEMO) return;
  fetch(`${URL_MOTOR}/revisao`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(eventos) }).catch(() => {});
}

async function ler(doc: DocumentoPedido, faces: Partial<Record<Face, Uint8Array>>, falhar: boolean) {
  const corpo = new FormData();
  for (const [face, bytes] of Object.entries(faces)) corpo.append(face, new Blob([bytes!], { type: 'image/jpeg' }), `${face}.jpg`);
  const r = await fetch(`${URL_MOTOR}/processar?doc=${doc.id}${falhar ? '&simular=falha' : ''}`, { method: 'POST', body: corpo });
  return (await r.json()) as { status: 'lido' | 'nova-foto'; motivo?: string; tipo?: string; campos?: Record<string, CampoLido>; previa?: string; rotacao?: Partial<Record<Face, number>> };
}
