// Aplicação do escritório, versão mínima do incremento 1: monta a lista de documentos,
// gera o link e o QR code, recebe as fotos cifradas e pede a leitura ao motor local.
// A tela de revisão completa chega no incremento 2.

import { useEffect, useRef, useState } from 'react';
import QRCode from 'qrcode';
import { CAMPOS_LARGOS, NOMES_CAMPOS, formatarValor } from './formatar';
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
interface CampoLido { valor: string; origem: string; validado: boolean }
interface Item { doc: DocumentoPedido; situacao: Situacao; faces: Partial<Record<Face, string>>; detalhe?: string; campos?: Record<string, CampoLido> }
type Sessao = 'montando' | 'aguardando-celular' | 'expirada' | 'pareada' | 'concluida';

export default function Escritorio() {
  const [escritorio, setEscritorio] = useState('Escritório Exemplo');
  const [escolhidos, setEscolhidos] = useState<string[]>(['identidade', 'comprovante', 'fatura']);
  const [sessao, setSessao] = useState<Sessao>('montando');
  const [link, setLink] = useState('');
  const [qr, setQr] = useState('');
  const [itens, setItens] = useState<Item[]>([]);
  const [simularFalha, setSimularFalha] = useState(false);
  const [copiado, setCopiado] = useState(false);
  const canal = useRef<RealtimeChannel | null>(null);
  const falhaRef = useRef(simularFalha);
  falhaRef.current = simularFalha;

  const atualizar = (id: string, mudanca: Partial<Item>) =>
    setItens((xs) => xs.map((x) => (x.doc.id === id ? { ...x, ...mudanca, faces: { ...x.faces, ...mudanca.faces } } : x)));

  async function gerar() {
    const docs = CATALOGO.filter((d) => escolhidos.includes(d.id));
    const id = crypto.randomUUID();
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
      if (aceito && !celular) { celular = p.celular; clearTimeout(expira); setSessao('pareada'); }
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
      const r = await ler(doc, faces, falhaRef.current);
      atualizar(doc.id, { situacao: r.status === 'lido' ? 'lido' : 'nova-foto', detalhe: r.motivo ?? TIPOS[r.tipo ?? ''] ?? r.tipo, campos: r.campos });
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
        {itens.map((i) => (
          <li key={i.doc.id} className={`item item-${i.situacao}`}>
            <div className="miniaturas">
              {(['frente', 'verso'] as Face[]).map((f) => i.faces[f] && <img key={f} src={i.faces[f]} alt={`${i.doc.rotulo}, ${f}`} />)}
            </div>
            <div>
              <b>{i.doc.rotulo}</b>
              <span className="situacao">{ROTULOS[i.situacao]}{i.detalhe ? ` · ${i.detalhe}` : ''}</span>
              {i.campos && Object.keys(i.campos).length > 0 && (
                <dl className="campos">
                  {Object.entries(i.campos).map(([k, c]) => (
                    <div key={k} className={CAMPOS_LARGOS.has(k) ? 'largo' : ''}>
                      <dt>{NOMES_CAMPOS[k] ?? k.replace(/_/g, ' ')}</dt>
                      <dd>{formatarValor(k, c.valor)}{c.validado && <span className="validado" title="Conferido por dígito verificador ou MRZ" aria-label="conferido"> ✓</span>}
                        {c.origem === 'ia' && !c.validado && <span className="origem-ia" title="Encontrado pela IA: confira com atenção">IA · conferir</span>}</dd>
                    </div>
                  ))}
                </dl>
              )}
            </div>
          </li>
        ))}
      </ul>
      <button className="btn btn-texto" onClick={encerrar}>Encerrar sessão (apaga as imagens da tela e da memória)</button>
    </main>
  );
}

const TIPOS: Record<string, string> = { cnh: 'CNH', cin: 'CIN', rg: 'RG antigo', nfe: 'NF-e', boleto: 'Boleto', fatura: 'Fatura', nao_reconhecido: 'Não reconhecido' };

const ROTULOS: Record<Situacao, string> = {
  aguardando: 'Aguardando', recebendo: 'Recebendo…', lendo: 'Lendo…', lido: '✓ Lido',
  'nova-foto': 'Nova foto pedida ao cliente', pendente: '⏸ Cliente não tem agora',
};

async function ler(doc: DocumentoPedido, faces: Partial<Record<Face, Uint8Array>>, falhar: boolean) {
  const corpo = new FormData();
  for (const [face, bytes] of Object.entries(faces)) corpo.append(face, new Blob([bytes!], { type: 'image/jpeg' }), `${face}.jpg`);
  const r = await fetch(`${URL_MOTOR}/processar?doc=${doc.id}${falhar ? '&simular=falha' : ''}`, { method: 'POST', body: corpo });
  return (await r.json()) as { status: 'lido' | 'nova-foto'; motivo?: string; tipo?: string; campos?: Record<string, CampoLido> };
}
