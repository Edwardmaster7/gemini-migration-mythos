---
name: migration-mythos
description: >
  Orchestrates end-to-end feature migration from legacy repositories to modern target repositories.
  Coordinates specialized skills (legacy-context-engineer, legacy-feature-archaeologist) and
  sub-agents (migration-architect, migration-validator) across six phases: context intake,
  legacy context engineering, feature archaeology, migration planning, execution, and validation.
  Activate for prompts like: "migrate feature X from legacy repo to target", "port module Y",
  "extract and migrate this feature", "move this functionality to the new system".
  Also handles multi-version legacy structures (N directories of the same system).
---

> **Compatibilidade:** Este skill funciona em **Claude Code** e **Gemini CLI**.
> - Sub-agentes `@migration-architect`/`@migration-validator`: invocados via `@nome` no Gemini CLI; via `Agent` tool (tipo `general-purpose`, passsando o conteúdo do arquivo `agents/<nome>.md` como prompt) no Claude Code.
> - Workflow estruturado: usa **Superpowers** (Gemini CLI) ou **Plan Mode** nativo (Claude Code) — ambos ativados pelo mesmo flag `USE_STRUCTURED_WORKFLOW`.
> - Sub-skills: ativadas da mesma forma em ambos os ambientes via nome da skill.
# 🏛️ Migration Mythos

> *"Every legacy system is an archaeological site. We don't demolish — we excavate, study, and translate."*

**Migration Mythos** é um orquestrador de migração de features legadas para repositórios modernos.
Ele coordena um ecossistema completo de skills especializadas e subagentes para garantir que nenhum
detalhe da feature seja perdido no processo de migração.

---

## Índice

