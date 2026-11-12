// Protocolo entre a página de captura (celular) e a aplicação do escritório (computador).
// Tudo passa por um canal Broadcast do Supabase chamado `sessao:<id>`, e o conteúdo das
// fotos viaja sempre cifrado, dividido em pedaços de 128 KB (Etapa 8, prova de conceito 1).

import { deBase64Url, paraBase64Url } from './cripto';


export const TAMANHO_PEDACO = 128 * 1024;
export const ESPERA_LEITURA_MS = 30_000; // RF-31
export const VALIDADE_PAREAMENTO_MS = 5 * 60_000; // RF-03

export type Grupo = 'identificacao' | 'comprovante' | 'prova';

export interface DocumentoPedido {
  id: string;
  rotulo: string; // "Conta de luz ou água"
  ajuda: string; // "Serve para comprovar seu endereço."
  temVerso: boolean;
  grupo: Grupo;
}

/** Documentos que a assistente pode incluir na lista (RF-33). */
export const CATALOGO: DocumentoPedido[] = [
  { id: 'identidade', rotulo: 'RG, CIN ou CNH', ajuda: 'Documento com foto. Fotografe frente e verso.', temVerso: true, grupo: 'identificacao' },
  { id: 'comprovante', rotulo: 'Conta de luz ou água', ajuda: 'Serve para comprovar seu endereço.', temVerso: false, grupo: 'comprovante' },
  { id: 'fatura', rotulo: 'Fatura que você contesta', ajuda: 'A fatura com a cobrança que você não reconhece.', temVerso: false, grupo: 'prova' },
  { id: 'boleto', rotulo: 'Boleto cobrado', ajuda: 'O boleto que chegou para você pagar.', temVerso: false, grupo: 'prova' },
  { id: 'nota', rotulo: 'Nota fiscal da compra', ajuda: 'A nota fiscal do produto ou serviço.', temVerso: false, grupo: 'prova' },
];

export interface DadosDoLink {
  sessao: string;
  chave: string; // base64url, só no fragmento
  escritorio: string;
  documentos: DocumentoPedido[];
}

/** Monta o link de captura. Chave, escritório e lista ficam no fragmento (#), fora do alcance do servidor.
 *  A lista vai só com os identificadores do catálogo, para o QR code ficar curto e fácil de ler. */
export function montarLink(base: string, d: DadosDoLink): string {
  const frag = new URLSearchParams({ k: d.chave, e: d.escritorio, d: d.documentos.map((x) => x.id).join('.') });
  return `${base}?s=${encodeURIComponent(d.sessao)}#${frag.toString()}`;
}

export function lerLink(href: string): DadosDoLink | null {
  try {
    const url = new URL(href);
    const sessao = url.searchParams.get('s');
    const frag = new URLSearchParams(url.hash.slice(1));
    const chave = frag.get('k');
    const escritorio = frag.get('e');
    const lista = frag.get('d');
    if (!sessao || !chave || !escritorio || !lista) return null;
    const documentos = lista.split('.').map((id) => CATALOGO.find((c) => c.id === id));
    if (documentos.length === 0 || documentos.some((x) => !x)) return null;
    return { sessao, chave, escritorio, documentos: documentos as DocumentoPedido[] };
  } catch {
    return null;
  }
}

// ---------- Mensagens do canal ----------

export type Face = 'frente' | 'verso';

export interface MsgPareamento { celular: string }
export interface MsgPareado { celular: string; aceito: boolean }
export interface MsgPedaco { envio: string; doc: string; face: Face; i: number; n: number; iv: string; dados: string; fotos?: number }
export interface MsgPendente { doc: string }
export interface MsgResultado { envio: string; doc: string; status: 'lido' | 'nova-foto'; motivo?: string }
export interface MsgConcluido { pendentes: string[] }

export const EVENTOS = {
  pareamento: 'pareamento',
  pareado: 'pareado',
  pedaco: 'pedaco',
  pendente: 'pendente',
  resultado: 'resultado',
  concluido: 'concluido',
} as const;

/** Divide o conteúdo cifrado em mensagens de até 128 KB (antes do base64). */
export function dividirEmPedacos(envio: string, doc: string, face: Face, iv: Uint8Array, dados: Uint8Array, fotos?: number): MsgPedaco[] {
  const n = Math.max(1, Math.ceil(dados.length / TAMANHO_PEDACO));
  const ivTexto = paraBase64Url(iv);
  return Array.from({ length: n }, (_, i) => ({
    envio, doc, face, i, n, iv: ivTexto, fotos,
    dados: paraBase64Url(dados.subarray(i * TAMANHO_PEDACO, (i + 1) * TAMANHO_PEDACO)),
  }));
}

/** Remonta os pedaços de cada envio, em qualquer ordem de chegada. */
export class Remontador {
  private envios = new Map<string, { n: number; partes: Map<number, Uint8Array>; iv: string; doc: string; face: Face }>();

  adicionar(m: MsgPedaco): { doc: string; face: Face; envio: string; iv: Uint8Array; dados: Uint8Array } | null {
    let e = this.envios.get(m.envio);
    if (!e) {
      e = { n: m.n, partes: new Map(), iv: m.iv, doc: m.doc, face: m.face };
      this.envios.set(m.envio, e);
    }
    e.partes.set(m.i, deBase64Url(m.dados));
    if (e.partes.size < e.n) return null;
    const total = [...e.partes.values()].reduce((s, p) => s + p.length, 0);
    const dados = new Uint8Array(total);
    let pos = 0;
    for (let i = 0; i < e.n; i++) {
      const p = e.partes.get(i)!;
      dados.set(p, pos);
      pos += p.length;
    }
    this.envios.delete(m.envio);
    return { doc: e.doc, face: e.face, envio: m.envio, iv: deBase64Url(e.iv), dados };
  }
}
