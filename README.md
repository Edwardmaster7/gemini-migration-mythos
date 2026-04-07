# 🏛️ Gemini CLI Extension: Migration Mythos

O **Migration Mythos** é um orquestrador avançado para o [Gemini CLI](https://github.com/google/gemini-cli) projetado para automatizar e estruturar sistematicamente a migração de features e módulos inteiros de sistemas legados para repositórios modernos.

Focado em resiliência de engenharia e preservação de histórico, ele conta com um arsenal de agentes autônomos e skills para desvendar arquiteturas monolíticas difusas, mapeá-las sem causar destruição de contexto, e produzir reescritas precisas através de fluxos nativos e/ou TDD rigorosos.

---

## 🚀 Instalação e Configuração

**1. Instale a extensão do orquestrador via repositório:**
```bash
gemini extensions install https://github.com/Edwardmaster7/gemini-migration-mythos.git
```

**2. [OPCIONAL, PORÉM RECOMENDADO] Instale a extensão de execução TDD:**
O framework possui uma integração nativa avançada para planejar e executar as migrações no modelo TDD da extensão *Superpowers*. Para habilitar este "Workflow Ouro", instale também no seu CLI global:
```bash
gemini extensions install https://github.com/obra/superpowers
```

---

## ⚠️ Pré-requisitos (Python & uv)

Para que a automação pesada e os relatórios estatísticos da migração funcionem de forma ultra-rápida, modular e segura, este projeto adota o instalador **`uv`**:
- Ter o **[uv](https://github.com/astral-sh/uv)** instalado no ambiente para criação efêmera de módulos das dependências;
- Ter **Python 3.8+**;

Se detectar a ferramenta `uv`, a inteligência artificial executará os scripts via `uv run python`. Em falhas eventuais de contexto, a IA faz fallbacks progressivos até o uso barebones nativo (procurando e varrendo os arquivos manualmente).

---

## 📦 O que tem na caixa?

Este plugin unifica **Skills** (diretrizes de orquestração de pensamento) e **Sub-agentes** (assistentes operacionais especializados).

### 🧠 Guia de Workflows (Skills)
- **`migration-mythos` (Orquestrador):** Detém o mapa mestre do fluxo. Avalia se deve bifurcar para planificação via Extensão Superpowers ou roteamento interno.
- **`legacy-context-engineer`:** Realiza estudos topográficos do projeto de origem para mapear regras macros.
- **`legacy-feature-archaeologist`:** O especialista em leitura de débitos. Ele levanta regras de negócio implícitas sob dezenas de camadas e traça dependências sombrias da *Feature* solicitada.

### 🤖 Especialistas Autônomos (Agentes Corporais)
A inteligência de execução das premissas coletadas pela Arqueologia e pela Engenharia de Contexto se manifesta nesses avatares:
- **`@migration-architect`:** O maestro das passagens. Esse agente compila os achados do legado para produzir Planos de Migração rigorosos, elegendo padrões arquiteturais adequados a cada contexto (ex: escolhendo aplicar *Strangler Fig*, *Branch-By-Abstraction* ou um *Direct Rewrite* seco).
- **`@migration-validator`:** O agente detetive de Regressão. Acionado nas fases finais (ou em modo TDD durante as passagens RED -> GREEN do workflow) garantindo que, por exemplo, um parser XML antigo está se comportando homogeneamente contra o novo Parser JSON na refatoração, através da execução dura de scripts, checagem e lint test.

---

## 🛡️ Principais Capacidades da Automação

### 1. Gate de Segurança e Idempotência Rigorosa
Uma vez que varreduras em legados custam tempo e tokens caros, todo o orquestrador bloqueia por padrão *reescritas automáticas* de documentação. Quando executado num local em que arquivos como `GEMINI.md` ou `overview.md` já existem (independentemente de sinônimos como `docs/` ou `documentacao/`), ele para a execução em um **Gate** exigindo resposta humana interativa:
- `1. Sobrescrever` ou `2. Mesclar de forma cirúrgica`. 
O agente **NUNCA** apagará passagens históricas da engenharia de contexto por contra própria.

### 2. Classificador de Escopo (Domínios x Features)
Se um desenvolvedor tentar enviar uma migração global como `clientes` (um mar de sub-sistemas) ao invés de buscar por `login_auth_financeiro_cliente`, o orquestrador `migration-mythos` é treinado para interceptar a ação (Phase 2.1).
Ele alertará que a heurística detectou tratar-se de um **Domínio Gigante** e solicitará autorização consciente para executar uma varredura sistêmica maciça. Autorizado, ele estrutura a documentação de maneira elegantemente aninhada (`/docs/features/clientes/...feature_A`).

### 3. Workflow Bifurcado Inteligente (`USE_SUPERPOWERS`)
Dependendo da gravidade e da maturidade necessária:
- Se você optar por "Sim" na integração de Superpowers no início da conversa, o orquestrador usará a arqueologia do legado como alavanca e deixará toda a implementação futura para as sub-skills da ferramenta oficial do Google (`brainstorming` -> `writing-plans` -> `executing-plans`), garantindo micro-commits passados em batches. 
- Sem a extensão, os agentes independentes Arquitetos e Validadores nativos deste repositório garantem abordagens seguras *one-time-shot* ou em pedaços de macro passos, sem a rigidez da burocracia de micro-commits do Superpowers.

---

## 🎯 Como Usar na Prática

No seu prompt de terminal:

> *"Ative a skill `migration-mythos`.*
> *Feature: Exportação Fiscal Faturamento*
> *Origem: /Users/eu/projetos/legado-delphi*
> *Destino: /Users/eu/projetos/novo-microsservico-python"*

Daqui em diante, responda com `S` ou `N` para as perguntas interativas das automações nos Gates Operacionais.

---

## ⚙️ Como Customizar e Evoluir o Plugin

O poder deste plugin está na maleabilidade de adaptação para a stack legada de sua corporação, seja ela `COBOL` ou `NodeJS`.

### 1. Extensões Alvo da Investigação (Scripts)
Se o seu repositório legado usa arquivos específicos, você deve enriquecer o dicionário de varredura:
- **Arquivo:** `skills/migration-mythos/scripts/scan_repo.py`
- Exemplo na variável `SUPPORTED_EXTENSIONS`:
  ```python
  SUPPORTED_EXTENSIONS = {
      "delphi": [".pas", ".dfm", ".dpr", ".inc"], # Linguagens customizadas!
  }
  ```

### 2. Matrizes de Avaliação de QA (Validators)
Alinhe o Agente Validador corporativo aos checkstyles de sua empresa.
- **Onde alterar:** Modifique no arquivo de checklist obrigatório em `skills/migration-mythos/references/VERIFICATION_CHECKLIST.md`. Itens com `🔴 BLOQUEANTE` travam o Validador.

### 3. Injeção de Padrões Arquiteturais 
As heurísticas usadas na documentação técnica. Adicione metodologias autorizadas de sua Engenharia (e.g., Vertical Slicing corporativo) no arquivo `skills/migration-mythos/references/MIGRATION_PATTERNS.md` lido pelo Arquiteto.
