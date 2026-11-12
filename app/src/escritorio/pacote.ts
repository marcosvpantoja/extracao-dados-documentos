// Pacote do cliente (HU-15, RF-26): arquivos originais + dados, num .zip gerado no navegador.
// Nada passa por servidor. Os nomes dos arquivos são neutros: nunca levam nome nem CPF.

import { strToU8, zipSync } from 'fflate';
import type { Face } from '../compartilhado/protocolo';
import type { CampoLido, Decisao } from './Revisao';

export interface DocumentoDoPacote {
  rotulo: string;
  tipo: string;
  arquivos: Partial<Record<Face, Uint8Array>>;
  campos: Record<string, CampoLido>;
  decisoes: Record<string, Decisao>;
}

const pasta = (i: number, rotulo: string) =>
  `${String(i + 1).padStart(2, '0')}-${rotulo.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`;

const extensao = (b: Uint8Array) => (b[0] === 0x25 && b[1] === 0x50 && b[2] === 0x44 && b[3] === 0x46 ? 'pdf' : 'jpg');

const situacao = (d?: Decisao) => (d === 'confirmado' ? 'confirmado' : d === 'recusado' ? 'recusado' : 'nao_revisado');

const csv = (v: string) => (/[;"\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v);

export function montarPacote(docs: DocumentoDoPacote[], agora = new Date()): Record<string, Uint8Array> {
  const arquivos: Record<string, Uint8Array> = {};
  const dados = docs.map((d, i) => {
    const p = pasta(i, d.rotulo);
    for (const [face, bytes] of Object.entries(d.arquivos)) if (bytes) arquivos[`${p}/${face}.${extensao(bytes)}`] = bytes;
    return {
      pasta: p, documento: d.rotulo, tipo: d.tipo,
      campos: Object.fromEntries(Object.entries(d.campos).map(([k, c]) => [k, {
        valor: c.valor, situacao: situacao(d.decisoes[k]), conferido_automaticamente: c.validado, origem: c.origem,
      }])),
    };
  });
  arquivos['dados.json'] = strToU8(JSON.stringify({ gerado_em: agora.toISOString(), documentos: dados }, null, 2));
  const linhas = ['documento;tipo;campo;valor;situacao;conferido_automaticamente;origem'];
  for (const d of dados) for (const [k, c] of Object.entries(d.campos))
    linhas.push([d.documento, d.tipo, k, c.valor, c.situacao, c.conferido_automaticamente ? 'sim' : 'nao', c.origem].map(csv).join(';'));
  arquivos['dados.csv'] = strToU8('﻿' + linhas.join('\n')); // BOM: o Excel abre os acentos certos
  arquivos['LEIA-ME.txt'] = strToU8([
    'Pacote do cliente gerado pelo cadastro por documentos (estudo de caso).',
    `Gerado em: ${agora.toLocaleString('pt-BR')}`,
    '',
    'Conteúdo:',
    '- uma pasta por documento, com os arquivos originais (foto ou PDF);',
    '- dados.json e dados.csv: todos os campos lidos, com a situação de cada um',
    '  (confirmado, recusado ou nao_revisado) e se foi conferido por dígito verificador.',
    '',
    'Este pacote saiu do sistema e passa a ser responsabilidade do escritório, como controlador',
    'dos dados (LGPD). Guarde-o no ambiente do escritório e apague cópias desnecessárias.',
  ].join('\n'));
  return arquivos;
}

export function baixarPacote(docs: DocumentoDoPacote[]): string {
  const agora = new Date();
  const zip = zipSync(montarPacote(docs, agora), { level: 0 }); // fotos e PDFs já são comprimidos
  const nome = `cadastro-${agora.toISOString().slice(0, 16).replace(/[-:T]/g, '').replace(/^(\d{8})(\d{4})$/, '$1-$2')}.zip`;
  const url = URL.createObjectURL(new Blob([zip], { type: 'application/zip' }));
  const a = Object.assign(document.createElement('a'), { href: url, download: nome });
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
  return nome;
}
