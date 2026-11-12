// Armazenamento temporário cifrado (ADR 0007) e auditoria (ADR 0009), no Supabase.
//
// - A CHAVE DO DIA é gerada no navegador, não pode ser exportada (Web Crypto) e fica guardada no
//   IndexedDB só para sobreviver a uma atualização da página (decisão de 11/11/2026). Às 18h ela é
//   destruída (camada 1). Nenhum CONTEÚDO fica no navegador: documentos e dados vão cifrados ao Supabase.
// - O Supabase apaga tudo às 18h (camada 2) e, de hora em hora, o que tiver mais de 24h (camada 3).
// - A auditoria registra só códigos: evento, perfil, estação, documento e tipo.

import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { deBase64Url, paraBase64Url } from '../compartilhado/cripto';

let cliente: SupabaseClient | null = null;
const supabase = (): SupabaseClient => (cliente ??= createClient(import.meta.env.VITE_SUPABASE_URL as string, import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string, {
  auth: { persistSession: false, autoRefreshToken: false }, // nada de sessão no navegador
}));

// ---------------------------------------------------------------- horário de Brasília

/** Hora atual em Brasília (UTC−3, sem horário de verão). */
export function agoraBrasilia(agora = new Date()): Date {
  return new Date(agora.getTime() - 3 * 3600_000);
}

/** O "dia" de armazenamento vai das 18h de um dia às 17h59 do seguinte; o identificador é a data do fim. */
export function periodoAtual(agora = new Date()): string {
  const b = agoraBrasilia(agora);
  if (b.getUTCHours() >= 18) b.setUTCDate(b.getUTCDate() + 1);
  return b.toISOString().slice(0, 10);
}

/** Milissegundos até a próxima remoção das 18h de Brasília. */
export function msAteRemocao(agora = new Date()): number {
  const b = agoraBrasilia(agora);
  const alvo = new Date(b);
  alvo.setUTCHours(18, 0, 0, 0);
  if (b >= alvo) alvo.setUTCDate(alvo.getUTCDate() + 1);
  return alvo.getTime() - b.getTime();
}

// ---------------------------------------------------------------- IndexedDB (só a chave e a estação)

function banco(): Promise<IDBDatabase> {
  return new Promise((ok, falha) => {
    const r = indexedDB.open('extracao-estudo', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('chaves');
    r.onsuccess = () => ok(r.result);
    r.onerror = () => falha(r.error);
  });
}

async function idb<T>(modo: IDBTransactionMode, f: (s: IDBObjectStore) => IDBRequest): Promise<T> {
  const db = await banco();
  return new Promise((ok, falha) => {
    const req = f(db.transaction('chaves', modo).objectStore('chaves'));
    req.onsuccess = () => ok(req.result as T);
    req.onerror = () => falha(req.error);
  });
}

/** Código aleatório deste navegador. Não identifica pessoa nem máquina. */
export async function estacao(): Promise<string> {
  let id = await idb<string | undefined>('readonly', (s) => s.get('estacao'));
  if (!id) {
    id = crypto.randomUUID();
    await idb('readwrite', (s) => s.put(id, 'estacao'));
  }
  return id;
}

/** Chave do período atual. Chaves de períodos anteriores são destruídas aqui também. */
export async function chaveDoDia(): Promise<CryptoKey> {
  const periodo = periodoAtual();
  const salva = await idb<{ periodo: string; chave: CryptoKey } | undefined>('readonly', (s) => s.get('chave-do-dia'));
  if (salva && salva.periodo === periodo) return salva.chave;
  const chave = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
  await idb('readwrite', (s) => s.put({ periodo, chave }, 'chave-do-dia'));
  return chave;
}

/** Camada 1 da remoção: sem a chave, qualquer cópia no Supabase (ou em backup) fica ilegível. */
export async function destruirChaveDoDia(): Promise<void> {
  await idb('readwrite', (s) => s.delete('chave-do-dia'));
}

// ---------------------------------------------------------------- documentos cifrados

export async function salvar(id: string, conteudo: object): Promise<void> {
  const [chave, est] = await Promise.all([chaveDoDia(), estacao()]);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const cifrado = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, chave, new TextEncoder().encode(JSON.stringify(conteudo))));
  const { error } = await supabase().from('cadastros_cifrados').upsert({
    id, estacao: est, iv: paraBase64Url(iv), conteudo: paraBase64Url(cifrado), atualizado_em: new Date().toISOString(),
  });
  if (error) throw error;
}

/** Documentos deste navegador que ainda podem ser decifrados com a chave do dia. */
export async function carregar<T>(): Promise<{ id: string; conteudo: T }[]> {
  const [chave, est] = await Promise.all([chaveDoDia(), estacao()]);
  const { data, error } = await supabase().from('cadastros_cifrados').select('id, iv, conteudo, criado_em').eq('estacao', est).order('criado_em');
  if (error) throw error;
  const saida: { id: string; conteudo: T }[] = [];
  for (const linha of data ?? []) {
    try {
      const aberto = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: deBase64Url(linha.iv) }, chave, deBase64Url(linha.conteudo));
      saida.push({ id: linha.id, conteudo: JSON.parse(new TextDecoder().decode(aberto)) as T });
    } catch {
      // cifrado com a chave de outro período: ilegível por definição, e será removido pelo servidor
    }
  }
  return saida;
}

export async function apagar(ids: string[]): Promise<void> {
  if (!ids.length) return;
  const { error } = await supabase().from('cadastros_cifrados').delete().in('id', ids);
  if (error) throw error;
}

// ---------------------------------------------------------------- auditoria (ADR 0009)

export type EventoAuditoria = 'documento_aberto' | 'pacote_baixado' | 'documento_excluido';
export type Perfil = 'assistente' | 'advogada';
const TIPOS = new Set(['cnh', 'cin', 'rg', 'nfe', 'boleto', 'fatura', 'nao_reconhecido']);

export async function auditar(evento: EventoAuditoria, perfil: Perfil, documento?: string, tipo?: string): Promise<void> {
  const est = await estacao();
  await supabase().from('auditoria').insert({ evento, perfil, estacao: est, documento: documento ?? null, tipo: tipo && TIPOS.has(tipo) ? tipo : null });
}

// ---------------------------------------------------------------- conversões para guardar arquivos

export const paraTexto = (b: Uint8Array) => paraBase64Url(b);
export const deTexto = (t: string) => deBase64Url(t);
