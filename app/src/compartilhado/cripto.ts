// Criptografia ponta a ponta entre o celular e o computador (ADR 0001).
// A chave AES-256-GCM é gerada no computador e viaja só no fragmento (#) do link,
// que o navegador nunca envia a servidor nenhum.

export function paraBase64Url(bytes: Uint8Array): string {
  let bin = '';
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export function deBase64Url(texto: string): Uint8Array {
  const b64 = texto.replace(/-/g, '+').replace(/_/g, '/');
  const bin = atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4));
  return Uint8Array.from(bin, (c) => c.charCodeAt(0));
}

export async function gerarChave(): Promise<CryptoKey> {
  return crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);
}

export async function exportarChave(chave: CryptoKey): Promise<string> {
  return paraBase64Url(new Uint8Array(await crypto.subtle.exportKey('raw', chave)));
}

export async function importarChave(texto: string): Promise<CryptoKey> {
  const bytes = deBase64Url(texto);
  if (bytes.length !== 32) throw new Error('Chave inválida');
  return crypto.subtle.importKey('raw', bytes, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt']);
}

export interface Cifrado {
  iv: Uint8Array;
  dados: Uint8Array;
}

export async function cifrar(chave: CryptoKey, conteudo: Uint8Array): Promise<Cifrado> {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const dados = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, chave, conteudo));
  return { iv, dados };
}

export async function decifrar(chave: CryptoKey, { iv, dados }: Cifrado): Promise<Uint8Array> {
  return new Uint8Array(await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, chave, dados));
}
