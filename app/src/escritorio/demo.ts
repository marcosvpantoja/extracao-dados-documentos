// Modo de demonstração do escritório: ?demo=1 (lista), ?demo=revisao (revisão aberta) ou ?demo=conferencia (conferência do cliente).
// Dados fictícios, os mesmos dos documentos de exemplo do projeto.

import { CATALOGO } from '../compartilhado/protocolo';

export const DEMO = new URLSearchParams(window.location.search).get('demo');

const c = (valor: string, origem = 'rótulo', validado = false) => ({ valor, origem, validado });

export const ITENS_DEMO = [
  {
    doc: CATALOGO[0], situacao: 'lido' as const, tipo: 'cnh', detalhe: 'CNH', faces: { frente: '/demo/cnh.jpg' },
    campos: {
      nome: c('NATALIA APARECIDA BARBOSA RIBEIRO', 'mrz', true), cpf: c('644.836.782-99', 'padrão', true),
      data_nascimento: c('1966-10-30', 'mrz', true), filiacao_pai: c('DIEGO PAULO MOREIRA RIBEIRO', 'ia'),
      filiacao_mae: c('CARLA VITORIA PEREIRA RIBEIRO'), numero_registro: c('63723669838'), categoria: c('D'),
      validade: c('2029-03-28'),
    },
    decisoes: DEMO === 'revisao' ? { cpf: 'confirmado' as const, nome: 'confirmado' as const } : {},
  },
  {
    doc: CATALOGO[1], situacao: 'lido' as const, tipo: 'fatura', detalhe: 'Fatura', faces: { frente: '/demo/fatura.jpg' },
    campos: { cliente: c('VINICIUS ROBERTO VIEIRA SANTOS'), cnpj_emissora: c('08.236.013/0001-76', 'padrão', true),
      valor_total: c('417.28'), vencimento: c('2026-10-15') },
    decisoes: { cliente: 'confirmado' as const, cnpj_emissora: 'confirmado' as const, valor_total: 'confirmado' as const, vencimento: 'confirmado' as const },
  },
  {
    doc: CATALOGO[4], situacao: 'lido' as const, tipo: 'nfe', detalhe: 'NF-e', faces: { frente: '/demo/nfe.jpg' },
    campos: { chave_acesso: c('13260929989158000118550010004347171918294748', 'rótulo', true),
      emitente_cnpj: c('29.989.158/0001-18', 'padrão', true), valor_total: c('5223.60'), data_emissao: c('2026-09-17') },
    decisoes: {},
  },
];
