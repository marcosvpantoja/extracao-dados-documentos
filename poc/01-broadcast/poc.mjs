// Prova de conceito 1: uma "foto" cifrada passa inteira pelo Supabase Realtime Broadcast?
//
// Simula dois aparelhos (celular e computador) com dois clientes Supabase separados.
// O conteúdo é aleatório: nenhum documento, real ou fictício, é usado.
//
// Uso: node poc.mjs   (lê SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY de ../../.env.local)

import { createClient } from '@supabase/supabase-js';
import { readFileSync } from 'node:fs';
import { webcrypto as crypto, randomBytes, createHash } from 'node:crypto';

const env = Object.fromEntries(
  readFileSync(new URL('../../.env.local', import.meta.url), 'utf8')
    .split('\n').filter(Boolean).map((l) => l.split(/=(.*)/s).slice(0, 2)),
);
const novoCliente = () =>
  createClient(env.SUPABASE_URL, env.SUPABASE_PUBLISHABLE_KEY, {
    realtime: { params: { eventsPerSecond: 50 } },
  });

const KB = 1024;
const TAMANHOS_FOTO = [300 * KB, 1024 * KB, 2048 * KB]; // fotos comprimidas típicas
const TAMANHOS_PEDACO = [64 * KB, 128 * KB, 180 * KB]; // antes do base64 (+33%)
const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

async function inscrever(canal) {
  await new Promise((ok, falha) => {
    canal.subscribe((status) => {
      if (status === 'SUBSCRIBED') ok();
      if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') falha(new Error(status));
    });
  });
}

async function cenario(tamanhoFoto, tamanhoPedaco) {
  const sessao = crypto.randomUUID();
  const celular = novoCliente();
  const computador = novoCliente();
  const nome = `poc:${sessao}`;

  // Chave AES-256-GCM: no produto, ela vai no fragmento (#) da URL do QR code.
  const chave = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const foto = randomBytes(tamanhoFoto);
  const cifrado = Buffer.from(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, chave, foto));

  // Computador: recebe os pedaços e remonta.
  const recebidos = new Map();
  let total = null;
  let fim;
  const completo = new Promise((r) => (fim = r));
  const canalPC = computador.channel(nome, { config: { broadcast: { self: false } } });
  canalPC.on('broadcast', { event: 'pedaco' }, ({ payload }) => {
    recebidos.set(payload.i, Buffer.from(payload.dados, 'base64'));
    total = payload.n;
    if (recebidos.size === total) fim();
  });
  await inscrever(canalPC);

  // Celular: divide o conteúdo cifrado em pedaços e envia, com confirmação (ack).
  const canalCel = celular.channel(nome, { config: { broadcast: { ack: true, self: false } } });
  await inscrever(canalCel);

  const n = Math.ceil(cifrado.length / tamanhoPedaco);
  const inicio = performance.now();
  const falhas = [];
  for (let i = 0; i < n; i++) {
    const dados = cifrado.subarray(i * tamanhoPedaco, (i + 1) * tamanhoPedaco).toString('base64');
    const r = await canalCel.send({ type: 'broadcast', event: 'pedaco', payload: { i, n, dados } });
    if (r !== 'ok') falhas.push(`${i}:${r}`);
  }
  const resultado = await Promise.race([completo.then(() => 'ok'), esperar(20000).then(() => 'tempo esgotado')]);
  const ms = Math.round(performance.now() - inicio);

  let integro = false;
  if (resultado === 'ok') {
    const remontado = Buffer.concat([...Array(n).keys()].map((i) => recebidos.get(i)));
    const aberto = Buffer.from(await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, chave, remontado));
    integro = sha256(aberto) === sha256(foto);
  }

  await celular.removeAllChannels();
  await computador.removeAllChannels();
  return {
    foto_kb: tamanhoFoto / KB,
    pedaco_kb: tamanhoPedaco / KB,
    mensagem_kb: Math.round((Math.ceil((tamanhoPedaco * 4) / 3) + 60) / KB),
    pedacos: n,
    recebidos: recebidos.size,
    envios_recusados: falhas.length,
    integro,
    ms: resultado === 'ok' ? ms : resultado,
  };
}

async function mensagemUnica(tamanho) {
  // Controle: uma mensagem única, sem dividir em pedaços. O envio é aceito e ela chega ao outro lado?
  const nome = `poc:${crypto.randomUUID()}`;
  const rx = novoCliente();
  const tx = novoCliente();
  let chegou = false;
  const canalRx = rx.channel(nome, { config: { broadcast: { self: false } } });
  canalRx.on('broadcast', { event: 'x' }, () => (chegou = true));
  await inscrever(canalRx);
  const canalTx = tx.channel(nome, { config: { broadcast: { ack: true, self: false } } });
  await inscrever(canalTx);
  const r = await canalTx.send({ type: 'broadcast', event: 'x', payload: { dados: randomBytes(tamanho).toString('base64') } });
  await esperar(5000);
  await rx.removeAllChannels();
  await tx.removeAllChannels();
  return { mensagem_unica_kb: Math.round((tamanho * 4) / 3 / KB), envio: r, chegou };
}

const so = process.argv[2];
if (so !== 'controle') {
  for (const foto of TAMANHOS_FOTO) {
    for (const pedaco of TAMANHOS_PEDACO) console.log(JSON.stringify(await cenario(foto, pedaco)));
  }
}
for (const kb of [150, 190, 250, 400, 1000]) console.log(JSON.stringify(await mensagemUnica(kb * KB)));
process.exit(0);
