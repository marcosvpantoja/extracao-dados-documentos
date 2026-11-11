// Verificação de qualidade da foto no próprio celular (RF-05), antes do envio.
// Os limites são valores iniciais e serão calibrados com as fotos dos documentos fictícios impressos.

export type MotivoQualidade = 'escura' | 'tremida' | 'reflexo';

export interface Imagem {
  data: Uint8ClampedArray; // RGBA
  width: number;
  height: number;
}

export interface ResultadoQualidade {
  ok: boolean;
  motivo?: MotivoQualidade;
  brilho: number; // 0 a 255
  nitidez: number; // variância do laplaciano
  reflexo: number; // fração de pixels quase brancos
}

export const LIMITES = {
  brilhoMinimo: 70,
  nitidezMinima: 40,
  reflexoMaximo: 0.08,
};

export const MENSAGENS: Record<MotivoQualidade, { titulo: string; dica: string }> = {
  escura: { titulo: 'A foto ficou escura', dica: 'Tente perto de uma janela ou com a luz acesa.' },
  tremida: { titulo: 'A foto ficou tremida', dica: 'Apoie os cotovelos e segure o celular firme.' },
  reflexo: { titulo: 'A foto tem reflexo de luz', dica: 'Incline um pouco o documento para o brilho sumir.' },
};

function tonsDeCinza(img: Imagem): Float32Array {
  const g = new Float32Array(img.width * img.height);
  for (let i = 0, p = 0; i < g.length; i++, p += 4) {
    g[i] = 0.299 * img.data[p] + 0.587 * img.data[p + 1] + 0.114 * img.data[p + 2];
  }
  return g;
}

export function analisar(img: Imagem): ResultadoQualidade {
  const { width: w, height: h } = img;
  const g = tonsDeCinza(img);

  let soma = 0;
  let claros = 0;
  for (const v of g) {
    soma += v;
    if (v >= 250) claros++;
  }
  const brilho = soma / g.length;
  const reflexo = claros / g.length;

  // Variância do laplaciano: imagens tremidas têm poucas bordas nítidas.
  let n = 0;
  let media = 0;
  let m2 = 0;
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const i = y * w + x;
      const lap = g[i - w] + g[i + w] + g[i - 1] + g[i + 1] - 4 * g[i];
      n++;
      const d = lap - media;
      media += d / n;
      m2 += d * (lap - media);
    }
  }
  const nitidez = n > 1 ? m2 / (n - 1) : 0;

  let motivo: MotivoQualidade | undefined;
  if (brilho < LIMITES.brilhoMinimo) motivo = 'escura';
  else if (reflexo > LIMITES.reflexoMaximo) motivo = 'reflexo';
  else if (nitidez < LIMITES.nitidezMinima) motivo = 'tremida';

  return { ok: !motivo, motivo, brilho, nitidez, reflexo };
}

/** Dica ao vivo na câmera (tela 4), a partir de um quadro reduzido do vídeo. */
export function dicaAoVivo(r: ResultadoQualidade): string {
  if (r.brilho < LIMITES.brilhoMinimo) return '💡 Procure mais luz';
  if (r.reflexo > LIMITES.reflexoMaximo) return '↘ Incline para tirar o reflexo';
  if (r.nitidez < LIMITES.nitidezMinima) return '✋ Segure firme';
  return '✓ Pronto, pode fotografar';
}
