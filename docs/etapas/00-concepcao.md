# Etapa 0 — Concepção e discovery

**Data de início:** 10/11/2026
**Status:** 🟡 Em andamento
**Atributo de PM praticado:** Discovery e definição do problema

## Natureza do projeto

Projeto de **estudo**, sem cliente real. O objetivo é praticar, de ponta a ponta, as atribuições de Product Management (discovery, requisitos, priorização, métricas, decisões técnicas, riscos de IA, roadmap e comunicação) enquanto o sistema é construído. Personas e cenários são **hipóteses explícitas**, validadas com pesquisa pública e documentos de exemplo, não com dados de clientes.

> Convenção: tudo marcado com 🧪 é hipótese ainda não validada. Quando for validada (ou descartada), a marca muda para ✅ ou ❌ com a fonte da evidência.

## Definição do produto ✅

> **O usuário envia um documento (NF-e, boleto, CNH ou RG) sem informar o tipo. O sistema identifica sozinho o tipo, extrai os dados e mostra os campos na tela.**

Três requisitos centrais, definidos pelo dono do produto em 10/11/2026:

1. **Tipos suportados no MVP:** Nota Fiscal (NF-e / DANFE), boleto bancário e documentos pessoais (CNH e RG).
2. **Classificação automática:** o usuário não escolhe o tipo; o sistema detecta.
3. **Saída em tela:** os dados extraídos aparecem organizados para o usuário ler e conferir.
4. **Captura pelo celular (fluxo cross-device):** o computador mostra um QR code; o usuário escaneia com o celular, fotografa o documento pela câmera e os dados voltam para a tela do computador.
5. **Extensível:** a arquitetura deve permitir incluir novos tipos de documento sem reescrever o sistema.

Decisões complementares (10/11/2026):
- **RG:** suportar **ambos**, o RG antigo (modelos estaduais) e a nova Carteira de Identidade Nacional (CIN).

## Cenário de trabalho 🧪

Um **escritório de contabilidade de pequeno porte**. No dia a dia ele recebe dois grupos de documentos misturados, pelos mesmos canais (e-mail, WhatsApp, pasta compartilhada):

- **Documentos fiscais e financeiros:** notas fiscais de compra e venda e boletos a pagar dos clientes, que precisam ser lançados no fechamento.
- **Documentos pessoais:** RG e CNH de sócios e responsáveis, usados em cadastros, abertura de empresa e alterações contratuais.

Hoje alguém abre cada arquivo, descobre o que é e digita os dados à mão.

## Persona 🧪

**Ana, assistente contábil**
- Recebe arquivos de tipos diferentes, misturados, sem padrão de nome.
- Precisa primeiro **entender o que é cada documento** e depois **transcrever os campos**.
- **Dor principal:** tempo gasto em triagem e digitação, e retrabalho causado por erro de digitação.
- **O que ela precisa:** soltar o arquivo, ver os dados prontos e confiar neles sem conferir campo por campo.

## Problema em uma frase 🧪

> Escritórios que lidam com notas fiscais, boletos e documentos pessoais misturados perdem tempo identificando cada arquivo e digitando seus dados à mão, num processo lento e propenso a erro.

## Fluxo do usuário (cross-device)

```
COMPUTADOR                                   CELULAR
1. Abre o sistema e clica em "Novo documento"
2. Tela mostra um QR code (sessão única) ──► 3. Escaneia o QR com a câmera
                                             4. Abre página web de captura (sem instalar app)
                                             5. Fotografa o documento
                                             6. Envia a imagem
7. Computador recebe em tempo real  ◄────────┘
8. Sistema detecta o tipo  ──►  "NF-e" | "Boleto" | "CNH" | "RG" | "Não reconhecido"
9. Sistema extrai os campos daquele tipo
10. Tela do computador mostra: tipo detectado + campos extraídos + confiança
```

O nome técnico desse padrão é **fluxo cross-device** (ou *mobile handoff*): o mesmo mecanismo de pareamento por QR code do WhatsApp Web, aplicado à captura de documentos, como fazem plataformas de verificação de identidade (KYC).

Upload direto de PDF no computador continua possível (ex.: NF-e e boleto recebidos por e-mail), mas o foco do MVP é a captura pelo celular.

## Campos-alvo (proposta inicial, a validar na Etapa 1)

| Nota Fiscal (NF-e) | Boleto | CNH | RG |
|---|---|---|---|
| Número e série | Linha digitável | Nome | Nome |
| Chave de acesso | Código de barras | CPF | Número do RG |
| Data de emissão | Banco emissor | Número de registro | Órgão emissor / UF |
| Emitente (razão social, CNPJ) | Beneficiário (nome, CNPJ/CPF) | Data de nascimento | Data de expedição |
| Destinatário (nome, CPF/CNPJ) | Pagador (nome, CPF/CNPJ) | Categoria | Data de nascimento |
| Valor total | Valor | Validade | Filiação |
| Itens (descrição, qtd., valor) | Data de vencimento | Primeira habilitação | CPF (quando presente) |

## Mapa de hipóteses

| # | Hipótese | Risco se estiver errada | Como validar |
|---|---|---|---|
| H1 🧪 | Triagem + digitação de documentos consome tempo significativo em escritórios pequenos | Problema pequeno demais para justificar o produto | Pesquisa pública (fóruns de contadores, conteúdos do setor) |
| H2 🧪 | É possível distinguir NF-e, boleto, CNH e RG automaticamente com alta acurácia | Usuário teria que escolher o tipo, quebrando o requisito central | Teste com conjunto de exemplos na etapa de classificação |
| H3 🧪 | Fotos de celular (RG/CNH) são lidas com qualidade suficiente | Extração falha justamente nos documentos pessoais | Testar com fotos em condições variadas (luz, ângulo, desfoque) |
| H6 🧪 | O usuário prefere fotografar pelo celular a usar scanner ou upload | Esforço no fluxo cross-device não se paga | Teste de usabilidade com o protótipo |
| H4 🧪 | O usuário confia no resultado se a tela indicar a confiança por campo | Se precisar conferir tudo, o ganho de tempo some | Protótipo da tela de resultado |
| H5 🧪 | Existem lacunas nas soluções atuais para escritório pequeno | Mercado já resolvido | Benchmark de concorrentes |

## Riscos e restrições

- **LGPD:** RG e CNH contêm dados pessoais. Proposta para o MVP: processar sem armazenar o documento nem os dados extraídos (decisão a ser registrada em ADR).
- **Repositório público:** nenhum documento real entra no repositório. Testes usam apenas documentos fictícios ou modelos públicos.
- **RG tem vários modelos:** o RG antigo varia por estado e há a nova CIN. Decidido suportar ambos, o que aumenta o esforço de classificação e extração; será o tipo mais trabalhoso do MVP.
- **Segurança do pareamento:** o QR code deve gerar uma sessão única, de curta duração e de uso único, para que ninguém envie documentos para a sessão de outra pessoa.
- **Qualidade da foto:** a página de captura no celular deve orientar enquadramento, luz e foco, porque a qualidade da imagem limita a acurácia.
- **CNH física x CNH digital (PDF):** layouts diferentes; ambos podem chegar.
- **Boleto tem validação matemática:** a linha digitável tem dígitos verificadores, o que permite checar automaticamente se a extração está correta. Pode servir de referência de confiança.

## Fora de escopo (MVP)

- Seleção manual do tipo de documento (contraria o requisito central).
- Outros documentos (contratos, comprovantes de pagamento, NFS-e), que ficam para depois do MVP.
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

As respostas fecham a Etapa 0 e abrem a Etapa 1 (documentos e campos-alvo).
