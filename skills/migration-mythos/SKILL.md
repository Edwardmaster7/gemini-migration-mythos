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
│   └── Gera: GEMINI.md, ai-context.md, ai-discovery-guidelines.md
│       └── Usa internamente: @codebase_investigator, @generalist
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

<thinking>
Antes de iniciar qualquer trabalho, preciso entender:
1. O que exatamente deve ser migrado? (feature, módulo, subsistema, função específica?)
2. Qual é a origem? (repo único, estrutura multi-versão, múltiplos repositórios?)
3. Qual é o destino? (repo existente? novo repo? branch específica?)
4. Existem instruções adicionais no prompt invocador? (manter API, mudar linguagem, targets de performance?)
5. Qual é o nível de autonomia aprovado? (pedir confirmação a cada fase? ou executar automaticamente?)
</thinking>

### 0.1 — Checklist de Contexto Obrigatório

| Item | Obrigatório | Como Obter se Ausente |
|------|-------------|----------------------|
| Caminho/URL do repo legado | ✅ SIM | Perguntar ao usuário |
| Nome/descrição da feature | ✅ SIM | Perguntar ao usuário |
| Caminho/URL do repo destino | ✅ SIM | Perguntar ao usuário |
| Instruções adicionais do prompt | ⬜ OPCIONAL | Inferir do contexto |
| Tipo de estrutura legada (único vs. multi-versão) | ⬜ OPCIONAL | Detectar na Phase 1 |
| Estratégia de testes no destino | ⬜ OPCIONAL | Inferir das convenções do repo destino |

**Se qualquer item obrigatório estiver ausente → parar e perguntar antes de prosseguir.**

### 0.2 — Parâmetros de Invocação Consolidados

Após a coleta de contexto, consolidar internamente:

```
FEATURE_NAME    = <nome da feature>
LEGACY_PATH     = <caminho do repo/diretório legado>
TARGET_PATH     = <caminho do repo destino>
MULTI_VERSION   = <true|false> (há múltiplos subdiretórios com versões?)
EXTRA_INSTRUCTIONS = <instruções adicionais do usuário>
AUTO_EXECUTE    = <true|false> (o usuário aprovou execução automática?)
```

### 0.3 — Pre-flight Check (Python & uv Dependency)

1. Execute silenciosamente `command -v uv` para verificar se o `uv` está disponível.
2. Se `uv` estiver disponível: 
   - Utilize-o para rodar todos os scripts da fase de automação: `uv run uv run python skills/migration-mythos/scripts/...`
3. Se `uv` NÃO estiver disponível, verifique o `python3`:
   - Execute `python3 --version`. Se existir, utilize `python3 skills/migration-mythos/scripts/...`
4. **Se nenhum estiver disponível (Native Fallback):** 
   - NÃO aborte a migração.
   - Em vez de usar os scripts `.py`, substitua o trabalho usando exaustivamente as ferramentas nativas `glob` e `grep_search` para simular as extrações de artefatos.


---

## Phase 1 — Context Engineering do Legado

**Objetivo:** Mapear o ecossistema legado e gerar artefatos de contexto que guiarão todas as fases seguintes.

**Delegado para:** skill `legacy-context-engineer`

### 1.1 — Ativação da Skill

Invocar a skill com o seguinte formato:

```
Ative a skill `legacy-context-engineer`.
Diretório Alvo: [LEGACY_PATH]
Fontes e Dicas: [FEATURE_NAME, linguagem principal se conhecida, sinônimos relevantes]
```

### 1.2 — Para Estruturas Multi-Versão

Se `MULTI_VERSION = true`, antes de ativar `legacy-context-engineer`:

1. Executar: `uv run python skills/migration-mythos/scripts/diff_versions.py --root <LEGACY_PATH> --feature "<FEATURE_NAME>"`
2. Identificar a **versão canônica** (a mais completa)
3. Ativar `legacy-context-engineer` apontando para a versão canônica
4. **Opcionalmente**, executar `legacy-context-engineer` nos outros diretórios de versão para capturar divergências

### 1.3 — Entregáveis Esperados da Phase 1

Verificar que os seguintes artefatos foram gerados DENTRO do repositório legado:
- `[LEGACY_PATH]/GEMINI.md` — indexador raiz do sistema legado
- `[LEGACY_PATH]/[pasta_ai]/ai-context.md` — contexto profundo de negócio
- `[LEGACY_PATH]/[pasta_ai]/ai-discovery-guidelines.md` — guia de navegação cirúrgica

**⛔ Não avançar para Phase 2 sem estes 3 artefatos.**

---

## Phase 2 — Arqueologia da Feature

**Objetivo:** Análise exaustiva e documentação profunda da feature específica a ser migrada.

**Delegado para:** skill `legacy-feature-archaeologist`

### 2.1 — Ativação da Skill

Invocar a skill com o seguinte formato, utilizando os artefatos gerados na Phase 1 como contexto:

```
Feature: [FEATURE_NAME]
Fontes: [LEGACY_PATH] (priorizar versão canônica se multi-versão)
Domain hints: [sinônimos, siglas, aliases, nomes históricos — extraídos do ai-context.md se disponível]
Restrições: [EXTRA_INSTRUCTIONS se relevante para a arqueologia]
```

### 2.2 — Para Estruturas Multi-Versão

