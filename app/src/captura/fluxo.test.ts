import { describe, expect, it } from 'vitest';
import { CATALOGO } from '../compartilhado/protocolo';
import { inicial, reduzir, type Acao, type Estado } from './fluxo';

const docs = [CATALOGO[0], CATALOGO[1], CATALOGO[2]]; // identidade (com verso), comprovante, fatura
const rodar = (acoes: Acao[], e: Estado = inicial(docs)) => acoes.reduce(reduzir, e);
const ate3 = [{ tipo: 'PAREADO' }, { tipo: 'COMECAR' }, { tipo: 'CAMERA_OK' }] as Acao[];

describe('fluxo da captura (espelho do fluxograma das telas)', () => {
  it('abre na tela 1 só depois de parear com o escritório', () => {
    expect(rodar([]).tela).toBe('conectando');
    expect(rodar([{ tipo: 'PAREADO' }]).tela).toBe('abertura');
  });

  it('câmera negada leva à tela 2b, e "tentar de novo" volta à 2', () => {
    const e = rodar([{ tipo: 'PAREADO' }, { tipo: 'COMECAR' }, { tipo: 'CAMERA_NEGADA' }]);
    expect(e.tela).toBe('camera-negada');
    expect(reduzir(e, { tipo: 'TENTAR_DE_NOVO' }).tela).toBe('permissao');
  });

  it('documento com verso pede o verso antes da leitura', () => {
    const e = rodar([...ate3, { tipo: 'FOTOGRAFAR' }, { tipo: 'FOTO_BOA' }]);
    expect(e.tela).toBe('verso');
    const v = rodar([{ tipo: 'FOTOGRAFAR_VERSO' }, { tipo: 'FOTO_BOA' }], e);
    expect(v.face).toBe('verso');
    expect(v.tela).toBe('lendo');
  });

  it('foto ruim só permite tirar outra (tela 5 → 4)', () => {
    const e = rodar([...ate3, { tipo: 'FOTOGRAFAR' }, { tipo: 'FOTO_RUIM', motivo: 'escura' }]);
    expect(e).toMatchObject({ tela: 'qualidade', motivoQualidade: 'escura' });
    expect(reduzir(e, { tipo: 'TIRAR_OUTRA' }).tela).toBe('camera');
  });

  it('na 3ª foto recusada seguida, a última segue para o motor', () => {
    let e = rodar([...ate3, { tipo: 'FOTOGRAFAR' }, { tipo: 'FOTO_RUIM', motivo: 'escura' }, { tipo: 'TIRAR_OUTRA' }, { tipo: 'FOTO_RUIM', motivo: 'escura' }]);
    expect(e).toMatchObject({ tela: 'qualidade', recusas: 2 });
    e = rodar([{ tipo: 'TIRAR_OUTRA' }, { tipo: 'FOTO_RUIM', motivo: 'tremida' }], e);
    expect(e).toMatchObject({ tela: 'verso', recusas: 0, fotosDoc: 3 }); // identidade tem verso; 3 fotos contadas
  });

  it('leitura que falha pede nova foto desde a frente (7b)', () => {
    const e = rodar([...ate3, { tipo: 'FOTOGRAFAR' }, { tipo: 'FOTO_BOA' }, { tipo: 'FOTOGRAFAR_VERSO' }, { tipo: 'FOTO_BOA' },
      { tipo: 'NOVA_FOTO', motivo: 'reflexo no número' }]);
    expect(e).toMatchObject({ tela: 'nova-foto', face: 'frente', motivoLeitura: 'reflexo no número' });
  });

  it('"não tenho agora" pula o documento e ele aparece como pendente no fim', () => {
    let e = rodar([...ate3, { tipo: 'FOTOGRAFAR' }, { tipo: 'FOTO_BOA' }, { tipo: 'FOTOGRAFAR_VERSO' }, { tipo: 'FOTO_BOA' }, { tipo: 'LIDO' }, { tipo: 'PROXIMO' }]);
    expect(e).toMatchObject({ tela: 'documento', idx: 1 });
    e = rodar([{ tipo: 'NAO_TENHO' }], e);
    expect(e).toMatchObject({ tela: 'documento', idx: 2 });
    e = rodar([{ tipo: 'FOTOGRAFAR' }, { tipo: 'FOTO_BOA' }, { tipo: 'TEMPO_ESGOTADO' }], e);
    expect(e.tela).toBe('demorado');
    e = reduzir(e, { tipo: 'PROXIMO' });
    expect(e.tela).toBe('fim');
    expect(e.situacao).toEqual({ identidade: 'enviado', comprovante: 'nao-tenho', fatura: 'demorado' });
  });

  it('resultado atrasado, depois do tempo esgotado, é ignorado', () => {
    const e = rodar([...ate3, { tipo: 'FOTOGRAFAR' }, { tipo: 'FOTO_BOA' }, { tipo: 'FOTOGRAFAR_VERSO' }, { tipo: 'FOTO_BOA' }, { tipo: 'TEMPO_ESGOTADO' }]);
    expect(reduzir(e, { tipo: 'LIDO' })).toBe(e);
  });
});
