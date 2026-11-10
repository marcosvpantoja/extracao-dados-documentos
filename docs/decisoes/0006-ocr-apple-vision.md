# 0006 — OCR: Apple Vision como implementação inicial, atrás de uma interface trocável

**Data:** 10/11/2026
**Status:** Aceita

## Contexto

O motor local ([ADR 0002](0002-motor-de-leitura-e-extracao.md)) precisa de um OCR que leia bem fotos de documentos (luz irregular, reflexo, inclinação) e rode sem enviar nada para fora do computador. O hardware de referência é um Mac com Apple M4 e 16 GB de RAM.

## Decisão

Usar o **Apple Vision** (OCR nativo do macOS) como primeira implementação, acessado por uma **interface de OCR** própria do sistema. O restante do pipeline depende só dessa interface: texto reconhecido, posição de cada trecho na imagem e confiança.

## Alternativas consideradas

| Opção | Prós | Contras |
|---|---|---|
| **Apple Vision** | Alta qualidade em fotos; roda no aparelho; sem custo; sem instalação de modelos | Só funciona em macOS (e iOS) |
| PaddleOCR | Portátil (Windows, Linux); bom em documentos | Instalação e dependências pesadas; mais lento sem GPU |
| Tesseract | Portátil, leve, maduro | Fraco em fotos de celular e fundos texturizados (RG) |
| Modelo de visão local (via Ollama) | Lê e estrutura em um passo | Lento e pesado para 16 GB de RAM; difícil explicar erros |

## Consequências

- O motor local roda apenas em Mac. Aceitável para o estudo de caso, em que o Mac é o hardware de referência.
- Levar o produto para Windows ou servidor Linux exige uma segunda implementação da interface de OCR (provavelmente PaddleOCR), sem alterar classificação, extração ou validação.
- A comparação de acurácia entre OCRs vira um teste possível no futuro, rodando o mesmo conjunto de desenvolvimento nas duas implementações.