1. [Quando Ativar](#quando-ativar)
2. [Arquitetura do Ecossistema](#arquitetura-do-ecossistema)
3. [Phase 0 — Context Intake](#phase-0--context-intake)
4. [Phase 1 — Context Engineering do Legado](#phase-1--context-engineering-do-legado)
5. [Phase 2 — Arqueologia da Feature](#phase-2--arqueologia-da-feature)
6. [Phase 3 — Planejamento da Migração](#phase-3--planejamento-da-migração)
7. [Phase 4 — Execução da Migração](#phase-4--execução-da-migração)
8. [Phase 5 — Validação e Verificação](#phase-5--validação-e-verificação)
9. [Phase 6 — Relatório Final](#phase-6--relatório-final)
10. [Árvores de Decisão](#árvores-de-decisão)
11. [Tratamento de Erros e Recuperação](#tratamento-de-erros-e-recuperação)
12. [Recursos Disponíveis](#recursos-disponíveis)
13. [Integração com Superpowers](#integração-com-superpowers)

---

## Quando Ativar

Ativar quando o prompt do usuário contiver **qualquer** destes sinais:

- Migrar, portar, extrair ou mover uma feature/módulo/subsistema
- Referências a "repo legado", "sistema antigo", "legado", diretórios com versões (v1, v2, v3...)
- "Trazer", "adaptar" ou "replicar" comportamento de um sistema antigo
- Menção de uma origem (legado) E um destino (novo repositório)

**NÃO ativar** para:

- Refatoração pura dentro de um único repositório sem mudança de destino
- Migrações de infraestrutura sem migração de código

---

## Arquitetura do Ecossistema

```
migration-mythos (ORQUESTRADOR)
│
├── PHASE 1 → skill: legacy-context-engineer
│   └── Gera: GEMINI.md + CLAUDE.md, ai-context.md, ai-discovery-guidelines.md
│       └── Usa internamente: @codebase_investigator (Gemini) / Glob+Grep+Agent (Claude Code)
│
├── PHASE 2 → skill: legacy-feature-archaeologist
│   └── Gera: overview.md, business_rules.md, tech_design.md
│
├── PHASE 3 → subagent: @migration-architect
│   └── Gera: migration_plan.json, MIGRATION_PLAN.md
│
├── PHASE 4 → main agent (este skill)
│   └── Usa: filesystem tools, bash, MCP GitHub, outras skills disponíveis
│
├── PHASE 5 → subagent: @migration-validator
│   └── Gera: validation_report.md
│
└── PHASE 6 → main agent
    └── Gera: MIGRATION_REPORT_<FEATURE>_<DATE>.md
```

**Princípio de orquestração:** Migration Mythos age como um **Supervisor Pattern** —
recebe o objetivo, decompõe em fases, delega para especialistas, consolida resultados,
e só avança para a próxima fase após validação de cada entregável.

---

## Phase 0 — Context Intake

**Objetivo:** Estabelecer o briefing completo antes de qualquer ação.

> ⚠️ **PRINCÍPIO FUNDAMENTAL DE AUTORIZAÇÃO**
> Este orquestrador opera sob um modelo de **aprovação explícita**. Nenhum código será
> escrito, modificado ou deletado sem que o usuário tenha revisado e aprovado o plano
> de migração (Phase 3). O valor padrão de `AUTO_EXECUTE` é sempre **`false`** —
> só é alterado para `true` se o usuário declarar isso explicitamente no prompt.

<thinking>
Antes de iniciar qualquer trabalho, preciso entender:
1. O que exatamente deve ser migrado? (feature, módulo, subsistema, função específica?)
2. Qual é a origem? (repo único, estrutura multi-versão, múltiplos repositórios?)
3. Qual é o destino? (repo existente? novo repo? branch específica?)
4. Existem instruções adicionais no prompt invocador? (manter API, mudar linguagem, targets de performance?)
5. Qual é o nível de autonomia aprovado? (pedir confirmação a cada fase? ou executar automaticamente?)
</thinking>

### 0.1 — Checklist de Contexto Obrigatório

| Item                                                | Obrigatório | Como Obter se Ausente                    |
| --------------------------------------------------- | ------------ | ---------------------------------------- |
| Caminho/URL do repo legado                          | ✅ SIM       | Perguntar ao usuário                    |
| Nome/descrição da feature                         | ✅ SIM       | Perguntar ao usuário                    |
| Caminho/URL do repo destino                         | ✅ SIM       | Perguntar ao usuário                    |
| Instruções adicionais do prompt                   | ⬜ OPCIONAL  | Inferir do contexto                      |
| Tipo de estrutura legada (único vs. multi-versão) | ⬜ OPCIONAL  | Detectar na Phase 1                      |
| Estratégia de testes no destino                    | ⬜ OPCIONAL  | Inferir das convenções do repo destino |

**Se qualquer item obrigatório estiver ausente → parar e perguntar antes de prosseguir.**

### 0.2 — Parâmetros de Invocação Consolidados

Após a coleta de contexto, consolidar internamente:

```
FEATURE_NAME       = <nome da feature>
LEGACY_PATH        = <caminho do repo/diretório legado>
TARGET_PATH        = <caminho do repo destino>
MULTI_VERSION      = <true|false> (há múltiplos subdiretórios com versões?)
EXTRA_INSTRUCTIONS = <instruções adicionais do usuário>
AUTO_EXECUTE          = false  ← PADRÃO. Só muda para true se o usuário disser
                                 explicitamente: "execute automaticamente", "auto-execute"
                                 ou expressão equivalente no prompt original.
USE_STRUCTURED_WORKFLOW = <true|false>  ← definido na seção 0.4 abaixo
  ↳ No Gemini CLI: implementado via Extensão Superpowers
  ↳ No Claude Code: implementado via Plan Mode nativo + TaskCreate
USE_SUPERPOWERS    = <true|false>  ← alias legado, equivalente a USE_STRUCTURED_WORKFLOW no Gemini CLI
PENDING_MIGRATIONS = []     ← Pilha (Stack) para pausar/retomar migrações dependentes
```

> 🔒 **Regra de ouro:** Na dúvida sobre o nível de autonomia desejado, assuma
> `AUTO_EXECUTE = false` e aguarde aprovação explícita antes de cada fase de execução.

### 0.3 — Pre-flight Check (Python & uv Dependency)

1. Execute silenciosamente `command -v uv` para verificar se o `uv` está disponível.
2. Se `uv` estiver disponível:
   - Utilize-o para rodar todos os scripts da fase de automação: `uv run uv run python skills/migration-mythos/scripts/...`
3. Se `uv` NÃO estiver disponível, verifique o `python3`:
   - Execute `python3 --version`. Se existir, utilize `python3 skills/migration-mythos/scripts/...`
4. **Se nenhum estiver disponível (Native Fallback):**
   - NÃO aborte a migração.
   - Em vez de usar os scripts `.py`, substitua o trabalho usando exaustivamente as ferramentas nativas `glob` e `grep_search` para simular as extrações de artefatos.

### 0.4 — Workflow Estruturado Opt-in

Após coletar o contexto obrigatório (seção 0.1), **antes de iniciar qualquer Phase**, perguntar ao usuário:

```
⚡ Você gostaria de usar um workflow estruturado para guiar o planejamento
   e execução desta migração?

   O workflow estruturado oferece:
     1. Spec de design validada antes de qualquer código
     2. Plano detalhado com tasks bite-sized e checkpoints
     3. Execução em batches com revisão entre lotes

   → Deseja ativar? (sim / não)
```

**Se usuário responder "sim":**

**— No Gemini CLI (Extensão Superpowers):**

1. Verificar disponibilidade:
   ```bash
   gemini extensions list 2>/dev/null | grep -i superpowers
   ls ~/.gemini/extensions/ 2>/dev/null | grep -i superpowers
   ```
2. **Se disponível →** `USE_STRUCTURED_WORKFLOW = true`, `USE_SUPERPOWERS = true`
   - Anunciar: "✅ Extensão Superpowers detectada. Fluxo: brainstorming → /write-plan → /execute-plan."
3. **Se indisponível →** informar:
   ```
   ⚠️ A extensão Superpowers não foi detectada.
   Opções:
     A) Instalar: gemini extensions install https://github.com/obra/superpowers
     B) Continuar com fluxo nativo (Phases 3 e 4)
   ```
   - Instalar → re-verificar → `USE_STRUCTURED_WORKFLOW = true`
   - Continuar → `USE_STRUCTURED_WORKFLOW = false`

**— No Claude Code (Plan Mode Nativo):**

Plan Mode é sempre disponível nativamente no Claude Code. Se o usuário respondeu "sim":
- `USE_STRUCTURED_WORKFLOW = true`
- Anunciar: "✅ Workflow estruturado ativo via Plan Mode nativo. Fluxo: spec document → plano detalhado → execução com TaskCreate."

**Se usuário responder "não":** `USE_STRUCTURED_WORKFLOW = false` — seguir fluxo nativo.

---

## Phase 1 — Context Engineering do Legado

**Objetivo:** Mapear o ecossistema legado e gerar artefatos de contexto que guiarão todas as fases seguintes.

**Delegado para:** skill `legacy-context-engineer`

### 1.1 — Ativação da Skill

Invocar a skill com o seguinte formato:

```
Ative a skill `legacy-context-engineer`.
Diretório Alvo (Varredura): [caminho do subdiretório ou versão a analisar]
Diretório Raiz de IA (Saída): [LEGACY_PATH raiz] ← onde os artefatos de IA são salvos (SEMPRE o diretório agrupador raiz, nunca uma versão individual)
Fontes e Dicas: [FEATURE_NAME, linguagem principal se conhecida, sinônimos relevantes]
```

### 1.2 — Para Estruturas Multi-Versão

Se `MULTI_VERSION = true`, siga esta sequência ANTES de ativar o `legacy-context-engineer`:

1. Executar: `uv run python skills/migration-mythos/scripts/diff_versions.py --root <LEGACY_PATH> --feature "<FEATURE_NAME>"`
2. Informar o resultado ao usuário e **perguntar obrigatoriamente**:
   ```
   🗂️ Detectei múltiplas versões/subdiretórios no legado:
      [listar subdiretórios encontrados]

   A versão identificada como canônica é: [VERSÃO_CANÔNICA]

   Você deseja:
   1. Mapear apenas a versão canônica (`[VERSÃO_CANÔNICA]`)
   2. Mapear todas as versões disponíveis
   ```
3. **⛔ BLOQUEIO:** Aguarde a resposta do usuário antes de prosseguir.
4. Baseado na escolha do usuário:
   - **Opção 1 (Canônica):** `Diretório Alvo (Varredura): [LEGACY_PATH]/[VERSÃO_CANÔNICA]` + `Diretório Raiz de IA (Saída): [LEGACY_PATH]`.
   - **Opção 2 (Todas):** Iterar pelos subdiretórios relevantes, mantendo sempre `Diretório Raiz de IA (Saída): [LEGACY_PATH]`.

### 1.3 — Entregáveis Esperados da Phase 1

Verificar que os seguintes artefatos foram gerados no **Diretório Raiz de IA** (`[LEGACY_PATH]`), e **nunca** aninhados dentro de uma versão específica:

- `[LEGACY_PATH]/GEMINI.md` — indexador raiz para Gemini CLI
- `[LEGACY_PATH]/CLAUDE.md` — indexador raiz para Claude Code (mesmo conteúdo de GEMINI.md)
- `[LEGACY_PATH]/[pasta_ai]/ai-context.md` — contexto profundo consolidado
- `[LEGACY_PATH]/[pasta_ai]/ai-discovery-guidelines.md` — guia de navegação cirúrgica

**⛔ Não avançar para Phase 2 sem ao menos GEMINI.md ou CLAUDE.md + os 2 artefatos de IA na raiz do agrupador.**

---

## Phase 2 — Arqueologia da Feature

**Objetivo:** Análise exaustiva e documentação profunda da feature específica a ser migrada.

**Delegado para:** skill `legacy-feature-archaeologist`

### 2.1 — Classificação de Escopo (Domínio vs Feature)

Antes de iniciar qualquer verificação ou ativação de arqueologia, analise a semântica do `[FEATURE_NAME]` solicitado pelo usuário.

- **Feature:** Refere-se a uma funcionalidade restrita e específica (ex: "exportacao_pdf_cliente", "autenticacao_oauth", "checkout_carrinho").
- **Domínio:** Refere-se a um sistema amplo, um módulo agregador ou um agrupador de múltiplas features (ex: "clientes", "financeiro", "pagamentos", "estoque").

**Se você identificar o alvo como um Domínio, você DEVE interromper a execução e:**

1. Explicar e justificar a classificação: *"A funcionalidade '[FEATURE_NAME]' parece ser um Domínio completo composto por várias features, o que gerará um mapeamento profundo de todo o subsistema..."*
2. Perguntar ativamente: *"Você autoriza a adoção desse entendimento para seguir com o processo exploratório amplo de domínio?"*

**⛔ BLOQUEIO:** Aguarde a confirmação explícita do usuário antes de avançar para as próximas etapas (Idempotência e Ativação).

### 2.2 — Verificação de Idempotência (Pre-flight)

Antes de acionar a skill de arqueologia, verifique se os artefatos `overview.md`, `business_rules.md` e `tech_design.md` já existem nos diretórios de documentação do projeto legado (ou de cada versão correspondente no caso de multi-versão).

- Utilize `run_command` com `find` ou observe a estrutura de diretórios para buscar por esses arquivos.
- Se eles já existirem (mesmo parcialmente), a skill `legacy-feature-archaeologist` tem instruções próprias para mesclar o conteúdo. No entanto, se eles já cobrirem toda a especificação da feature atual, você pode **pular** a ativação da skill e prosseguir para a próxima Phase, poupando processamento.

### 2.3 — Ativação da Skill

Caso decida acionar a arqueologia (conteúdo faltando ou arquivos não existem), invoque a skill com o seguinte formato, utilizando os artefatos gerados na Phase 1 como contexto:

```
Feature: [FEATURE_NAME]
Scope: [Feature | Domain] (classificação identificada na etapa 2.1)
Fontes: [LEGACY_PATH] (priorizar versão canônica se multi-versão)
Domain hints: [sinônimos, siglas, aliases, nomes históricos — extraídos do ai-context.md se disponível]
Restrições: [EXTRA_INSTRUCTIONS se relevante para a arqueologia]
```

### 2.4 — Para Estruturas Multi-Versão

Incluir na invocação todas as fontes relevantes:

```
Feature: [FEATURE_NAME]
Scope: [Feature | Domain]
Fontes:
  - [LEGACY_PATH]/v3/ (canônica)
  - [LEGACY_PATH]/v2/ (verificar divergências)
  - [LEGACY_PATH]/v1/ (histórico)
Domain hints: [...]
```

### 2.5 — Entregáveis Esperados da Phase 2

Verificar que os seguintes artefatos foram gerados ou que já existem previamente:

- `overview.md` — topologia de componentes, fluxo principal, débito técnico
- `business_rules.md` — regras de negócio com evidências concretas, cenários Gherkin
- `tech_design.md` — design técnico, dicionário de dados, acoplamentos, efeitos colaterais

**Ler estes 3 arquivos antes de iniciar a Phase 2.1.** Eles são o insumo primário da orquestração e planejamento.

---

## Phase 2.1 — Gate de Priorização e Restrição de Contexto

**Objetivo:** Interceptar dependências críticas e gerenciar a fila (stack) de prioridade antes de despender tokens no planejamento e design.

1. Leia ativamente a seção `## Dependências Bloqueantes (Outras Features/Domínios)` do `overview.md` gerado pela Phase 2.
2. Liste as dependências encontradas.
3. Se houver pre-requisitos bloqueantes, realize uma estimativa heurística da complexidade (Baixa, Média, Alta) desses pre-requisitos.
4. Verifique com o usuário quais dessas dependências já foram migradas previamente para o repositório destino.
5. Para as dependências que ainda não foram migradas, peça autorização do usuário paralisando a Phase atual:
   > *"A feature atual [FEATURE_X] possui dependência funcional direta de [FEATURE_Y] (Complexidade Alta). Recomendo focar primeiro na migração de [FEATURE_Y] para não retermos débitos ocultos. Deseja aplicar o **Context Reset** e migrar a feature bloqueante primeiro?"*
   >
6. Se o usuário escolher "Sim":
   - **Stack Push**: Faça push de `[FEATURE_X]` para a lista `PENDING_MIGRATIONS`.
   - **Modify Target**: Altere o contexto ativo (`FEATURE_NAME = [FEATURE_Y]`).
   - **Worktrees (isolamento):**
     - **Gemini CLI com Superpowers:** Acione `superpowers:using-git-worktrees` para isolar a sub-migração.
     - **Claude Code:** Use `git worktree add <path> -b migration/<FEATURE_Y>` via Bash tool para criar um worktree isolado manualmente.
     - **Sem worktrees:** Crie uma branch `migration/<FEATURE_Y>` normalmente.
   - **Reset**: Retorne o fluxo inteiramente para a **Phase 1**, instruindo o `legacy-context-engineer` a mapear `[FEATURE_Y]` do absoluto zero.

---

## Phase 2.5 — Spec de Design (Workflow Estruturado)

> 🔀 **Esta phase só existe quando `USE_STRUCTURED_WORKFLOW = true`.** Se `false`, pular direto para Phase 3.

**Objetivo:** Produzir uma especificação de design validada pelo usuário antes de gerar o plano de implementação.

**Bifurcação por ambiente:**
- **Gemini CLI:** "Estou usando a skill `superpowers:brainstorming` para refinar o design desta migração."
- **Claude Code:** "Iniciando análise estruturada de design da migração com geração de spec document."

### 2.5.1 — Contexto de Entrada para a Spec

Alimentar o processo de spec com os achados das Phases 1 e 2:

> **Gemini CLI:** Invocar via `/brainstorm`.
> **Claude Code:** Usar análise estruturada direta com os dados abaixo.

```
[/brainstorm — Gemini CLI | Análise estruturada — Claude Code]

Estou migrando a feature [FEATURE_NAME] de [LEGACY_PATH] para [TARGET_PATH].

Contexto do legado (extraído da arqueologia):
- Propósito: [do overview.md]
- Componentes: [lista do overview.md]
- Regras de negócio críticas: [do business_rules.md]
- Dependências externas: [do tech_design.md]
- Débito técnico / riscos: [do overview.md]

Instruções adicionais do usuário: [EXTRA_INSTRUCTIONS]
```

### 2.5.2 — Checklist do Brainstorming (seguir em ordem)

1. **Explorar contexto do repo destino** — estrutura, convenções, stack
2. **Perguntas clarificadoras** — uma por vez: abordagem de migração, testes, compatibilidade de API, etc.
3. **Propor 2-3 abordagens** com trade-offs e recomendação
4. **Apresentar design em seções** — aguardar aprovação por seção
5. **Escrever spec/design doc** — salvar em:

   ```
   [PASTA_DE_DOCUMENTACAO]/specs/YYYY-MM-DD-[FEATURE_NAME]-migration-design.md
   ```

   > 🚨 **IMPORTANTE (Anti-Default Superpowers — Gemini CLI):** O framework tentará salvar em `docs/superpowers/specs/`. Impeça explicitamente: *"Encontre a pasta de documentação existente e salve em `[pasta-encontrada]/specs/`."*
   >
   > **Claude Code:** Use o `Write` tool diretamente no caminho correto. Nunca crie `docs/superpowers/`.
6. **Self-review da spec** — checar placeholders, contradições, ambiguidade
7. **Gate de revisão do usuário** — aguardar confirmação explícita antes de prosseguir

### 2.5.3 — Gate de Aprovação da Spec

> *"Spec escrita e commitada em `[PASTA_DE_DOCUMENTACAO]/specs/YYYY-MM-DD-[FEATURE_NAME]-migration-design.md`.
> Por favor revise e me diga se quer ajustes antes de começarmos o plano de implementação."*

**⛔ NÃO avançar para Phase 3 sem aprovação explícita da spec pelo usuário.**

---

## Phase 3 — Planejamento da Migração

**Objetivo:** Produzir um plano de migração detalhado, ordenado e verificável antes de escrever qualquer código.

**Delegado para:**
- **Fluxo nativo:** subagente `@migration-architect` (Gemini CLI) ou Agent tool com prompt de `agents/migration-architect.md` (Claude Code)
- **Fluxo estruturado Gemini:** `superpowers:writing-plans`
- **Fluxo estruturado Claude Code:** Plan Mode nativo + Write tool para salvar o plano

### 3.1 — Contexto a Passar para o Arquiteto

Antes de acionar o arquiteto, preparar o seguinte sumário (baseado nas Phases 1 e 2):

> **Invocação do arquiteto:**
> - **Gemini CLI:** `@migration-architect` com o brief abaixo.
> - **Claude Code:** Agent tool (tipo `general-purpose`) com o conteúdo de `agents/migration-architect.md` como prompt + o brief abaixo como contexto adicional.

```
MIGRATION BRIEF para migration-architect:

Feature: [FEATURE_NAME]
Origem: [LEGACY_PATH]
Destino: [TARGET_PATH]

Achados da Arqueologia (resumo do overview.md):
- Propósito: [...]
- Componentes principais: [lista dos artefatos-chave]
- Dependências críticas: [deps externas e internas]
- Débito técnico: [riscos identificados]

Achados das Regras de Negócio (resumo do business_rules.md):
- Regras críticas: [RN001, RN002, ...]
- Hardcodes e gambiarras: [lista]
- Casos de borda: [lista]

Design Técnico (resumo do tech_design.md):
- Arquitetura as-is: [descrição]
- Estruturas de dados afetadas: [lista]
- Integrações invisíveis: [lista]

Instruções adicionais do usuário: [EXTRA_INSTRUCTIONS]
```

### 3.2 — Escolha do Padrão de Migração

Consultar `skills/migration-mythos/references/MIGRATION_PATTERNS.md` e instruir `@migration-architect` a escolher o padrão adequado:

| Situação                                    | Padrão Recomendado                   |
| --------------------------------------------- | ------------------------------------- |
| Feature usada por muitos consumidores         | Strangler Fig + ACL                   |
| Fortemente acoplada, não desacoplável       | Branch-by-Abstraction                 |
| Feature pequena e isolada                     | Direct Port                           |
| Linguagem/framework diferente                 | Rewrite com Contract Test             |
| Feature com muitos efeitos colaterais         | Adapter + Shadow Mode                 |
| Multi-versão com comportamentos conflitantes | Canonical Selection + Behavioral Spec |

### 3.3 — Gate de Aprovação do Plano ⛔ OBRIGATÓRIO

> 🔀 **Bifurcação:** O comportamento desta seção depende de `USE_SUPERPOWERS`.

---

#### 3.3-A — SE `USE_STRUCTURED_WORKFLOW = true` → Fluxo Estruturado

> **Pré-requisito:** A spec da Phase 2.5 deve estar aprovada.

---

**— Gemini CLI (Superpowers `/write-plan`):**

**Announce:** "Estou usando a skill `superpowers:writing-plans` para gerar o plano de migração."

1. **Invocar `/write-plan`** referenciando a spec:
   ```
   /write-plan
   Spec de referência: [PASTA_DE_DOCUMENTACAO]/specs/YYYY-MM-DD-[FEATURE_NAME]-migration-design.md
   IMPORTANTE: Salve o plano em [PASTA_DE_DOCUMENTACAO]/plans/ (evite criar a pasta raiz padrão do superpowers).
   ```
   O Superpowers gera plano com tasks bite-sized (TDD: RED → GREEN → REFACTOR), caminhos exatos e checkboxes `- [ ]`.
2. Plano salvo em `[PASTA_DE_DOCUMENTACAO]/plans/YYYY-MM-DD-[FEATURE_NAME]-migration.md`
3. Self-review automático do Superpowers + apresentação ao usuário para aprovação.
4. Após aprovação: seguir para **Phase 4-A-Gemini**.

---

**— Claude Code (Plan Mode + Write):**

**Announce:** "Gerando plano de migração estruturado via Plan Mode."

1. Baseado na spec aprovada (Phase 2.5), construa um plano detalhado com:
   - Header: Goal, Architecture, Tech Stack
   - Tasks bite-sized numeradas com: descrição, arquivos afetados, critério de aceitação, comando de verificação
   - Checkboxes `- [ ]` para rastreamento
2. Escreva o plano usando o `Write` tool em:
   ```
   [PASTA_DE_DOCUMENTACAO]/plans/YYYY-MM-DD-[FEATURE_NAME]-migration.md
   ```
3. **Self-review manual do plano:**
   - Cobertura da spec: todas as requirements têm task correspondente?
   - Sem TBD, TODO, "implement later" sem resolução
   - Consistência de tipos e nomes entre tasks
4. Apresente ao usuário e aguarde aprovação explícita.
5. Após aprovação: seguir para **Phase 4-A-Claude**.

---

#### 3.3-B — SE `USE_SUPERPOWERS = false` → Fluxo Nativo

Antes de avançar para a execução, apresentar ao usuário o plano completo e aguardar
resposta explícita. Este gate é **incondicional** — mesmo que `AUTO_EXECUTE = true`,
o plano deve ser apresentado antes de qualquer escrita de código.

```
╔══════════════════════════════════════════════════════════════╗
║              📋 PLANO DE MIGRAÇÃO — REVISÃO OBRIGATÓRIA      ║
╠══════════════════════════════════════════════════════════════╣
║ Feature    : [FEATURE_NAME]                                  ║
║ Origem     : [LEGACY_PATH]                                   ║
║ Destino    : [TARGET_PATH]                                   ║
║ Padrão     : [PADRÃO ESCOLHIDO]                              ║
║ Etapas     : [N] tarefas                                     ║
║ Complexidade: BAIXA | MÉDIA | ALTA                           ║
║ Riscos     : [top 3 riscos identificados]                    ║
╠══════════════════════════════════════════════════════════════╣
║ TAREFAS PLANEJADAS:                                          ║
║ [Listagem numerada de todas as etapas em alto nível]         ║
╠══════════════════════════════════════════════════════════════╣
║ ⚠️  NENHUM CÓDIGO SERÁ ESCRITO OU MODIFICADO SEM SUA         ║
║    APROVAÇÃO. Aguardando sua decisão:                        ║
║                                                              ║
║  ✅ "sim" / "pode executar" → inicia Phase 4                 ║
║  ✏️  "ajustar" + instruções  → revisa o plano               ║
║  ❌ "abortar"               → encerra a migração             ║
╚══════════════════════════════════════════════════════════════╝
```

**⛔ BLOQUEIO ABSOLUTO: NÃO avançar para Phase 4 sem resposta afirmativa explícita
do usuário neste gate — sem exceções, mesmo que `AUTO_EXECUTE = true`.**

> A única exceção reconhecida é se o prompt original contiver a frase exata
> "execute automaticamente" ou "auto-execute" **e** o usuário ratificar isso
> ao ser apresentado ao resumo do plano.

---

## Phase 4 — Execução da Migração

**Objetivo:** Executar o plano **previamente aprovado pelo usuário no Gate 3.3**, etapa por etapa,
verificando cada passo antes de avançar.

> 🔒 **Pré-condição obrigatória:** A Phase 4 só pode iniciar após confirmação explícita
> do usuário no Gate 3.3. Se esta condição não foi satisfeita, retornar à Phase 3.

> 🔀 **Bifurcação:** O comportamento desta fase depende de `USE_SUPERPOWERS`.

---

### 4-A — SE `USE_STRUCTURED_WORKFLOW = true` → Execução Estruturada

---

**— 4-A-Gemini: Superpowers `/execute-plan`**

**Announce:** "Estou usando `superpowers:executing-plans` para executar o plano."

1. Carregar o plano em `[PASTA_DE_DOCUMENTACAO]/plans/YYYY-MM-DD-<feature-name>-migration.md`
2. Revisar criticamente + levantar dúvidas antes de iniciar
3. Invocar `/execute-plan`
4. Executar em **batches de 3 tasks** com checkpoints (TDD: test → fail → implement → pass → commit)
5. Se bloqueio mid-batch: **PARAR e escalar**
6. Após todas as tasks: usar `superpowers:finishing-a-development-branch`

> Após conclusão, retomar na **Phase 5** (Validação).

---

**— 4-A-Claude: Execução via TaskCreate + Checkpoints**

**Announce:** "Iniciando execução estruturada via task tracking nativo."

1. Carregar o plano em `[PASTA_DE_DOCUMENTACAO]/plans/YYYY-MM-DD-<feature-name>-migration.md`
2. Criar tasks no sistema de tarefas para cada task do plano (use `TaskCreate` para as principais)
3. Executar em **batches de 3 tasks** com checkpoints:
   - `TaskUpdate` → `status: in_progress` antes de iniciar
   - Executar o trabalho do plano exatamente
   - Verificar critério de aceitação
   - `TaskUpdate` → `status: completed` após verificação
   - Reportar ao usuário: o que foi feito + output de verificação
   - **⛔ AGUARDAR** feedback do usuário antes do próximo batch
4. Se bloqueio mid-batch: **PARAR e escalar** (não adivinhar)
5. Após todas as tasks: criar commit final de integração

**Regras durante execução (ambos os ambientes):**
- Nunca pular verificações definidas no plano
- Commits atômicos por task (conforme definido em 4.2)
- Escalar obrigatoriamente conforme 4.5

> Após conclusão, retomar na **Phase 5** (Validação).

---

### 4-B — SE `USE_SUPERPOWERS = false` → Fluxo Nativo

**Executor:** main agent (este skill), com acesso a filesystem, bash e MCP servers

### 4.1 — Loop de Execução (Planner-Executor com Auto-Correção)

Para cada tarefa do plano de migração:

```
<thinking>
Etapa N de M: [descrição da tarefa]
- Quais arquivos precisam ser criados/modificados?
- Qual é o critério de aceitação desta etapa?
- Há riscos específicos nesta etapa?
- Como verifico que esta etapa foi concluída com sucesso antes de avançar?
- Esta etapa requer aprovação do usuário? (deletar código existente? alterar auth? efeitos colaterais?)
</thinking>

1. Executar a tarefa
2. Verificar o critério de aceitação
3. Se PASSOU → registrar sucesso, avançar
4. Se FALHOU:
   → Tentar autocorreção (máx. 2 tentativas)
   → Se ainda falhar → escalar para o usuário com contexto completo
```

### 4.2 — Boas Práticas de Execução

- **Nunca sobrescrever** arquivos no repo destino sem antes ler e entender seu conteúdo atual
- **Preservar convenções do destino**: nomenclatura, formatação, padrões de teste do repo alvo
- **Commits atômicos**: cada etapa lógica em um commit separado
- **Disciplina de branch**: sempre criar `migration/<feature-name>` no repo destino

### 4.3 — Uso do MCP GitHub

Se MCP GitHub disponível:

```
→ mcp_github_create_branch: criar "migration/<FEATURE_NAME>"
→ mcp_github_push_files: commits atômicos por etapa
→ mcp_github_create_pull_request: finalizar como PR revisável
→ mcp_github_run_secret_scanning: antes de qualquer commit
```

Se MCP GitHub indisponível:

```
→ Usar bash com git para todas as operações de controle de versão
```

### 4.4 — Composição com Outras Skills

Se a migração envolver capacidades de outras skills disponíveis no agente,
**verificar skills disponíveis com `/skills` e ativá-las explicitamente**.

Exemplos:

- Migração envolve planilhas/Excel → ativar skill `xlsx`
- Migração envolve PDFs de documentação técnica → ativar skill `pdf`
- Migração requer pesquisa sobre padrões específicos do framework destino → ativar skill `research`

**Esta skill foi projetada para ser versátil e composta com outras skills do ecossistema.**

### 4.5 — Escalada Obrigatória ao Usuário

Sempre escalar (não tentar resolver autonomamente) quando:

- Execução requer **deletar** código existente no repo destino
- Migração toca código de **autenticação, autorização ou segurança**
- Descoberta de comportamento legado que **contradiz** a intenção declarada do usuário
- Feature tem **efeitos colaterais não documentados** (escrita em DB, envio de e-mails, etc.)
- Conflitos de merge que precisam de decisão de negócio

---

## Phase 5 — Validação e Verificação

**Objetivo:** Garantir que a feature migrada funciona corretamente no repositório destino.

**Delegado para:** subagente `@migration-validator` (Gemini CLI) ou Agent tool com prompt de `agents/migration-validator.md` (Claude Code)

### 5.1 — Contexto a Passar para o Validador

> **Invocação do validador:**
> - **Gemini CLI:** `@migration-validator` com o brief abaixo.
> - **Claude Code:** Agent tool (tipo `general-purpose`) com o conteúdo de `agents/migration-validator.md` como prompt + o brief abaixo como contexto.

```
VALIDATION BRIEF para migration-validator:

Feature migrada: [FEATURE_NAME]
Repo destino: [TARGET_PATH]
Branch: migration/[FEATURE_NAME]
Workspace de migração: ./migration_workspace/

Artefatos de referência:
- Regras de negócio originais: [path]/business_rules.md
- API contract: migration_plan.json (campo api_contract)
- Checklist completo: skills/migration-mythos/references/VERIFICATION_CHECKLIST.md

Critérios especiais do usuário: [EXTRA_INSTRUCTIONS relevantes para validação]
```

### 5.2 — Executar Script de Validação

```bash
uv run python skills/migration-mythos/scripts/validate_migration.py \
  --workspace ./migration_workspace/ \
  --target <TARGET_PATH> \
  --feature <FEATURE_NAME>
```

### 5.3 — Categorias de Validação

Consultar `skills/migration-mythos/references/VERIFICATION_CHECKLIST.md` para o checklist completo.
O validador deve cobrir no mínimo:

- ✅ Completude estrutural (todos os artefatos presentes)
- ✅ Qualidade de código (linting, sem debug prints, sem TODOs críticos)
- ✅ Integridade de dependências (sem imports apontando para legado)
- ✅ Segurança (secret scanning, sem credenciais hardcoded)
- ✅ Cobertura de testes (testes existem e passam)
- ✅ Ausência de regressões (suite existente do destino continua passando)
- ✅ Contrato de API (assinaturas e comportamentos conforme especificado)
- ✅ Equivalência comportamental (feature age como o legado documentado)

**⛔ Não avançar para Phase 6 se houver issues bloqueantes (❌) no relatório de validação.**

---

## Phase 6 — Relatório Final

**Objetivo:** Produzir documentação completa da migração para fins de auditoria, onboarding e histórico.

Usar o template em `skills/migration-mythos/assets/migration_report_template.md` para gerar o relatório final.

### 6.1 — Conteúdo do Relatório

1. **Executive Summary** — o quê foi migrado, de onde, para onde, quando *(Se migrou advindo de uma pausa de prioridade do contexto, obrigatoriamente inclua: "Este relatório trata de um pré-requisito e migração prévia exigida para a liberação da feature alvo original [FEATURE_X]")*.
2. **Archaeology Findings** — insights-chave sobre a feature legada (referências ao overview.md)
3. **Migration Decisions** — decisões arquiteturais tomadas e justificativas
4. **Changes Made** — lista de todos os arquivos criados, modificados, deletados
5. **Test Results** — cobertura e resultados do relatório de validação
6. **Known Limitations** — dívida técnica ou trabalho deferido
7. **Next Steps** — ações de follow-up recomendadas

### 6.2 — Destino do Relatório

Salvar como: `MIGRATION_REPORT_<FEATURE_NAME>_<YYYYMMDD>.md`

- Preferencialmente em: `<TARGET_PATH>/docs/migrations/`
- Fallback: raiz do `<TARGET_PATH>`

### 6.3 — PR Final (se MCP GitHub disponível)

```
→ Commit do relatório na branch migration/<FEATURE_NAME>
→ mcp_github_create_pull_request com:
   - title: "feat: migrate <FEATURE_NAME> from legacy"
   - body: link para o MIGRATION_REPORT + resumo dos achados principais
   - base: branch principal do repo destino
```

### 6.4 — Fluxo de Retomada (Popping the Stack)

1. Após a geração/finalização da migração (seja pelo fluxo nativo ou via fechamento de branch pela Phase 4 do Superpowers), avalie o cofre `PENDING_MIGRATIONS`.
2. Se a pilha NÃO estiver vazia (ex: `['Feature X']`):
   - Faça Pop da última feature pausada e mude `FEATURE_NAME` de volta para `Feature X`.
   - Comunique ao usuário: *"A migração dependente [FEATURE_Y] finalizou no relatório. Sua pendência original [FEATURE_X] teve seus bloqueios eliminados. Retomando context de migração..."*
   - Volte para o repositório principal de trabalho/worktree correta da Feature X.
   - Pule direto para a **Phase 2.5** (se `USE_STRUCTURED_WORKFLOW=true`) para Feature X com o novo contexto que [FEATURE_Y] já existe:
     - Gemini CLI: invocar `/brainstorm`
     - Claude Code: análise estruturada direta com Write tool para spec
   - Ou Phase 3 diretamente (se `USE_STRUCTURED_WORKFLOW=false`).

---

## Árvores de Decisão

### Single repo vs. Multi-versão?

```
Verificar LEGACY_PATH
       │
  ┌────┴────┐
  │         │
Single    Subdiretórios
 repo     com versões
  │         │
  ▼         ▼
Phase 1   diff_versions.py
direta    → canonical version
          → Phase 1 no canônico
          → Phase 2 com todas as fontes
```

### Qual artefato do legado usar como fonte da verdade?

```
Há business_rules.md gerado pelo legacy-feature-archaeologist?
  → SIM: Usar como fonte primária
  → NÃO: Executar Phase 2 antes de planejar qualquer coisa

business_rules.md tem divergências entre versões documentadas?
  → SIM: Escalar ao usuário quais comportamentos preservar
  → NÃO: Prosseguir com a versão canônica
```

---

## Tratamento de Erros e Recuperação

| Cenário de Erro                                           | Estratégia de Recuperação                                              |
| ---------------------------------------------------------- | ------------------------------------------------------------------------- |
| `legacy-context-engineer` falha (permissões, git error) | Tentar com `--shallow`; fallback manual via grep                        |
| `legacy-feature-archaeologist` não encontra a feature   | Ampliar domain hints; pedir ao usuário confirmação do nome             |
| `@migration-architect` gera plano com >30 etapas         | Chunking em sub-migrações; apresentar ao usuário para priorização    |
| Conflitos no repo destino com arquivos migrados            | Gerar relatório de conflitos; usuário decide resolução                |
| Testes falham após migração                             | Modo debug do `@migration-validator`; relatório de diff comportamental |
| MCP GitHub indisponível                                   | Fallback completo para bash/git                                           |
| Feature abrange >50 arquivos                               | Dividir em sub-features; executar fases iterativamente                    |
| Superpowers não instala / comando falha                   | Definir `USE_SUPERPOWERS = false`; prosseguir com fluxo nativo          |

---

## Recursos Disponíveis

| Recurso                    | Caminho                                                           | Propósito                                                      |
| -------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| Skill: Context Engineering | `legacy-context-engineer` (skill externa)                       | Gera GEMINI.md + CLAUDE.md, ai-context.md, ai-discovery-guidelines.md |
| Skill: Feature Archaeology | `legacy-feature-archaeologist` (skill externa)                  | Gera overview.md, business_rules.md, tech_design.md             |
| Subagente: Arquiteto       | `agents/migration-architect.md`                                 | Plano de migração detalhado (Gemini: `@migration-architect` / Claude Code: Agent tool) |
| Subagente: Validador       | `agents/migration-validator.md`                                 | Validação pós-migração (Gemini: `@migration-validator` / Claude Code: Agent tool) |
| Padrões de Migração     | `skills/migration-mythos/references/MIGRATION_PATTERNS.md`      | Strangler Fig, ACL, etc.                                        |
| Checklist de Verificação | `skills/migration-mythos/references/VERIFICATION_CHECKLIST.md`  | Validação completa                                            |
| Script: Diff de Versões   | `skills/migration-mythos/scripts/diff_versions.py`              | Comparação multi-versão                                      |
| Script: Scan de Repo       | `skills/migration-mythos/scripts/scan_repo.py`                  | Mapeamento de artefatos                                         |
| Script: Extração         | `skills/migration-mythos/scripts/extract_feature.py`            | Extração de artefatos                                         |
| Script: Plano              | `skills/migration-mythos/scripts/migration_plan.py`             | Geração de plano JSON                                         |
| Script: Validação        | `skills/migration-mythos/scripts/validate_migration.py`         | Validação automatizada                                        |
| Template de Relatório     | `skills/migration-mythos/assets/migration_report_template.md`   | Relatório final de migração                                  |
| Schema do Feature Map      | `skills/migration-mythos/assets/feature_map_schema.json`        | Schema JSON para feature maps                                   |
| Ext: Superpowers (Gemini)  | `gemini extensions install https://github.com/obra/superpowers` | Brainstorming + planning TDD + execução em batches (Gemini CLI only) |
| Plan Mode (Claude Code)    | Nativo no Claude Code                                           | Workflow estruturado equivalente ao Superpowers no Claude Code  |

---

## Workflow Estruturado: Superpowers (Gemini CLI) vs Plan Mode (Claude Code)

O workflow estruturado é uma integração **opcional** que adiciona as Phases 2.5 (spec) e enriquece as Phases 3 e 4 com planejamento rigoroso e execução em batches. Flag: `USE_STRUCTURED_WORKFLOW = true`.

### Quando Usar

| Cenário                                          | Recomendação                                                     |
| ------------------------------------------------- | ----------------------------------------------------------------- |
| Migração complexa com muitos componentes        | Workflow estruturado (spec + plano bite-sized facilita rastreamento) |
| Time novo no destino (baixo conhecimento do repo) | Workflow estruturado (levanta dúvidas antes de codar)           |
| Migração rápida e feature simples              | Fluxo nativo (menos overhead)                                     |

### Gemini CLI: Superpowers

**Instalação:**
```bash
gemini extensions install https://github.com/obra/superpowers
```

| Skill Superpowers                              | Phase         | O que Faz                                          |
| ---------------------------------------------- | ------------- | -------------------------------------------------- |
| `superpowers:brainstorming`                  | Phase 2.5     | Refina design, gera spec em `[DOCS]/specs/`      |
| `superpowers:writing-plans`                  | Phase 3.3-A   | Gera plano bite-sized com TDD em `[DOCS]/plans/` |
| `superpowers:executing-plans`                | Phase 4-A     | Executa plano em batches com checkpoints           |
| `superpowers:finishing-a-development-branch` | Pós Phase 4-A | Verifica e encerra branch de migração            |
| `superpowers:using-git-worktrees`            | Phase 2.1     | Isola sub-migrações em branches/worktrees        |

### Claude Code: Plan Mode Nativo

Todas as funcionalidades do Superpowers têm equivalente nativo no Claude Code:

| Superpowers (Gemini CLI)    | Claude Code Equivalent              |
| --------------------------- | ----------------------------------- |
| `/brainstorm`               | Análise estruturada + Write spec doc |
| `/write-plan`               | Write plano .md + Task tracking      |
| `/execute-plan`             | TaskCreate + execução por batch     |
| `finishing-a-development-branch` | git commit final + branch cleanup |
| `using-git-worktrees`       | `git worktree add` via Bash tool    |

### Estrutura de Diretórios (ambos os ambientes)

```
[PASTA_DE_DOCUMENTACAO_DO_USUARIO]/
├── specs/   ← design docs (Phase 2.5)
│   └── YYYY-MM-DD-<feature>-migration-design.md
└── plans/   ← planos de migração (Phase 3)
    └── YYYY-MM-DD-<feature>-migration.md
```

### Fluxo Completo com Workflow Estruturado

```
Phase 0 → opt-in workflow estruturado?
   ↓ sim
   USE_STRUCTURED_WORKFLOW = true
   ↓
Phase 1 → legacy-context-engineer    (inalterado)
   ↓
Phase 2 → legacy-feature-archaeologist    (inalterado)
   ↓
Phase 2.5 → Spec de design
   Gemini: superpowers:brainstorming via /brainstorm
   Claude: análise estruturada + Write tool
   → spec salva em [DOCS]/specs/YYYY-MM-DD-<feature>-migration-design.md
   → GATE: aprovação da spec pelo usuário (obrigatório)
   ↓
Phase 3 → Plano estruturado
   Gemini: superpowers:writing-plans via /write-plan
   Claude: plano detalhado via Write + Task tracking
   → plano salvo em [DOCS]/plans/YYYY-MM-DD-<feature>-migration.md
   → GATE: aprovação do plano pelo usuário (obrigatório)
   ↓
Phase 4 → Execução em batches
   Gemini: superpowers:executing-plans via /execute-plan
   Claude: TaskCreate → batches de 3 tasks → checkpoints
   → commits atômicos por task
   ↓
Phase 5 → migration-validator    (inalterado)
   ↓
Phase 6 → relatório final    (inalterado)
```
