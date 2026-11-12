import { describe, expect, it } from 'vitest';
import { cifrar, decifrar, exportarChave, gerarChave, importarChave } from './cripto';
import { CATALOGO, Remontador, TAMANHO_PEDACO, dividirEmPedacos, lerLink, montarLink } from './protocolo';

describe('link de captura', () => {
  it('ida e volta preserva sessão, chave, escritório e lista', async () => {
    const chave = await exportarChave(await gerarChave());
    const dados = { sessao: 'abc-123', chave, escritorio: 'Escritório Exemplo', documentos: CATALOGO.slice(0, 3) };
    const link = montarLink('https://captura.exemplo/captura.html', dados);
    expect(lerLink(link)).toEqual(dados);
  });

  it('a chave e a lista ficam só no fragmento, fora do que vai ao servidor', async () => {
    const chave = await exportarChave(await gerarChave());
    const link = new URL(montarLink('https://captura.exemplo/captura.html', { sessao: 's1', chave, escritorio: 'E', documentos: CATALOGO.slice(0, 1) }));
    expect(link.search).toBe('?s=s1');
    expect(link.search).not.toContain(chave);
    expect(link.hash).toContain(chave);
  });

  it('link incompleto ou adulterado é recusado', () => {
    expect(lerLink('https://captura.exemplo/captura.html?s=1')).toBeNull();
    expect(lerLink('https://captura.exemplo/captura.html?s=1#k=a&e=b&d=lixo')).toBeNull();
    expect(lerLink('não é url')).toBeNull();
  });
});

describe('cifra e pedaços', () => {
  it('foto de 1 MB atravessa cifrada, em pedaços embaralhados, e volta idêntica', async () => {
    const chave = await gerarChave();
    const grande = new Uint8Array(1024 * 1024); // 1 MB aleatório, em blocos de 64 KB (limite do gerador)
    for (let i = 0; i < grande.length; i += 65536) crypto.getRandomValues(grande.subarray(i, i + 65536));

    const { iv, dados } = await cifrar(chave, grande);
    const pedacos = dividirEmPedacos('e1', 'identidade', 'frente', iv, dados);
    expect(pedacos.length).toBe(Math.ceil(dados.length / TAMANHO_PEDACO));

    const r = new Remontador();
    let saida = null;
    for (const p of [...pedacos].reverse()) saida = r.adicionar(p) ?? saida;
    expect(saida).not.toBeNull();
    const aberto = await decifrar(chave, { iv: saida!.iv, dados: saida!.dados });
    expect(aberto).toEqual(grande);
    expect(saida!.doc).toBe('identidade');
    expect(saida!.face).toBe('frente');
  }, 30_000); // cifrar 1 MB leva ~1,4 s no Mac e mais de 5 s na máquina gratuita da integração contínua

  it('chave errada não decifra', async () => {
    const certa = await gerarChave();
    const errada = await importarChave(await exportarChave(await gerarChave()));
    const c = await cifrar(certa, new Uint8Array([1, 2, 3]));
    await expect(decifrar(errada, c)).rejects.toBeTruthy();
  });
});
