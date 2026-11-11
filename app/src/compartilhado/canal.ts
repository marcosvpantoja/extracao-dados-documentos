// Canal em tempo real (Supabase Broadcast). Só repassa mensagens; não grava nada.

import { createClient, type RealtimeChannel } from '@supabase/supabase-js';

const URL_SUPABASE = import.meta.env.VITE_SUPABASE_URL as string;
const CHAVE_PUBLICA = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string;

export async function abrirCanal(sessao: string): Promise<RealtimeChannel> {
  const cliente = createClient(URL_SUPABASE, CHAVE_PUBLICA, {
    auth: { persistSession: false, autoRefreshToken: false }, // nada em localStorage
    realtime: { params: { eventsPerSecond: 50 } },
  });
  const canal = cliente.channel(`sessao:${sessao}`, { config: { broadcast: { ack: true, self: false } } });
  return canal;
}

export function inscrever(canal: RealtimeChannel): Promise<void> {
  return new Promise((ok, falha) => {
    canal.subscribe((status) => {
      if (status === 'SUBSCRIBED') ok();
      if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') falha(new Error(status));
    });
  });
}

export async function enviar(canal: RealtimeChannel, evento: string, payload: object): Promise<void> {
  const r = await canal.send({ type: 'broadcast', event: evento, payload });
  if (r !== 'ok') throw new Error(`Falha ao enviar ${evento}: ${r}`);
}
