---
name: corrigir-minuta-tjes
description: Corrige uma minuta (sentença, decisão ou voto) conforme a jurisprudência do TJES, consultando sempre acórdãos de segundo grau (Câmaras Cíveis/Criminais e Tribunal Pleno). Aponta divergências com o entendimento do TJES, confere as citações da minuta, sugere precedentes e devolve a minuta revisada com as alterações marcadas. Use quando o usuário pedir "corrija conforme TJES", "alinhe à jurisprudência do TJES", "confira a minuta com o TJES", "revise com base no Tribunal", ou enviar uma minuta pedindo adequação ao entendimento do TJES.
---

# Correção de minutas conforme a jurisprudência do TJES (2º grau)

Objetivo: revisar a minuta do usuário à luz do entendimento **atual** do Tribunal de
Justiça do Espírito Santo, usando **somente acórdãos de segundo grau** como parâmetro.

## Fonte da jurisprudência

1. **Fonte principal:** ferramentas da EmentAI (servidor MCP `EmentAI_jurisprud_ncia_e_legisla_o_brasileiras`).
   Carregue-as com ToolSearch (`select:` + nomes abaixo) antes do primeiro uso:
   - `pesquisar_jurisprudencia` — sempre com `tribunal: "TJES"` e `tipo: "acordao"`.
   - `obter_decisao` — inteiro teor/ementa completa de um resultado (pelo `id`).
   - `verificar_citacao` e `conferir_peca` — conferência das citações já existentes na minuta.
   - `pesquisar_sumulas` / `pesquisar_precedentes` — súmulas e temas vinculantes (STF/STJ) quando o ponto exigir.
2. **Site oficial:** https://sistemas.tjes.jus.br/consulta-jurisprudencia/ — cada resultado da
   EmentAI traz o link "Fonte oficial" para esse site. Cite sempre esse link para o usuário conferir.
   (O site bloqueia acesso a partir de servidores na nuvem; por isso a consulta é feita pela EmentAI.)

## Filtro obrigatório: só acórdão de segundo grau

Considere apenas acórdãos de **Câmaras** (Cíveis, Criminais, Reunidas) e do **Tribunal Pleno** do TJES.
**Descarte** e não use como parâmetro:
- Acórdãos de **Turma Recursal** dos Juizados (sinais: "recurso inominado", "Turma Recursal",
  "Colegiado Recursal", "Juizado Especial" como órgão julgador, numeração de processo dos Juizados).
- Decisões monocráticas (mesmo de desembargador).
- Sentenças de primeiro grau.

Na dúvida sobre o órgão julgador (a EmentAI às vezes mostra "Órgão: n/i"), use `obter_decisao`
e verifique a classe ("Apelação Cível", "Agravo de Instrumento", "Embargos de Declaração" de câmara etc.).
Se continuar incerto, só use o julgado sinalizando a incerteza no relatório.

Prefira, nesta ordem: julgados mais recentes (últimos 2–3 anos; passe `data_inicio`), julgados
que reflitam entendimento reiterado (vários acórdãos no mesmo sentido), e da Câmara com competência
sobre a matéria. Teses vinculantes (STF/STJ repetitivos, IRDR/IAC do TJES, súmulas) prevalecem sobre
acórdãos isolados — se a minuta contrariar uma delas, isso é divergência grave.

## Fluxo

### 1. Receber e ler a minuta
- Aceite texto colado, `.docx` ou `.pdf`. Para `.docx` use a skill `anthropic-skills:docx`; para PDF, `anthropic-skills:pdf`.
- Identifique: tipo de ato, classe/matéria, partes (sem expor dados pessoais fora do necessário),
  pedidos, e **cada questão jurídica decidida** (ex.: prescrição, legitimidade, dano moral in re ipsa,
  quantum indenizatório, juros/correção, honorários, gratuidade).

### 2. Pesquisar o entendimento do TJES por questão
- Para cada questão, faça 1–2 pesquisas objetivas (`limite` 5–10), com a tese em linguagem natural.
- Para valores (dano moral, honorários, multa), colete os patamares que o TJES tem mantido em casos análogos
  e calcule uma faixa usual (mínimo–máximo e o valor mais frequente), indicando os acórdãos que a sustentam.
