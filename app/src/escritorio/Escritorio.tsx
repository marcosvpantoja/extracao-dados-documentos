// Aplicação do escritório, versão mínima do incremento 1: monta a lista de documentos,
// gera o link e o QR code, recebe as fotos cifradas e pede a leitura ao motor local.
// A tela de revisão completa chega no incremento 2.

import { useEffect, useRef, useState } from 'react';
import QRCode from 'qrcode';
import Revisao, { Conferir, type CampoLido, type Conferencia, type Decisao } from './Revisao';
import { DEMO, ITENS_DEMO } from './demo';
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
interface Item { doc: DocumentoPedido; situacao: Situacao; faces: Partial<Record<Face, string>>; detalhe?: string; tipo?: string; campos?: Record<string, CampoLido>; decisoes?: Record<string, Decisao>; conferencia?: Record<string, Conferencia>; conferido?: boolean }
type Sessao = 'montando' | 'aguardando-celular' | 'expirada' | 'pareada' | 'concluida';

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
    setItens(docs.map((doc) => ({ doc, situacao: 'aguardando', faces: {} })));
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
      atualizar(pronto.doc, { faces: { [pronto.face]: URL.createObjectURL(new Blob([bytes], { type: 'image/jpeg' })) } });

      const doc = docs.find((d) => d.id === pronto.doc)!;
      if (doc.temVerso && !(faces.frente && faces.verso)) return; // espera as duas faces
      recebidas.delete(pronto.envio);
      atualizar(doc.id, { situacao: 'lendo' });
      const t0 = performance.now();
      const r = await ler(doc, faces, falhaRef.current);
      registrar([{ etapa: 'captura', sessao: sessaoId.current, evento: 'documento_lido', doc: doc.id, tipo: r.tipo ?? '', fotos: m.fotos ?? 0,
        faces: Object.keys(faces).length, status: r.status, ms: Math.round(performance.now() - t0) }]);
      if (r.previa) atualizar(doc.id, { faces: { frente: r.previa } }); // PDF importado: prévia renderizada pelo motor
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
    itens.forEach((i) => Object.values(i.faces).forEach((u) => u && URL.revokeObjectURL(u)));
    setItens([]); setLink(''); setQr(''); setSessao('montando');
  }

  useEffect(() => () => { canal.current?.unsubscribe(); }, []);

  if (sessao === 'montando') {
    return (
      <main className="escritorio">
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
      <h1>Cadastro em andamento</h1>
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
                  <button className="btn btn-primario" onClick={() => setAberto(i.doc.id)}>{decididos < total ? 'Revisar' : 'Ver revisão'}</button>
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
              titulo={i.doc.rotulo} tipo={TIPOS[i.tipo ?? ''] ?? ''} faces={i.faces} campos={i.campos ?? {}} decisoes={i.decisoes ?? {}}
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
  return (await r.json()) as { status: 'lido' | 'nova-foto'; motivo?: string; tipo?: string; campos?: Record<string, CampoLido>; previa?: string };
}
