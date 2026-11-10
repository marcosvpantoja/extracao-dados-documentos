# Etapa 0 — Concepção e discovery

**Data de início:** 10/11/2026
**Status:** 🟡 Em andamento
**Atributo de PM praticado:** Discovery e definição do problema

## Natureza do projeto

Projeto de **estudo**, sem cliente real. O objetivo é praticar, de ponta a ponta, as atribuições de Product Management (discovery, requisitos, priorização, métricas, decisões técnicas, riscos de IA, roadmap e comunicação) enquanto o sistema é construído. Personas e cenários são **hipóteses explícitas**, validadas com pesquisa pública e documentos de exemplo, não com dados de clientes.

> Convenção: tudo marcado com 🧪 é hipótese ainda não validada. Quando for validada (ou descartada), a marca muda para ✅ ou ❌ com a fonte da evidência.

## Definição do produto ✅

> **O usuário envia um documento (nota fiscal, CNH ou RG) sem informar o tipo. O sistema identifica sozinho o tipo, extrai os dados e mostra os campos na tela.**

Três requisitos centrais, definidos pelo dono do produto em 10/11/2026:

1. **Tipos suportados no MVP:** Nota Fiscal (NF-e / DANFE), CNH e RG.
2. **Classificação automática:** o usuário não escolhe o tipo; o sistema detecta.
3. **Saída em tela:** os dados extraídos aparecem organizados para o usuário ler e conferir.

## Cenário de trabalho 🧪

Um **escritório de contabilidade de pequeno porte**. No dia a dia ele recebe dois grupos de documentos misturados, pelos mesmos canais (e-mail, WhatsApp, pasta compartilhada):

- **Documentos fiscais:** notas fiscais de compra e venda dos clientes, que precisam ser lançadas no fechamento.
- **Documentos pessoais:** RG e CNH de sócios e responsáveis, usados em cadastros, abertura de empresa e alterações contratuais.

Hoje alguém abre cada arquivo, descobre o que é e digita os dados à mão.

## Persona 🧪

**Ana, assistente contábil**
- Recebe arquivos de tipos diferentes, misturados, sem padrão de nome.
- Precisa primeiro **entender o que é cada documento** e depois **transcrever os campos**.
- **Dor principal:** tempo gasto em triagem e digitação, e retrabalho causado por erro de digitação.
- **O que ela precisa:** soltar o arquivo, ver os dados prontos e confiar neles sem conferir campo por campo.

## Problema em uma frase 🧪

> Escritórios que lidam com documentos fiscais e pessoais misturados perdem tempo identificando cada arquivo e digitando seus dados à mão, num processo lento e propenso a erro.

## Fluxo do usuário

```
1. Envia o arquivo (PDF ou foto)
2. Sistema detecta o tipo  ──►  "Nota Fiscal" | "CNH" | "RG" | "Não reconhecido"
3. Sistema extrai os campos daquele tipo
4. Tela mostra: tipo detectado + campos extraídos + indicação de confiança
```

## Campos-alvo (proposta inicial, a validar na Etapa 1)

| Nota Fiscal (NF-e) | CNH | RG |
|---|---|---|
| Número e série | Nome | Nome |
| Chave de acesso | CPF | Número do RG |
| Data de emissão | Número de registro | Órgão emissor / UF |
| Emitente (razão social, CNPJ) | Data de nascimento | Data de expedição |
| Destinatário (nome, CPF/CNPJ) | Categoria | Data de nascimento |
| Valor total | Validade | Filiação |
| Itens (descrição, qtd., valor) | Primeira habilitação | CPF (quando presente) |

## Mapa de hipóteses

| # | Hipótese | Risco se estiver errada | Como validar |
|---|---|---|---|
| H1 🧪 | Triagem + digitação de documentos consome tempo significativo em escritórios pequenos | Problema pequeno demais para justificar o produto | Pesquisa pública (fóruns de contadores, conteúdos do setor) |
| H2 🧪 | É possível distinguir NF, CNH e RG automaticamente com alta acurácia | Usuário teria que escolher o tipo, quebrando o requisito central | Teste com conjunto de exemplos na etapa de classificação |
| H3 🧪 | Fotos de celular (RG/CNH) são lidas com qualidade suficiente | Extração falha justamente nos documentos pessoais | Testar com fotos em condições variadas (luz, ângulo, desfoque) |
| H4 🧪 | O usuário confia no resultado se a tela indicar a confiança por campo | Se precisar conferir tudo, o ganho de tempo some | Protótipo da tela de resultado |
| H5 🧪 | Existem lacunas nas soluções atuais para escritório pequeno | Mercado já resolvido | Benchmark de concorrentes |

## Riscos e restrições

- **LGPD:** RG e CNH contêm dados pessoais. Proposta para o MVP: processar sem armazenar o documento nem os dados extraídos (decisão a ser registrada em ADR).
- **Repositório público:** nenhum documento real entra no repositório. Testes usam apenas documentos fictícios ou modelos públicos.
- **RG tem vários modelos:** o RG antigo varia por estado e há a nova Carteira de Identidade Nacional (CIN). Escopo exato a definir na Etapa 1.
- **CNH física x CNH digital (PDF):** layouts diferentes; ambos podem chegar.

## Fora de escopo (MVP)

- Seleção manual do tipo de documento (contraria o requisito central).
- Outros documentos (boletos, contratos, comprovantes), que ficam para depois do MVP.
- Integração com sistemas contábeis e exportação automática.
- Armazenamento de histórico de documentos.
- Documentos manuscritos.

## Critérios de sucesso (rascunho)

- **Acurácia da classificação:** % de documentos com tipo detectado corretamente.
- **Acurácia por campo:** % de campos extraídos corretamente, por tipo de documento.
- **Tempo até o resultado:** do envio até os dados aparecerem na tela.

As metas numéricas serão definidas na etapa de métricas, depois de medir uma linha de base.

## ✍️ Sua tarefa como PM nesta etapa

1. **Revisar a persona e o problema:** o cenário do escritório contábil serve, ou prefere outro contexto (ex.: cadastro de clientes em financeira, imobiliária)?
2. **Validar os campos-alvo:** cortar ou incluir campos na tabela acima.
3. **Decidir o escopo de RG:** só a nova CIN, só o RG antigo, ou ambos?

As respostas fecham a Etapa 0 e abrem a Etapa 1 (documentos e campos-alvo).
