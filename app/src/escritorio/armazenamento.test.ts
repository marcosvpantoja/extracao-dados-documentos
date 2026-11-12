import { describe, expect, it } from 'vitest';
import { msAteRemocao, periodoAtual } from './armazenamento';

describe('horário da remoção (18h de Brasília = 21h UTC)', () => {
  it('antes das 18h, o período é o próprio dia', () => {
    expect(periodoAtual(new Date('2026-11-12T20:59:00Z'))).toBe('2026-11-12'); // 17h59 em Brasília
  });

  it('a partir das 18h, começa o período do dia seguinte (a chave antiga deixa de valer)', () => {
    expect(periodoAtual(new Date('2026-11-12T21:00:00Z'))).toBe('2026-11-13'); // 18h00 em Brasília
  });

  it('calcula o tempo até a remoção para o aviso das 17h', () => {
    expect(msAteRemocao(new Date('2026-11-12T20:00:00Z'))).toBe(60 * 60_000); // 17h → falta 1 hora
    expect(msAteRemocao(new Date('2026-11-12T21:00:00Z'))).toBe(24 * 60 * 60_000); // 18h → próxima amanhã
  });
});
