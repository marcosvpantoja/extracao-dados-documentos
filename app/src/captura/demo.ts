// Modo de demonstração (para apresentações e imagens das telas): ?demo=<tela>
// Mostra cada tela já preenchida com dados de exemplo, sem celular pareado nem câmera.
// Nada é enviado: o canal não é aberto.

import { CATALOGO } from '../compartilhado/protocolo';
import { inicial, type Estado, type Tela } from './fluxo';

export const DEMO = new URLSearchParams(window.location.search).get('demo') as Tela | null;

export const DEMO_LINK = {
  sessao: 'demo', chave: '', escritorio: 'Escritório Exemplo',
  documentos: [CATALOGO[0], CATALOGO[1], CATALOGO[2]],
};

export function estadoDemo(tela: Tela): Estado {
  const e = inicial(DEMO_LINK.documentos);
  const base: Estado = { ...e, tela, idx: 1 };
  switch (tela) {
    case 'camera': return { ...base, idx: 0, face: 'frente' };
    case 'verso': return { ...base, idx: 0 };
    case 'qualidade': return { ...base, motivoQualidade: 'escura', recusas: 1 };
    case 'nova-foto': return { ...base, idx: 0, motivoLeitura: 'Não conseguimos ler o CPF do documento' };
    case 'enviado': return { ...base, situacao: { identidade: 'enviado', comprovante: 'enviado' } };
    case 'demorado': return { ...base, situacao: { identidade: 'enviado', comprovante: 'demorado' } };
    case 'fim': return { ...base, idx: 2, situacao: { identidade: 'enviado', comprovante: 'nao-tenho', fatura: 'enviado' } };
    default: return base;
  }
}
