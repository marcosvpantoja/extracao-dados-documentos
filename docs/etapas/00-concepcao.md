# Etapa 0 — Concepção e escopo

**Data de início:** 10/11/2026
**Status:** 🟡 Em andamento

## Natureza do projeto

Projeto de **estudo**, sem cliente real. O objetivo é praticar, de ponta a ponta, as atribuições de Product Management (discovery, requisitos, priorização, métricas, decisões técnicas, riscos de IA, roadmap e comunicação) enquanto o sistema é construído. Personas e cenários são hipóteses explícitas, validadas com pesquisa pública e documentos de exemplo, não com dados de clientes.

## Problema

Documentos chegam em formatos heterogêneos (PDF digital, PDF escaneado, foto de celular) e os dados que importam precisam ser digitados manualmente em outro sistema. Isso é lento, sujeito a erro e não escala.

## Proposta

Um pipeline que transforma documento → dados estruturados:

```
Documento ──► Ingestão ──► Leitura (texto/OCR) ──► Classificação ──► Extração ──► Validação ──► JSON
                                                                                      │
                                                                                      └──► Revisão humana (baixa confiança)
```

## Perguntas em aberto

Respostas vão alimentar a Etapa 1.

- [ ] Quais tipos de documento entram no primeiro escopo? (ex.: notas fiscais, contratos, RG/CNH, comprovantes, boletos)
- [ ] Quais campos precisam ser extraídos de cada tipo?
- [ ] Qual o volume esperado (documentos/dia) e o tempo de resposta aceitável?
- [ ] Os documentos contêm dados pessoais sensíveis? (impacta LGPD, armazenamento e escolha de provedores)
- [ ] Para onde vão os dados extraídos? (planilha, banco, ERP, API de terceiros)
- [ ] Quem revisa os casos de baixa confiança?

## Critérios de sucesso (rascunho)

- Acurácia por campo medida sobre um conjunto de documentos reais rotulados.
- Taxa de documentos que passam sem revisão humana.
- Tempo médio de processamento por documento.

## Próximo passo

Responder às perguntas em aberto e montar um conjunto inicial de documentos de exemplo (anonimizados) para guiar as decisões de arquitetura.
