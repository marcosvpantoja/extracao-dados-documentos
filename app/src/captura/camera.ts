// Câmera dentro da página (decisão de UX da Etapa 9). Nada é salvo na galeria nem no navegador:
// a foto existe só na memória até ser cifrada e enviada.

import { analisar, type ResultadoQualidade } from './qualidade';

export type ErroCamera = 'negada' | 'indisponivel';

export async function abrirCamera(video: HTMLVideoElement): Promise<MediaStream> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' }, width: { ideal: 1920 }, height: { ideal: 1080 } },
      audio: false,
    });
    video.srcObject = stream;
    await video.play();
    return stream;
  } catch (e) {
    const nome = (e as DOMException)?.name;
    throw (nome === 'NotAllowedError' || nome === 'SecurityError' ? 'negada' : 'indisponivel') as ErroCamera;
  }
}

export function fecharCamera(stream: MediaStream | null, video?: HTMLVideoElement | null) {
  stream?.getTracks().forEach((t) => t.stop());
  if (video) video.srcObject = null;
}

function desenhar(video: HTMLVideoElement, ladoMaior: number): HTMLCanvasElement {
  const escala = Math.min(1, ladoMaior / Math.max(video.videoWidth, video.videoHeight));
  const c = document.createElement('canvas');
  c.width = Math.round(video.videoWidth * escala);
  c.height = Math.round(video.videoHeight * escala);
  c.getContext('2d')!.drawImage(video, 0, 0, c.width, c.height);
  return c;
}

/** Quadro pequeno para a dica ao vivo. */
export function avaliarQuadro(video: HTMLVideoElement): ResultadoQualidade | null {
  if (!video.videoWidth) return null;
  const c = desenhar(video, 320);
  return analisar(c.getContext('2d')!.getImageData(0, 0, c.width, c.height));
}

export interface Foto {
  bytes: Uint8Array; // JPEG
  previa: string; // URL temporária para a miniatura; revogar depois do uso
  qualidade: ResultadoQualidade;
}

export async function fotografar(video: HTMLVideoElement): Promise<Foto> {
  const grande = desenhar(video, 1600);
  const pequeno = desenhar(video, 320);
  const qualidade = analisar(pequeno.getContext('2d')!.getImageData(0, 0, pequeno.width, pequeno.height));
  const blob: Blob = await new Promise((ok) => grande.toBlob((b) => ok(b!), 'image/jpeg', 0.85));
  return { bytes: new Uint8Array(await blob.arrayBuffer()), previa: URL.createObjectURL(blob), qualidade };
}