Incluir na invocação todas as fontes relevantes:

```
Feature: [FEATURE_NAME]
Fontes:
  - [LEGACY_PATH]/v3/ (canônica)
  - [LEGACY_PATH]/v2/ (verificar divergências)
  - [LEGACY_PATH]/v1/ (histórico)
Domain hints: [...]
```

### 2.3 — Entregáveis Esperados da Phase 2

Verificar que os seguintes artefatos foram gerados:
- `overview.md` — topologia de componentes, fluxo principal, débito técnico
- `business_rules.md` — regras de negócio com evidências concretas, cenários Gherkin
- `tech_design.md` — design técnico, dicionário de dados, acoplamentos, efeitos colaterais

**Ler estes 3 arquivos antes de iniciar a Phase 3.** Eles são o insumo primário do planejamento.

---

## Phase 3 — Planejamento da Migração

**Objetivo:** Produzir um plano de migração detalhado, ordenado e verificável antes de escrever qualquer código.

**Delegado para:** subagente `@migration-architect`

### 3.1 — Contexto a Passar para o Arquiteto

Antes de acionar `@migration-architect`, preparar o seguinte sumário (baseado nas Phases 1 e 2):

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

| Situação | Padrão Recomendado |
|----------|--------------------|
| Feature usada por muitos consumidores | Strangler Fig + ACL |
| Fortemente acoplada, não desacoplável | Branch-by-Abstraction |
| Feature pequena e isolada | Direct Port |
| Linguagem/framework diferente | Rewrite com Contract Test |
| Feature com muitos efeitos colaterais | Adapter + Shadow Mode |
| Multi-versão com comportamentos conflitantes | Canonical Selection + Behavioral Spec |

### 3.3 — Gate de Aprovação do Plano

Antes de avançar para a execução, apresentar ao usuário:

```
📋 PLANO DE MIGRAÇÃO PRONTO

Feature: [FEATURE_NAME]
Origem: [LEGACY_PATH]
Destino: [TARGET_PATH]
Padrão escolhido: [PADRÃO]
Total de tarefas: [N] etapas
Complexidade estimada: BAIXA | MÉDIA | ALTA
Riscos principais: [top 3 riscos]

[Listagem das tarefas em alto nível]

→ Posso prosseguir com a execução? (sim / ajustar plano / abortar)
```

**NÃO avançar para Phase 4 sem aprovação explícita do usuário,
salvo se o prompt original contiver "execute automaticamente", "auto-execute" ou similar.**

---

## Phase 4 — Execução da Migração

**Objetivo:** Executar o plano aprovado, etapa por etapa, verificando cada passo antes de avançar.

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

**Delegado para:** subagente `@migration-validator`

### 5.1 — Contexto a Passar para o Validador

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

1. **Executive Summary** — o quê foi migrado, de onde, para onde, quando
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

| Cenário de Erro | Estratégia de Recuperação |
|-----------------|---------------------------|
| `legacy-context-engineer` falha (permissões, git error) | Tentar com `--shallow`; fallback manual via grep |
| `legacy-feature-archaeologist` não encontra a feature | Ampliar domain hints; pedir ao usuário confirmação do nome |
| `@migration-architect` gera plano com >30 etapas | Chunking em sub-migrações; apresentar ao usuário para priorização |
| Conflitos no repo destino com arquivos migrados | Gerar relatório de conflitos; usuário decide resolução |
| Testes falham após migração | Modo debug do `@migration-validator`; relatório de diff comportamental |
| MCP GitHub indisponível | Fallback completo para bash/git |
| Feature abrange >50 arquivos | Dividir em sub-features; executar fases iterativamente |

---

## Recursos Disponíveis

| Recurso | Caminho | Propósito |
|---------|---------|-----------|
| Skill: Context Engineering | `legacy-context-engineer` (skill externa) | Gera GEMINI.md, ai-context.md, ai-discovery-guidelines.md |
| Skill: Feature Archaeology | `legacy-feature-archaeologist` (skill externa) | Gera overview.md, business_rules.md, tech_design.md |
| Subagente: Arquiteto | `agents/migration-architect.md` | Plano de migração detalhado |
| Subagente: Validador | `agents/migration-validator.md` | Validação pós-migração |
| Padrões de Migração | `skills/migration-mythos/references/MIGRATION_PATTERNS.md` | Strangler Fig, ACL, etc. |
| Checklist de Verificação | `skills/migration-mythos/references/VERIFICATION_CHECKLIST.md` | Validação completa |
| Script: Diff de Versões | `skills/migration-mythos/scripts/diff_versions.py` | Comparação multi-versão |
| Script: Scan de Repo | `skills/migration-mythos/scripts/scan_repo.py` | Mapeamento de artefatos |
| Script: Extração | `skills/migration-mythos/scripts/extract_feature.py` | Extração de artefatos |
| Script: Plano | `skills/migration-mythos/scripts/migration_plan.py` | Geração de plano JSON |
| Script: Validação | `skills/migration-mythos/scripts/validate_migration.py` | Validação automatizada |
| Template de Relatório | `skills/migration-mythos/assets/migration_report_template.md` | Relatório final de migração |
| Schema do Feature Map | `skills/migration-mythos/assets/feature_map_schema.json` | Schema JSON para feature maps |

