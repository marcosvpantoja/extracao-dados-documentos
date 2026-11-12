// Máquina de estados da página de captura, espelho do "Fluxo das telas"
// (docs/ux/captura-wireframes.md). Funções puras, testadas sem navegador.

import type { DocumentoPedido, Face } from '../compartilhado/protocolo';
import { TENTATIVAS_MAXIMAS, type MotivoQualidade } from './qualidade';

export type Tela =
  | 'conectando' // antes da tela 1, enquanto pareia com o escritório
  | 'link-invalido' // E1
  | 'abertura' // 1
  | 'permissao' // 2
  | 'camera-negada' // 2b
  | 'documento' // 3
  | 'camera' // 4
  | 'qualidade' // 5
  | 'verso' // 6
  | 'lendo' // 7
  | 'nova-foto' // 7b
  | 'enviado' // 8
  | 'demorado' // E2
  | 'fim'; // 9

export type SituacaoDoc = 'enviado' | 'nao-tenho' | 'demorado';

export interface Estado {
  tela: Tela;
  docs: DocumentoPedido[];
  idx: number;
  face: Face;
  situacao: Record<string, SituacaoDoc>;
  recusas: number; // fotos recusadas seguidas na face atual
  fotosDoc: number; // fotos tiradas no documento atual, para medir o KR4 (aceita de primeira)
  motivoQualidade?: MotivoQualidade;
  motivoLeitura?: string;
}

export type Acao =
  | { tipo: 'PAREADO' }
  | { tipo: 'LINK_INVALIDO' }
  | { tipo: 'COMECAR' }
  | { tipo: 'CAMERA_OK' }
  | { tipo: 'CAMERA_NEGADA' }
  | { tipo: 'TENTAR_DE_NOVO' }
  | { tipo: 'FOTOGRAFAR' }
  | { tipo: 'NAO_TENHO' }
  | { tipo: 'FOTO_RUIM'; motivo: MotivoQualidade }
  | { tipo: 'TIRAR_OUTRA' }
  | { tipo: 'FOTO_BOA' }
  | { tipo: 'FOTOGRAFAR_VERSO' }
  | { tipo: 'LIDO' }
  | { tipo: 'NOVA_FOTO'; motivo: string }
  | { tipo: 'TEMPO_ESGOTADO' }
  | { tipo: 'PROXIMO' }
  | { tipo: 'CANCELAR' };

export function inicial(docs: DocumentoPedido[]): Estado {
  return { tela: 'conectando', docs, idx: 0, face: 'frente', situacao: {}, recusas: 0, fotosDoc: 0 };
}

export function docAtual(e: Estado): DocumentoPedido {
  return e.docs[e.idx];
}

/** Próximo documento ainda sem situação, depois do atual. */
export function proximoIdx(e: Estado, situacao = e.situacao): number | null {
  for (let i = e.idx + 1; i < e.docs.length; i++) if (!situacao[e.docs[i].id]) return i;
  return null;
}

function avancar(e: Estado, situacao: Record<string, SituacaoDoc>): Estado {
  const prox = proximoIdx(e, situacao);
  return prox === null
    ? { ...e, situacao, tela: 'fim' }
    : { ...e, situacao, idx: prox, face: 'frente', tela: 'documento', recusas: 0, fotosDoc: 0 };
}

export function reduzir(e: Estado, a: Acao): Estado {
  switch (a.tipo) {
    case 'PAREADO': return e.tela === 'conectando' ? { ...e, tela: 'abertura' } : e;
    case 'LINK_INVALIDO': return { ...e, tela: 'link-invalido' };
    case 'COMECAR': return { ...e, tela: 'permissao' };
    case 'CAMERA_OK': return { ...e, tela: 'documento', idx: 0, face: 'frente' };
    case 'CAMERA_NEGADA': return { ...e, tela: 'camera-negada' };
    case 'TENTAR_DE_NOVO': return { ...e, tela: 'permissao' };
    case 'FOTOGRAFAR': return { ...e, tela: 'camera', face: 'frente' };
    case 'NAO_TENHO': return avancar(e, { ...e.situacao, [docAtual(e).id]: 'nao-tenho' });
    case 'FOTO_RUIM':
      // Na 3ª recusa seguida, a última foto segue para o motor, que ainda pode pedir outra.
      return e.recusas + 1 >= TENTATIVAS_MAXIMAS
        ? reduzir({ ...e, recusas: 0 }, { tipo: 'FOTO_BOA' })
        : { ...e, tela: 'qualidade', motivoQualidade: a.motivo, recusas: e.recusas + 1, fotosDoc: e.fotosDoc + 1 };
    case 'TIRAR_OUTRA': return { ...e, tela: 'camera' };
    case 'FOTO_BOA': {
      const n = e.fotosDoc + 1;
      return docAtual(e).temVerso && e.face === 'frente' ? { ...e, tela: 'verso', recusas: 0, fotosDoc: n } : { ...e, tela: 'lendo', recusas: 0, fotosDoc: n };
    }
    case 'FOTOGRAFAR_VERSO': return { ...e, tela: 'camera', face: 'verso' };
    case 'LIDO': return e.tela === 'lendo' ? { ...e, tela: 'enviado', situacao: { ...e.situacao, [docAtual(e).id]: 'enviado' } } : e;
    case 'NOVA_FOTO': return e.tela === 'lendo' ? { ...e, tela: 'nova-foto', motivoLeitura: a.motivo, face: 'frente' } : e;
    case 'TEMPO_ESGOTADO': return e.tela === 'lendo' ? { ...e, tela: 'demorado', situacao: { ...e.situacao, [docAtual(e).id]: 'demorado' } } : e;
    case 'PROXIMO': return avancar(e, e.situacao);
    case 'CANCELAR': return { ...e, tela: 'documento', face: 'frente' };
  }
}
