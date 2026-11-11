# 0008 — Armazenamento dos documentos em produção

**Data:** 10/11/2026
**Status:** Aceita como desenho de referência · **não implementada no estudo de caso**, que segue o [ADR 0007](0007-retencao-temporaria-e-purga-diaria.md)

## Contexto

O [ADR 0007](0007-retencao-temporaria-e-purga-diaria.md) define uma regra do **estudo de caso**: dados e fotos ficam cifrados na nuvem durante o dia e são removidos às 18h. Ela existe para proteger os documentos das pessoas que testam o sistema, e não descreve o produto.

Um escritório em operação precisa guardar os documentos dos clientes por todo o tempo do processo. Várias assistentes acessam o mesmo cadastro, a advogada anexa os arquivos à petição e o cliente pode pedir a exclusão dos dados a qualquer momento (LGPD). Para o produto funcionar de ponta a ponta no estudo, esse armazenamento não precisa ser construído, mas o desenho precisa estar decidido. Sem isso, o estudo deixaria sem resposta uma pergunta óbvia: "e em produção?".

A pergunta central é **quem consegue ler os documentos guardados**.

## Decisão

**Criptografia em repouso controlada pela aplicação, reforçada com chave por escritório, controle de acesso, trilha de auditoria e retenção definida pelo escritório.** O servidor da aplicação consegue ler os documentos, mas só sob regras explícitas e com registro de cada acesso.

| Camada | Como | Protege contra |
|---|---|---|
| **Transporte** | TLS em todas as conexões; captura pelo celular continua cifrada ponta a ponta ([ADR 0001](0001-transporte-cross-device.md)) | Interceptação na rede |
| **Repouso, pelo provedor** | Banco e Storage cifrados pelo provedor (AES-256) | Roubo de disco ou de mídia de backup |
| **Repouso, pela aplicação** | Criptografia de envelope: cada arquivo tem uma chave própria, protegida por uma **chave mestra do escritório** guardada num serviço de gerenciamento de chaves (KMS), com rotação periódica | Vazamento do banco: o conteúdo copiado continua ilegível sem acesso ao KMS |
| **Isolamento entre escritórios** | Row Level Security por escritório e chaves mestras separadas | Um escritório ver dados de outro, por erro ou ataque |
| **Controle de acesso** | Perfis (assistente, advogada, administrador), autenticação com segundo fator, sessões curtas | Acesso indevido dentro do escritório ou por senha vazada |
| **Trilha de auditoria** | Registro de quem abriu, baixou, alterou ou excluiu cada documento, sem gravar o conteúdo | Uso indevido não detectado; exigência de prestação de contas da LGPD |
| **Retenção** | Prazo definido por escritório, com exclusão automática ao fim; exclusão e exportação a pedido do titular | Guarda além do necessário |
| **Backups** | Cifrados, com prazo próprio, e exclusão de chaves aplicada também a eles | Dado excluído que sobrevive em backup |

## Alternativas consideradas

- **Criptografia ponta a ponta com a chave só com o escritório (servidor cego)** — segurança máxima: nem o fornecedor lê os documentos. Mas se o escritório perder a chave, perde todos os documentos; compartilhar entre várias estações e usuários é complexo; busca e processamento no servidor ficam impossíveis. Recusada pelo custo operacional num escritório de massa, onde várias pessoas acessam o mesmo cadastro.
- **Só a criptografia padrão do provedor** — simples, mas um vazamento do banco ou um acesso indevido ao servidor expõe tudo, e não existe registro de quem acessou o quê. Recusada por ser insuficiente para documentos de identificação.
- **Manter a remoção diária do ADR 0007 em produção** — incompatível com o uso real: o escritório precisa dos documentos durante todo o processo. Recusada.

## Consequências

- **A segurança passa a depender da confiança no operador.** Quem administra o KMS e o servidor pode, em tese, ler os documentos. A trilha de auditoria e a separação de funções reduzem esse risco, mas não o eliminam. É a troca aceita em favor da operação.
- **A promessa ao cliente muda.** Ela deixa de ser "nada sobrevive às 18h" e passa a ser "seus documentos ficam cifrados, só pessoas autorizadas do escritório acessam, cada acesso é registrado e tudo é apagado no prazo definido".
- **Novos componentes:** KMS, perfis de acesso, trilha de auditoria e rotinas de retenção e de exclusão a pedido. Nenhum deles é construído no estudo de caso.
- **O que o estudo aproveita:** o fluxo de captura cifrado ponta a ponta, a revisão humana e o motor de extração não mudam. Só a camada de armazenamento é trocada.
