import { describe, expect, it } from 'vitest';
import { analisar, dicaAoVivo, type Imagem } from './qualidade';

function imagem(w: number, h: number, pixel: (x: number, y: number) => number): Imagem {
  const data = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const v = pixel(x, y), p = (y * w + x) * 4;
    data[p] = data[p + 1] = data[p + 2] = v; data[p + 3] = 255;
  }
  return { data, width: w, height: h };
}

// "Documento" nítido: fundo claro com linhas de texto escuras e bordas duras.
const nitido = (x: number, y: number) => (y % 8 < 2 && x % 40 < 30 ? 30 : 200);

describe('qualidade da foto', () => {
  it('documento bem iluminado e nítido passa', () => {
    const r = analisar(imagem(200, 120, nitido));
    expect(r.ok).toBe(true);
    expect(dicaAoVivo(r)).toContain('Pronto');
  });

  it('foto escura é recusada', () => {
    const r = analisar(imagem(200, 120, (x, y) => nitido(x, y) * 0.2));
    expect(r).toMatchObject({ ok: false, motivo: 'escura' });
  });

  it('foto sem bordas (tremida) é recusada', () => {
    const r = analisar(imagem(200, 120, (x) => 150 + Math.round(x / 40)));
    expect(r).toMatchObject({ ok: false, motivo: 'tremida' });
  });

  it('documento branco e bem iluminado (ou na tela de um computador) não é recusado por reflexo', () => {
    const r = analisar(imagem(200, 120, (x, y) => (y % 8 < 2 && x % 40 < 30 ? 30 : 255)));
    expect(r.ok).toBe(true);
    expect(r.reflexo).toBeGreaterThan(0.5);
  });
});