- Abra o inteiro teor (`obter_decisao`) dos 1–3 julgados mais relevantes antes de usá-los como base.

### 3. Conferir as citações da minuta
- Rode `conferir_peca` com o texto da minuta (até 60 mil caracteres; divida se maior).
- Para cada citação com problema (inexistente, dados divergentes, súmula cancelada, artigo revogado,
  tese que não corresponde à ementa), aprofunde com `verificar_citacao` informando relator, data e tese.
- "Não encontrado" não prova que a citação é falsa: classifique como "não confirmada — conferir manualmente".

### 4. Classificar cada ponto
| Classificação | Quando |
|---|---|
| **Divergente** | A minuta decide em sentido contrário ao entendimento predominante do TJES ou a tese vinculante. |
| **Parcialmente alinhada** | Mesma conclusão, mas fundamento, parâmetro (valor, índice, termo inicial) ou alcance diferente. |
| **Alinhada** | Conforme o TJES; pode ganhar reforço com precedente. |
| **Sem parâmetro** | Não foram encontrados acórdãos de 2º grau suficientes; diga isso, não invente. |

Se houver **divergência interna entre Câmaras do TJES**, não escolha silenciosamente: mostre as duas
correntes, com os julgados de cada, e indique qual é majoritária/mais recente.

### 5. Reescrever a minuta
- Corrija apenas o necessário: trechos divergentes, citações erradas, parâmetros fora da faixa do TJES,
  e inclua precedentes do TJES na fundamentação onde reforcem a decisão.
- Preserve o estilo, a estrutura e a conclusão do magistrado sempre que estiverem alinhadas.
  Se a correção **mudar o resultado** (procedência/improcedência, provimento, valor da condenação),
  não aplique sozinho: proponha a alteração e destaque que depende de decisão do usuário.
- Formato de citação dos precedentes do TJES:
  `TJES, Apelação Cível nº 0000000-00.0000.8.08.0000, Rel. Des. Nome, [Órgão julgador], j. dd/mm/aaaa.`
  Use apenas dados confirmados pela ferramenta; não complete relator, órgão ou data por suposição.
- Saída da minuta revisada:
  - Se a entrada foi `.docx`: gere `.docx` com **controle de alterações** (tracked changes) pela skill `anthropic-skills:docx`,
    para o usuário aceitar/rejeitar cada mudança.
  - Se foi texto: devolva o texto com ~~trecho removido~~ e **trecho incluído**, e também uma versão limpa.

### 6. Relatório de correção (sempre, antes da minuta)
Estrutura:
1. **Resumo** — quantos pontos divergentes, parcialmente alinhados e alinhados; alterações que mudam o resultado.
2. **Divergências** — para cada uma: trecho da minuta → entendimento do TJES → acórdãos (número, relator,
   órgão, data, link oficial, trecho da ementa) → correção proposta.
3. **Citações conferidas** — tabela: citação | situação (confirmada / divergente / não confirmada) | observação.
4. **Precedentes sugeridos** — onde incluir e por quê.
5. **Pontos sem parâmetro ou com divergência entre Câmaras.**

## Cuidados
- Nunca invente julgado, número, relator, data ou trecho de ementa. Todo precedente citado deve ter vindo
  de uma ferramenta nesta sessão, com o link oficial do TJES.
- Ementas resumem: antes de afirmar a tese de um acórdão, confira que o trecho realmente a sustenta.
- Use ementa recente; se o único precedente for antigo (antes de 2020) ou anterior a mudança legislativa
  ou tese vinculante posterior, sinalize.
- Para revisão técnico-processual geral (art. 489 CPC, congruência, honorários) combine com a skill
  `anthropic-skills:revisao-decisao-civel`; esta skill foca na aderência à jurisprudência do TJES.
- A palavra final é do magistrado: o relatório é apoio, não substitui a conferência no inteiro teor.
