import { useCallback, useEffect, useReducer, useRef, useState } from 'react';
import type { RealtimeChannel } from '@supabase/supabase-js';
import { abrirCanal, enviar, inscrever } from '../compartilhado/canal';
import { cifrar, importarChave } from '../compartilhado/cripto';
import {
  ESPERA_LEITURA_MS, EVENTOS, dividirEmPedacos, lerLink,
  type DadosDoLink, type Face, type MsgPareado, type MsgResultado,
} from '../compartilhado/protocolo';
import { abrirCamera, avaliarQuadro, fecharCamera, fotografar, ligarLanterna, temLanterna } from './camera';
import { docAtual, inicial, proximoIdx, reduzir } from './fluxo';
import { MENSAGENS, dicaAoVivo } from './qualidade';

import { DEMO, DEMO_LINK, estadoDemo } from './demo';

const link: DadosDoLink | null = DEMO ? DEMO_LINK : lerLink(window.location.href);

export default function Captura() {
  const [e, despachar] = useReducer(reduzir, DEMO ? estadoDemo(DEMO) : inicial(link?.documentos ?? []));
  const canal = useRef<RealtimeChannel | null>(null);
  const chave = useRef<CryptoKey | null>(null);
  const fotos = useRef<Partial<Record<Face, Uint8Array>>>({}); // só em memória, até o envio
  const envioAtual = useRef<string>('');
  const [previa, setPrevia] = useState<string | null>(DEMO === 'qualidade' ? '/demo/cnh.jpg' : null);
  const titulo = useRef<HTMLHeadingElement>(null);
  const [avisoArquivo, setAvisoArquivo] = useState<string | null>(null);

  // Pareamento com o escritório (RF-03): só o primeiro celular é aceito.
  useEffect(() => {
    if (DEMO) return; // demonstração: sem canal, sem pareamento
    if (!link) { despachar({ tipo: 'LINK_INVALIDO' }); return; }
    // Remove a chave da barra de endereço e do histórico do navegador.
    history.replaceState(null, '', window.location.pathname + window.location.search);
    const celular = crypto.randomUUID();
    let vivo = true;
    const limite = setTimeout(() => vivo && despachar({ tipo: 'LINK_INVALIDO' }), 15_000);
    (async () => {
      try {
        chave.current = await importarChave(link.chave);
        const c = await abrirCanal(link.sessao);
        canal.current = c;
        c.on('broadcast', { event: EVENTOS.pareado }, ({ payload }) => {
          const p = payload as MsgPareado;
          if (p.celular !== celular) return;
          clearTimeout(limite);
          despachar({ tipo: p.aceito ? 'PAREADO' : 'LINK_INVALIDO' });
        });
        c.on('broadcast', { event: EVENTOS.resultado }, ({ payload }) => {
          const r = payload as MsgResultado;
          if (r.envio !== envioAtual.current) return;
          despachar(r.status === 'lido' ? { tipo: 'LIDO' } : { tipo: 'NOVA_FOTO', motivo: r.motivo ?? 'Não conseguimos ler o documento' });
        });
        await inscrever(c);
        await enviar(c, EVENTOS.pareamento, { celular });
      } catch {
        if (vivo) despachar({ tipo: 'LINK_INVALIDO' });
      }
    })();
    return () => { vivo = false; clearTimeout(limite); };
  }, []);

  // Leva o foco ao título a cada troca de tela (leitores de tela anunciam a mudança).
  useEffect(() => { titulo.current?.focus(); }, [e.tela, e.idx]);

  // Envio cifrado e espera pela leitura (RF-31: até 30 s).
  useEffect(() => {
    if (e.tela !== 'lendo' || !canal.current || !chave.current) return;
    const doc = docAtual(e);
    const fotosDoc = e.fotosDoc; // nº de fotos tiradas neste documento (sem dado pessoal)
    const envio = crypto.randomUUID();
    envioAtual.current = envio;
    const relogio = setTimeout(() => despachar({ tipo: 'TEMPO_ESGOTADO' }), ESPERA_LEITURA_MS);
    (async () => {
      for (const face of ['frente', 'verso'] as Face[]) {
        const bytes = fotos.current[face];
        if (!bytes) continue;
        const { iv, dados } = await cifrar(chave.current!, bytes);
        for (const p of dividirEmPedacos(envio, doc.id, face, iv, dados, fotosDoc)) await enviar(canal.current!, EVENTOS.pedaco, p);
      }
      fotos.current = {}; // a foto deixa de existir no celular depois de enviada
    })().catch(() => despachar({ tipo: 'TEMPO_ESGOTADO' }));
    return () => clearTimeout(relogio);
  }, [e.tela]); // eslint-disable-line react-hooks/exhaustive-deps

  // Avisa o escritório do que ficou pendente e encerra.
  useEffect(() => {
    if (e.tela === 'fim' && canal.current) {
      const pendentes = e.docs.filter((d) => e.situacao[d.id] === 'nao-tenho').map((d) => d.id);
      enviar(canal.current, EVENTOS.concluido, { pendentes }).finally(() => canal.current?.unsubscribe());
    }
  }, [e.tela]); // eslint-disable-line react-hooks/exhaustive-deps

  const naoTenho = useCallback(async () => {
    if (canal.current) await enviar(canal.current, EVENTOS.pendente, { doc: docAtual(e).id }).catch(() => {});
    despachar({ tipo: 'NAO_TENHO' });
  }, [e]);

  const pedirCamera = useCallback(async () => {
    const v = document.createElement('video');
    v.muted = true; v.setAttribute('playsinline', '');
    try { fecharCamera(await abrirCamera(v), v); despachar({ tipo: 'CAMERA_OK' }); }
    catch { despachar({ tipo: 'CAMERA_NEGADA' }); }
  }, []);

  const escritorio = link?.escritorio ?? 'o escritório';
  const doc = e.docs[e.idx];
  const n = e.docs.length;
  const H = (t: string) => <h1 ref={titulo} tabIndex={-1}>{t}</h1>;
  const Privacidade = () => <p className="privacidade">🔒 <span>Só a equipe de {escritorio} vê seus documentos.</span></p>;

  switch (e.tela) {
    case 'conectando':
      return <Tela><div className="centro"><div className="carregando" role="status" aria-label="Conectando" /><p className="suave">Conectando ao escritório…</p></div></Tela>;

    case 'link-invalido':
      return <Tela>{H('Este link não vale mais')}<div className="aviso aviso-erro">Ele já foi usado ou passou do tempo. Peça um novo ao escritório.</div></Tela>;

    case 'abertura':
      return (
        <Tela>
          <span className="marca">{escritorio}</span>
          {H('Olá! Vamos enviar seus documentos.')}
          <p>São {n} documento{n > 1 ? 's' : ''}:</p>
          <ul className="lista">{e.docs.map((d) => <li key={d.id}>{d.rotulo}</li>)}</ul>
          <p className="suave">Leva uns 3 minutos. Tenha os documentos em mãos.</p>
          <Espaco />
          <button className="btn btn-primario" onClick={() => despachar({ tipo: 'COMECAR' })}>Começar</button>
          <Privacidade />
          <details className="saiba-mais"><summary>Saiba mais</summary>
            <p>As fotos vão cifradas direto para a equipe de {escritorio}. Só pessoas autorizadas têm acesso, e cada acesso é registrado. As fotos não ficam salvas no seu celular.</p>
          </details>
        </Tela>
      );

    case 'permissao':
      return (
        <Tela>
          {H('Precisamos usar sua câmera')}
          <p>Para fotografar os documentos, o celular vai pedir permissão.</p>
          <p>Toque em <b>“Permitir”</b> na próxima mensagem.</p>
          <Espaco />
          <button className="btn btn-primario" onClick={pedirCamera}>Entendi</button>
        </Tela>
      );

    case 'camera-negada':
      return (
        <Tela>
          {H('A câmera está bloqueada')}
          <p>Sem ela não dá para fotografar os documentos.</p>
          <p>Para liberar:</p>
          <ol className="lista"><li>Toque no “aA” ou no cadeado ao lado do endereço</li><li>Permita a câmera</li><li>Toque em “Tentar de novo”</li></ol>
          <Espaco />
          <button className="btn btn-primario" onClick={() => despachar({ tipo: 'TENTAR_DE_NOVO' })}>Tentar de novo</button>
        </Tela>
      );

    case 'documento':
      return (
        <Tela>
          <span className="marca">{escritorio}</span>
          <Progresso atual={e.idx + 1} total={n} />
          {H(doc.rotulo)}
          <p className="suave">{doc.ajuda}</p>
          <Espaco />
          <button className="btn btn-primario" onClick={() => despachar({ tipo: 'FOTOGRAFAR' })}>📷 Fotografar</button>
          <label className="btn btn-secundario-claro">
            📁 Importar dos arquivos
            <input type="file" accept="image/*,application/pdf" className="visualmente-oculto"
              onChange={async (ev) => {
                const arq = ev.target.files?.[0];
                ev.target.value = '';
                if (!arq) return;
                if (arq.size > 15 * 1024 * 1024) { setAvisoArquivo('O arquivo é grande demais (máximo de 15 MB).'); return; }
                setAvisoArquivo(null);
                fotos.current = { frente: new Uint8Array(await arq.arrayBuffer()) };
                despachar({ tipo: 'IMPORTADO' });
              }} />
          </label>
          {avisoArquivo && <div className="aviso aviso-alerta" role="alert">{avisoArquivo}</div>}
          <button className="btn btn-texto" onClick={naoTenho}>Não tenho agora</button>
          <Privacidade />
        </Tela>
      );

    case 'camera':
      return (
        <Camera
          rotulo={`${doc.rotulo}${e.face === 'verso' ? ' (verso)' : e.face === 'frente' && doc.temVerso ? ' (frente)' : ''}`}
          formato={doc.grupo === 'identificacao' ? 'cartao' : 'folha'}
          onCancelar={() => despachar({ tipo: 'CANCELAR' })}
          onNegada={() => despachar({ tipo: 'CAMERA_NEGADA' })}
          onFoto={(bytes, url, motivo) => {
            if (previa) URL.revokeObjectURL(previa);
            setPrevia(url);
            fotos.current[e.face] = bytes; // guardada mesmo se recusada: na 3ª recusa, é ela que segue
            despachar(motivo ? { tipo: 'FOTO_RUIM', motivo } : { tipo: 'FOTO_BOA' });
          }}
        />
      );

    case 'qualidade': {
      const m = MENSAGENS[e.motivoQualidade ?? 'escura'];
      return (
        <Tela>
          {previa && <img className="miniatura" src={previa} alt="Miniatura da foto tirada" />}
          <div className="aviso aviso-alerta" role="alert"><b>{m.titulo}</b>{m.dica}</div>
          <Espaco />
          <button className="btn btn-primario" onClick={() => despachar({ tipo: 'TIRAR_OUTRA' })}>Tirar outra</button>
        </Tela>
      );
    }

    case 'verso':
      return (
        <Tela>
          <div className="aviso aviso-sucesso">✓ Frente fotografada</div>
          {H('Agora vire o documento e fotografe o verso.')}
          <Espaco />
          <button className="btn btn-primario" onClick={() => despachar({ tipo: 'FOTOGRAFAR_VERSO' })}>📷 Fotografar o verso</button>
        </Tela>
      );

    case 'lendo':
      return (
        <Tela>
          <div className="centro" role="status" aria-live="polite">
            <div className="carregando" />
            {H('Lendo seu documento…')}
            <p className="suave">Isso leva alguns segundos. Mantenha o documento por perto.</p>
          </div>
        </Tela>
      );

    case 'nova-foto':
      return (
        <Tela>
          {H('Vamos tentar de novo')}
          <div className="aviso aviso-alerta" role="alert"><b>{e.motivoLeitura}</b>Incline um pouco o documento e fotografe de novo.</div>
          <Espaco />
          <button className="btn btn-primario" onClick={() => despachar({ tipo: 'FOTOGRAFAR' })}>Fotografar de novo</button>
        </Tela>
      );

    case 'enviado':
    case 'demorado': {
      const prox = proximoIdx(e);
      return (
        <Tela>
          {e.tela === 'enviado'
            ? <div className="aviso aviso-sucesso" role="status"><b>✓ {doc.rotulo} enviado</b></div>
            : <div className="aviso aviso-sucesso" role="status"><b>✓ Recebemos sua foto</b>A leitura está demorando. Se for preciso outra foto, o escritório avisa você.</div>}
          <Espaco />
          <button className="btn btn-primario" onClick={() => despachar({ tipo: 'PROXIMO' })}>
            {prox === null ? 'Terminar' : `Próximo: ${e.docs[prox].rotulo} →`}
          </button>
        </Tela>
      );
    }

    case 'fim': {
      const pendentes = e.docs.filter((d) => e.situacao[d.id] === 'nao-tenho');
      return (
        <Tela>
          {H('✓ Pronto!')}
          <p>A equipe de {escritorio} já recebeu seus documentos.</p>
          <ul className="lista sem-marcador">
            {e.docs.map((d) => <li key={d.id}>{e.situacao[d.id] === 'nao-tenho' ? '⏸' : '✓'} {d.rotulo}</li>)}
          </ul>
          {pendentes.length > 0 && <div className="aviso aviso-alerta">Você disse que não tem agora: {pendentes.map((d) => d.rotulo).join(', ')}. O escritório vai te mandar um novo link.</div>}
          <Espaco />
          <p className="suave">Pode fechar esta página. As fotos não ficam salvas no seu celular.</p>
        </Tela>
      );
    }
  }
}

