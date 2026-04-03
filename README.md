# 🏛️ Gemini CLI Extension: Migration Mythos

O **Migration Mythos** é um orquestrador avançado para o [Gemini CLI](https://github.com/google/gemini-cli) projetado para automatizar e estruturar a migração de features e módulos de sistemas legados para repositórios modernos.

---

## ⚠️ Pré-requisitos

Para que a automação pesada funcione de forma otimizada, é **altamente recomendado** ter o Python instalado na máquina:
- **Python 3.8+** (utilizado pelos scripts de varredura e validação em massa).

*(Nota: Se o Python não estiver disponível no ambiente, a IA está programada para utilizar ferramentas de fallback nativas do Gemini CLI, como `grep_search` e `glob`. O processo continuará funcionando, mas poderá consumir mais tokens).*

---


## 📦 O que tem na caixa?

Este plugin combina **Skills** (diretrizes de comportamento) e **Sub-agentes** (assistentes autônomos especializados):

### 🧠 Skills (Guias de Workflow)
Localizadas em `skills/`:
- **`migration-mythos`**: O orquestrador central. Detém o mapa das 6 fases de migração.
- **`legacy-context-engineer`**: Faz o mapeamento arquitetural do repositório legado como um todo (Fase 1).
- **`legacy-feature-archaeologist`**: Analisa uma feature específica a fundo, extraindo regras de negócio e débitos técnicos (Fase 2).

### 🤖 Sub-agentes (Especialistas Autônomos)
Localizados em `agents/`:
- **`@migration-architect`**: Lê as descobertas da arqueologia e monta um plano de migração passo-a-passo (Fase 3).
- **`@migration-validator`**: Um QA rigoroso que roda checklists de segurança, integridade e testes após a escrita do código (Fase 5).

### 🛠️ Scripts Utilitários
Localizados em `skills/migration-mythos/scripts/`:
Scripts em Python que automatizam extrações pesadas sem sobrecarregar a janela de contexto (busca de arquivos, extração de variáveis de ambiente, comparações estruturais, etc).

---

## 🚀 Instalação e Configuração

**1. Instale o plugin no seu Gemini CLI localmente:**
```bash
# Navegue até o diretório onde você clonou este repositório e rode:
gemini extensions install .
```

**2. Verifique se foi instalado corretamente:**
```bash
gemini extensions list
```
*(Você verá `migration-mythos` e suas respectivas skills na lista)*

---

## 🎯 Como Usar

No seu prompt diário utilizando o Gemini CLI em qualquer repositório, basta invocar a skill principal informando a origem e o destino:

> *"Ative a skill `migration-mythos`.*
> *Feature: Módulo de Faturamento*
> *Origem: /Users/eu/projetos/legado-delphi*
> *Destino: /Users/eu/projetos/novo-microsservico"*

O orquestrador assumirá o controle da conversa, chamará os agentes necessários e pedirá sua aprovação nos "Gates" críticos (como antes de iniciar a reescrita de código).

---

## ⚙️ Como Customizar e Evoluir o Plugin

O poder deste plugin está na facilidade de customização para a realidade da sua empresa. Se o seu legado for em `COBOL` ou o seu destino em `Golang`, veja como adaptar:

### 1. Customizando a Arqueologia e Linguagens (Scripts)
Se o seu repositório legado usa extensões ou linguagens proprietárias, você precisa informar o mapeador.
- **Arquivo:** `skills/migration-mythos/scripts/scan_repo.py`
- **O que alterar:** Adicione suas extensões de arquivo na variável `SUPPORTED_EXTENSIONS`. Exemplo:
  ```python
  SUPPORTED_EXTENSIONS = {
      "python": [".py"],
      "java": [".java"],
      "delphi": [".pas", ".dfm", ".dpr"], # <- Adicione linguagens legadas aqui!
  }
  ```

### 2. Customizando as Regras de Negócio e o Checklist (Prompts e Markdown)
Se a sua empresa possui padrões de QA ou segurança específicos (como não usar certos pacotes, ou obrigar relatórios de segurança do SonarQube).
- **Onde alterar:** Modifique o arquivo de checklist em `skills/migration-mythos/references/VERIFICATION_CHECKLIST.md`.
- O agente `@migration-validator` lê as regras diretamente desse arquivo. Tudo o que você colocar como `🔴 BLOQUEANTE` fará o agente rejeitar a migração caso não seja cumprido.

### 3. Ajustando os Padrões Arquiteturais (Markdown)
Na Fase 3, o Arquiteto escolhe um padrão de migração (Strangler Fig, ACL, etc).
- **Onde alterar:** Adicione os padrões de arquitetura internos da sua empresa em `skills/migration-mythos/references/MIGRATION_PATTERNS.md`.
- O `@migration-architect` vai considerar os seus guias para desenhar a arquitetura de destino.

### 4. Afinando a Personalidade dos Sub-Agentes (YAML/Markdown)
Você quer que o validador rode comandos específicos do seu ecossistema (ex: `npm run lint:custom` ou um script docker)?
- **Arquivo:** `agents/migration-validator.md`
- **O que alterar:** Edite os comandos na seção **Category F: Regression Testing**.

> ⚠️ **Atenção:** Se você alterar configurações no diretório raiz do repositório, lembre-se de rodar novamente o comando de instalação para que o Gemini CLI recarregue as mudanças:
> ```bash
> gemini extensions install .
> ```
