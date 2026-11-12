import { describe, expect, it } from 'vitest';
import { strFromU8 } from 'fflate';
import { montarPacote } from './pacote';

const doc = {
  rotulo: 'RG, CIN ou CNH', tipo: 'cnh',
  arquivos: { frente: new Uint8Array([0xff, 0xd8, 1]), verso: new Uint8Array([0x25, 0x50, 0x44, 0x46]) },
  campos: { cpf: { valor: '644.836.782-99', origem: 'padrão', validado: true }, nome: { valor: 'NATALIA; RIBEIRO', origem: 'rótulo', validado: false } },
  decisoes: { cpf: 'confirmado' as const },
};

describe('pacote do cliente', () => {
  it('tem os arquivos originais com nomes neutros, sem nome nem CPF', () => {
    const p = montarPacote([doc]);
    expect(Object.keys(p).sort()).toEqual(['01-rg-cin-ou-cnh/frente.jpg', '01-rg-cin-ou-cnh/verso.pdf', 'LEIA-ME.txt', 'dados.csv', 'dados.json']);
    expect(Object.keys(p).join(' ')).not.toMatch(/644|NATALIA/);
  });

  it('dados trazem a situação de cada campo, inclusive os não revisados', () => {
    const p = montarPacote([doc]);
    const j = JSON.parse(strFromU8(p['dados.json']));
    expect(j.documentos[0].campos.cpf).toMatchObject({ situacao: 'confirmado', conferido_automaticamente: true });
    expect(j.documentos[0].campos.nome.situacao).toBe('nao_revisado');
    expect(strFromU8(p['dados.csv'])).toContain('"NATALIA; RIBEIRO"'); // separador escapado
  });
});