function Tela({ children }: { children: React.ReactNode }) {
  return <main className="tela">{children}</main>;
}
function Espaco() { return <div className="espaco" />; }
function Progresso({ atual, total }: { atual: number; total: number }) {
  return (
    <div className="progresso" aria-label={`Documento ${atual} de ${total}`}>
      Documento {atual} de {total}
      {Array.from({ length: total }, (_, i) => <i key={i} className={i < atual ? 'feito' : ''} />)}
    </div>
  );
}

function Camera({ rotulo, formato, onFoto, onCancelar, onNegada }: {
  rotulo: string;
  formato: 'cartao' | 'folha';
  onFoto: (bytes: Uint8Array, previa: string, motivo?: 'escura' | 'tremida' | 'reflexo') => void;
  onCancelar: () => void;
  onNegada: () => void;
}) {
  const video = useRef<HTMLVideoElement>(null);
  const negada = useRef(onNegada);
  const [dica, setDica] = useState('Enquadre o documento na moldura');
  const [ocupado, setOcupado] = useState(false);
  const fluxo = useRef<MediaStream | null>(null);
  const [lanternaDisponivel, setLanternaDisponivel] = useState(false);
  const [lanterna, setLanterna] = useState(false);

  useEffect(() => {
    let stream: MediaStream | null = null;
    let vivo = true;
    if (DEMO) { setDica('✓ Pronto, pode fotografar'); setLanternaDisponivel(true); return; }
    abrirCamera(video.current!).then((s) => {
      if (!vivo) { fecharCamera(s); return; }
      stream = s; fluxo.current = s;
      setLanternaDisponivel(temLanterna(s));
    }).catch(() => negada.current());
    const t = setInterval(() => { const r = video.current && avaliarQuadro(video.current); if (r) setDica(dicaAoVivo(r)); }, 600);
    const v = video.current;
    return () => { vivo = false; clearInterval(t); fecharCamera(stream, v); };
  }, []);

  // Câmera em tela cheia, com quatro cantos indicando a área do documento
  // (decisão do teste no celular, 11/11/2026: a moldura fechada ficava pequena).
  return (
    <main className="camera-cheia">
      {DEMO ? <img className="demo-camera" src="/demo/cnh.jpg" alt="" /> : <video ref={video} playsInline muted aria-label="Imagem da câmera" />}
      <header className="camera-topo">
        <span>{rotulo}</span>
        <div className="camera-acoes">
          {lanternaDisponivel && (
            <button
              className={`camera-flash${lanterna ? ' ligado' : ''}`} aria-pressed={lanterna}
              aria-label={lanterna ? 'Desligar o flash' : 'Ligar o flash'}
              onClick={async () => { if (await ligarLanterna(fluxo.current, !lanterna)) setLanterna(!lanterna); }}
            >⚡ {lanterna ? 'Flash ligado' : 'Flash'}</button>
          )}
          <button className="camera-fechar" onClick={onCancelar} aria-label="Cancelar e voltar">✕</button>
        </div>
      </header>
      <div className={`cantos cantos-${formato}`} aria-hidden="true"><i /><i /><i /><i /></div>
      <footer className="camera-base">
        <p className="dica" aria-live="polite">
          {dica}{lanternaDisponivel && !lanterna && dica.includes('luz') ? ' ou ligue o flash ⚡' : ''}
        </p>
        <button
          className="disparador" aria-label="Tirar foto" disabled={ocupado}
          onClick={async () => {
            if (!video.current) return;
            setOcupado(true);
            const f = await fotografar(video.current);
            onFoto(f.bytes, f.previa, f.qualidade.motivo);
          }}
        />
      </footer>
    </main>
  );
}
