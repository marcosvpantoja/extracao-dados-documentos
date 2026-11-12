// Tela de revisão (HU-03, HU-04, HU-05; RF-16, RF-17): foto à esquerda, campos à direita.
// Cada campo tem ✓ e ✗; "Confirmar os demais" fecha os que não foram marcados.
// Campos que pedem atenção (vindos da IA ou sem conferência automática) aparecem primeiro.

import { useState } from 'react';
import type { Face } from '../compartilhado/protocolo';
import { NOMES_CAMPOS, formatarValor } from './formatar';

export interface CampoLido { valor: string; origem: string; validado: boolean }
export type Decisao = 'confirmado' | 'recusado';
export type Conferencia = 'certo' | 'errado';

export function ordenarParaRevisao(campos: Record<string, CampoLido>): [string, CampoLido][] {
  const peso = (c: CampoLido) => (c.origem === 'ia' ? 0 : c.validado ? 2 : 1);
  return Object.entries(campos).sort(([, a], [, b]) => peso(a) - peso(b));
}

/**
 * Conferência pelo cliente (HU-23, métrica de proteção): depois da revisão, o tester vê na tela do
 * escritório os dados JÁ CONFIRMADOS e marca o que estiver errado. Fica no Mac, e não no celular,
 * para nenhum dado voltar ao aparelho do cliente.
 */
export function Conferir({ titulo, faces, campos, decisoes, conferencia, onConferir, onFechar }: {
  titulo: string;
  faces: Partial<Record<Face, string>>;
  campos: Record<string, CampoLido>;
  decisoes: Record<string, Decisao>;
  conferencia: Record<string, Conferencia>;
  onConferir: (c: Record<string, Conferencia>, concluir: boolean) => void;
  onFechar: () => void;
}) {
  const confirmados = Object.entries(campos).filter(([k]) => decisoes[k] === 'confirmado');
  const [marcados, setMarcados] = useState<Record<string, Conferencia>>(conferencia);
  const foto = faces.frente ?? faces.verso;
  return (
    <section className="revisao conferencia" aria-label={`Conferência do cliente: ${titulo}`}>
      <header className="revisao-topo">
        <div><h2>Confira seus dados · {titulo}</h2><span className="situacao">Para o cliente: marque o que estiver errado. O que não for marcado será considerado certo.</span></div>
        <button className="btn btn-texto" onClick={onFechar}>Fechar</button>
      </header>
      <div className="revisao-corpo">
        <div className="revisao-foto"><div className="foto-area">{foto && <img src={foto} alt={titulo} style={{ width: '100%' }} />}</div></div>
        <div className="revisao-campos">
          <ul>
            {confirmados.map(([k, c]) => (
              <li key={k} className={`campo-rev${marcados[k] === 'errado' ? ' recusado' : ''}`}>
                <div className="campo-texto"><span className="campo-nome">{NOMES_CAMPOS[k] ?? k}</span><span className="campo-valor">{formatarValor(k, c.valor)}</span></div>
                <button className={`btn-errado${marcados[k] === 'errado' ? ' marcado' : ''}`} aria-pressed={marcados[k] === 'errado'}
                  onClick={() => setMarcados((m) => ({ ...m, [k]: m[k] === 'errado' ? 'certo' : 'errado' }))}>
                  {marcados[k] === 'errado' ? '✗ Está errado' : 'Está errado?'}
                </button>
              </li>
            ))}
          </ul>
          <button className="btn btn-primario" onClick={() => onConferir(Object.fromEntries(confirmados.map(([k]) => [k, marcados[k] ?? 'certo'])), true)}>
            Concluir conferência
          </button>
        </div>
      </div>
    </section>
  );
}

export default function Revisao({ titulo, tipo, faces, campos, decisoes, onDecidir, onFechar }: {
  titulo: string;
  tipo: string;
  faces: Partial<Record<Face, string>>;
  campos: Record<string, CampoLido>;
  decisoes: Record<string, Decisao>;
  onDecidir: (novas: Record<string, Decisao>) => void;
  onFechar: () => void;
}) {
  const disponiveis = (['frente', 'verso'] as Face[]).filter((f) => faces[f]);
  const [face, setFace] = useState<Face>(disponiveis[0] ?? 'frente');
  const [zoom, setZoom] = useState(1);
  const lista = ordenarParaRevisao(campos);
  const pendentes = lista.filter(([k]) => !decisoes[k]).length;

  return (
    <section className="revisao" aria-label={`Revisão: ${titulo}`}>
      <header className="revisao-topo">
        <div><h2>{titulo}</h2><span className="situacao">{tipo}</span></div>
        <button className="btn btn-texto" onClick={onFechar}>Fechar</button>
      </header>
      <div className="revisao-corpo">
        <div className="revisao-foto">
          <div className="foto-area">
            {faces[face] && <img src={faces[face]} alt={`${titulo}, ${face}`} style={{ width: `${zoom * 100}%` }} />}
          </div>
          <div className="foto-controles">
            {disponiveis.length > 1 && disponiveis.map((f) => (
              <button key={f} className={`aba${f === face ? ' ativa' : ''}`} aria-pressed={f === face} onClick={() => setFace(f)}>{f}</button>
            ))}
            <span className="espaco-h" />
            <button className="aba" aria-label="Diminuir zoom" onClick={() => setZoom((z) => Math.max(1, z - 0.5))}>－</button>
            <span className="zoom">{Math.round(zoom * 100)}%</span>
            <button className="aba" aria-label="Aumentar zoom" onClick={() => setZoom((z) => Math.min(4, z + 0.5))}>＋</button>
          </div>
        </div>
        <div className="revisao-campos">
          <ul>
            {lista.map(([k, c]) => {
              const d = decisoes[k];
              return (
                <li key={k} className={`campo-rev${d ? ` ${d}` : ''}`}>
                  <div className="campo-texto">
                    <span className="campo-nome">
                      {NOMES_CAMPOS[k] ?? k}
                      {c.validado && <span className="validado" title="Conferido por dígito verificador ou MRZ"> ✓ conferido</span>}
                      {c.origem === 'ia' && !c.validado && <span className="origem-ia">IA · conferir</span>}
                    </span>
                    <span className="campo-valor">{formatarValor(k, c.valor)}</span>
                  </div>
                  <div className="campo-acoes" role="group" aria-label={`Decisão sobre ${NOMES_CAMPOS[k] ?? k}`}>
                    <button className={`decidir ok${d === 'confirmado' ? ' marcado' : ''}`} aria-pressed={d === 'confirmado'}
                      aria-label={`Confirmar ${NOMES_CAMPOS[k] ?? k}`} onClick={() => onDecidir({ ...decisoes, [k]: 'confirmado' })}>✓</button>
                    <button className={`decidir nao${d === 'recusado' ? ' marcado' : ''}`} aria-pressed={d === 'recusado'}
                      aria-label={`Recusar ${NOMES_CAMPOS[k] ?? k}`} onClick={() => onDecidir({ ...decisoes, [k]: 'recusado' })}>✗</button>
                  </div>
                </li>
              );
            })}
          </ul>
          <button className="btn btn-primario" disabled={pendentes === 0}
            onClick={() => onDecidir(Object.fromEntries(lista.map(([k]) => [k, decisoes[k] ?? 'confirmado'])))}>
            {pendentes === lista.length ? 'Confirmar todos' : pendentes > 0 ? `Confirmar os demais (${pendentes})` : 'Revisão concluída ✓'}
          </button>
        </div>
      </div>
    </section>
  );
}
