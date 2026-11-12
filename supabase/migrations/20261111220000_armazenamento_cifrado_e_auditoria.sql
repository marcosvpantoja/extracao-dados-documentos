-- Estudo de caso: armazenamento temporário cifrado (ADR 0007) e trilha de auditoria (ADR 0009).
-- O servidor só guarda conteúdo cifrado: a chave do dia fica no navegador do escritório.

-- 1. Cadastros cifrados -------------------------------------------------------------------------
-- Cada linha é um documento do cadastro, inteiro (dados, decisões e arquivos), cifrado com AES-GCM
-- no navegador. Em aberto, só metadados técnicos: id, estação (código aleatório do navegador) e horário.
-- Decisão de 11/11/2026: os arquivos vão dentro da linha, e não no Storage, para a remoção diária
-- ser feita inteiramente em SQL (o Storage não permite apagar arquivos por SQL).
create table if not exists public.cadastros_cifrados (
  id uuid primary key,
  estacao uuid not null,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  iv text not null,
  conteudo text not null  -- base64 do conteúdo cifrado
);
create index if not exists cadastros_cifrados_estacao on public.cadastros_cifrados (estacao);

alter table public.cadastros_cifrados enable row level security;
-- Sem login no estudo: a chave pública pode ler e gravar, mas tudo é cifrado e ilegível sem a chave do dia.
create policy "estudo: inserir" on public.cadastros_cifrados for insert to anon with check (true);
create policy "estudo: ler" on public.cadastros_cifrados for select to anon using (true);
create policy "estudo: atualizar" on public.cadastros_cifrados for update to anon using (true) with check (true);
create policy "estudo: apagar" on public.cadastros_cifrados for delete to anon using (true);

-- 2. Auditoria (ADR 0009) ---------------------------------------------------------------------
-- Só inclusão. Nenhuma coluna de texto livre: códigos, horários e listas fechadas.
create table if not exists public.auditoria (
  id uuid primary key default gen_random_uuid(),
  quando timestamptz not null default now(),
  evento text not null check (evento in ('documento_aberto', 'pacote_baixado', 'documento_excluido')),
  perfil text not null check (perfil in ('assistente', 'advogada')),
  estacao uuid not null,
  documento uuid,
  tipo text check (tipo in ('cnh', 'cin', 'rg', 'nfe', 'boleto', 'fatura', 'nao_reconhecido'))
);
alter table public.auditoria enable row level security;
create policy "auditoria: só inclusão" on public.auditoria for insert to anon with check (true);
create policy "auditoria: leitura" on public.auditoria for select to anon using (true);
-- sem políticas de update/delete: ninguém altera nem apaga um registro

-- 3. Remoção às 18h e limite de 24h (ADR 0007, camadas 2 e 3) -----------------------------------
create extension if not exists pg_cron;

create table if not exists public.registro_remocao (
  id bigserial primary key,
  quando timestamptz not null default now(),
  camada text not null,
  removidos integer not null
);
alter table public.registro_remocao enable row level security;
create policy "remoção: leitura" on public.registro_remocao for select to anon using (true);

create or replace function public.remover_cadastros(camada text, so_antigos boolean)
returns void language plpgsql security definer set search_path = public as $$
declare n integer;
begin
  if so_antigos then
    delete from public.cadastros_cifrados where criado_em < now() - interval '24 hours';
  else
    delete from public.cadastros_cifrados;
  end if;
  get diagnostics n = row_count;
  insert into public.registro_remocao (camada, removidos) values (camada, n);
end $$;

-- 18h de Brasília = 21h UTC
select cron.schedule('remocao-18h', '0 21 * * *', $$select public.remover_cadastros('18h', false)$$);
-- de hora em hora, qualquer item com mais de 24h
select cron.schedule('limite-24h', '0 * * * *', $$select public.remover_cadastros('24h', true)$$);
