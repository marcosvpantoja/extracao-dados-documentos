# Etapa 5: Métricas

**Status:** 🟡 Em andamento · 10/11/2026
**Papéis:** PM
**Entradas:** [Etapa 4](04-estrategia.md), [PRD, métricas de sucesso](../requisitos.md#9-métricas-de-sucesso)

As métricas desta etapa valem para o **produto em produção**, com escritórios usando o sistema todos os dias. O estudo de caso não tem uso real, então cada métrica de produção ganha uma **métrica substituta**, medida nas sessões com testers ([Etapa 13](../../README.md#roteiro)). É a mesma separação dos ADRs [0007](../decisoes/0007-retencao-temporaria-e-purga-diaria.md) e [0008](../decisoes/0008-armazenamento-em-producao.md).

---

## 1. North Star

> **Clientes cadastrados por semana sem nenhuma edição**
> Clientes cujos campos, em todos os documentos, foram confirmados na revisão sem nenhuma correção.

| Critério | Como a métrica atende |
|---|---|
| Reflete valor para o usuário | Conta clientes que saíram prontos sem a Juliana digitar nada |
| Cobre os dois atributos | **Preciso:** o sistema acertou todos os campos. **Ágil:** a revisão foi só confirmação |
| Unidade certa | O cliente, e não o documento: um cadastro com um campo corrigido ainda exigiu trabalho manual |
| Mostra uso | Por ser uma quantidade, sobe quando o produto é mais usado |
| O time influencia | Melhorar OCR, extração e captura aumenta diretamente o número |

**Limite conhecido:** a métrica é exigente. Um único campo corrigido em qualquer documento tira o cliente da conta. No início o número pode ser baixo, mas ele só sobe se o produto melhorar de verdade.

### Métrica de apoio

> **% de documentos confirmados sem edição**

A North Star mistura uso e qualidade. A métrica de apoio isola a qualidade: mostra se o sistema está acertando mais, independente do volume de clientes, e aponta em qual tipo de documento está o problema.

### Como a métrica foi escolhida

| Versão | Proposta | Por que mudou |
|---|---|---|
| 1 | Documentos importados com sucesso | "Sucesso" lido como arquivo aceito: mediria volume, sem dizer se os dados estavam certos |
| 2 | Documentos importados sem nenhuma edição | Mede o acerto de primeira, e zero edição cobre ágil e preciso ao mesmo tempo; mas a unidade era o documento e deixava de fora a captura pelo celular |
| 3 | **Clientes cadastrados sem nenhuma edição**, com % de documentos sem edição como apoio | Unidade passa a ser o cliente; a porcentagem separa qualidade de volume |

Alternativas descartadas:
- **Tempo mediano de cadastro:** mede só o ágil e dá para "melhorar" conferindo menos.
- **Clientes cadastrados em até X minutos e sem erro:** exigiria um X definido sem dados.

---

## 2. Métrica de proteção

> **% de documentos editados depois da confirmação, por qualquer perfil**

A North Star pode subir por um motivo errado: se a revisão vira um clique automático em "confirmar", as edições somem e o número melhora enquanto os erros passam adiante. A métrica de proteção não pode piorar enquanto a North Star sobe. Se piorar, a subida é falsa.

**Por que ela funciona:** vem de fora da revisão. Quem detecta o erro é outra pessoa (a advogada ou qualquer outro perfil), depois da confirmação. Um descuido de quem revisa engana a North Star, mas não engana essa métrica.

**Como o sistema fica sabendo:** a correção costuma acontecer no software jurídico, fora do produto. Por isso a tela do cadastro tem um botão **"devolver por dado errado"**: quem encontra o erro marca o campo no produto, mesmo que corrija em outro lugar (RF-30).

**Limite conhecido:** a métrica depende de a pessoa lembrar de marcar. Erros corrigidos sem marcação ficam invisíveis, então o número real tende a ser maior que o medido.

| Alternativa | Por que não foi escolhida |
|---|---|
| Documentos que precisaram de edição na revisão | Anda junto com a North Star: se a revisão vira clique automático, as duas melhoram ao mesmo tempo |
| Edição feita dentro do produto | Obriga o jurídico a trocar de ferramenta |
| Integração com o software jurídico | Fora do escopo do MVP; depende de cada fornecedor |
| Confirmações rápidas demais como alerta | Indício, não prova; não incluída nesta versão |
