// Servidor MCP do estudo de caso: expõe o motor de extração como ferramentas para assistentes de IA
// (Claude Code, Claude Desktop e outros clientes MCP).
//
// Privacidade: a ferramenta de leitura aceita SÓ arquivos de data/exemplos (documentos fictícios).
// Documentos reais nunca devem passar por um assistente de IA (regra da Etapa 1).
//
// Requisitos: motor rodando em http://127.0.0.1:8787 (scripts/iniciar-motor.sh). O motor usa o
// Apple Vision e só funciona no macOS.

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { execFile } from 'node:child_process';
import { readFile, readdir } from 'node:fs/promises';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { z } from 'zod';

const RAIZ = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const EXEMPLOS = join(RAIZ, 'data', 'exemplos');
const MOTOR = 'http://127.0.0.1:8787';
const PYTHON = join(RAIZ, '.venv', 'bin', 'python');

const texto = (t) => ({ content: [{ type: 'text', text: t }] });

function rodar(script, args = []) {
  return new Promise((ok) => {
    execFile(PYTHON, [join(RAIZ, 'scripts', script), ...args], { cwd: RAIZ, timeout: 15 * 60_000, maxBuffer: 10 * 1024 * 1024 },
      (erro, saida, erros) => ok(erro && !saida ? `Falhou: ${erros || erro.message}` : saida));
  });
}

async function online(url) {
  try { return (await fetch(url, { signal: AbortSignal.timeout(1500) })).ok; } catch { return false; }
}

const servidor = new McpServer({ name: 'extracao-documentos', version: '1.0.0' });

servidor.registerTool('estado', {
  title: 'Estado do motor',
  description: 'Verifica se o motor de extração e a IA local (Ollama) estão rodando neste computador.',
  inputSchema: {},
}, async () => {
  const [motor, ia] = await Promise.all([online(`${MOTOR}/escritorio.html`), online('http://127.0.0.1:11434/api/tags')]);
  return texto([
    `Motor de extração (${MOTOR}): ${motor ? 'rodando' : 'parado. Rode scripts/iniciar-motor.sh'}`,
    `IA local (Ollama): ${ia ? 'rodando' : 'parada. O motor funciona só com regras'}`,
    `Sistema: ${process.platform === 'darwin' ? 'macOS (OCR disponível)' : 'não é macOS: o OCR (Apple Vision) não funciona aqui'}`,
  ].join('\n'));
});

servidor.registerTool('listar_documentos_ficticios', {
  title: 'Listar documentos fictícios',
  description: 'Lista os documentos fictícios disponíveis para teste (data/exemplos).',
  inputSchema: {},
}, async () => {
  const pastas = await readdir(EXEMPLOS, { withFileTypes: true });
  const linhas = [];
  for (const p of pastas.filter((d) => d.isDirectory())) {
    const arquivos = (await readdir(join(EXEMPLOS, p.name))).filter((f) => f.endsWith('.pdf'));
    linhas.push(`${p.name}: ${arquivos.map((f) => `${p.name}/${f}`).join(', ')}`);
  }
  return texto(linhas.join('\n'));
});

servidor.registerTool('ler_documento_ficticio', {
  title: 'Ler documento fictício',
  description: 'Envia um documento fictício ao motor e devolve o tipo identificado e os campos extraídos, '
    + 'com origem (rótulo, padrão, MRZ, IA) e se cada campo foi conferido por dígito verificador. '
    + 'Aceita só arquivos de data/exemplos, por exemplo "cnh/cnh-ficticio-01.pdf".',
  inputSchema: { arquivo: z.string().describe('Caminho dentro de data/exemplos, ex.: "nfe/nfe-ficticio-01.pdf"') },
}, async ({ arquivo }) => {
  const caminho = resolve(EXEMPLOS, arquivo);
  if (!caminho.startsWith(EXEMPLOS + sep)) return texto('Recusado: só documentos fictícios de data/exemplos podem ser lidos por esta ferramenta.');
  let bytes;
  try { bytes = await readFile(caminho); } catch { return texto(`Arquivo não encontrado: ${relative(RAIZ, caminho)}`); }
  const corpo = new FormData();
  corpo.append('frente', new Blob([bytes]), arquivo.split('/').pop());
  try {
    const r = await fetch(`${MOTOR}/processar?doc=teste`, { method: 'POST', body: corpo, signal: AbortSignal.timeout(60_000) });
    const j = await r.json();
    delete j.previa;
    return texto(JSON.stringify(j, null, 2));
  } catch {
    return texto('O motor não respondeu. Rode scripts/iniciar-motor.sh e tente de novo.');
  }
});

servidor.registerTool('avaliar_motor', {
  title: 'Avaliar o motor',
  description: 'Roda a avaliação do motor nos 32 documentos fictícios e devolve classificação, '
    + 'campos certos e cobertura por tipo. Com ia=true usa a IA local (mais lento).',
  inputSchema: {
    ia: z.boolean().default(false).describe('Usar a IA local para completar campos'),
    variantes: z.boolean().default(false).describe('Avaliar só os 14 documentos de layout novo'),
  },
}, async ({ ia, variantes }) => texto(await rodar('avaliar.py', [...(ia ? ['--ia'] : []), ...(variantes ? ['--variantes'] : [])])));

servidor.registerTool('resultados_chave', {
  title: 'Resultados-chave',
  description: 'Calcula os resultados-chave (KR1 a KR4), a métrica de proteção e a North Star a partir do '
    + 'registro local de medição, que guarda só eventos, contagens e tempos (nenhum dado pessoal).',
  inputSchema: {},
}, async () => texto(await rodar('relatorio.py')));

await servidor.connect(new StdioServerTransport());
