Trecho sanitizado de spec, 2026-06-10.

# Evolução Arquitetural do Workflow SDD e Memória Contínua

## 2. Requisitos e Regras (AGENTS.md)

### 2.1 O "Feedback Loop" do SDD
Especificações são a fonte da verdade. Se, durante a Fase de Implementação, o subagente desenvolvedor identificar um bloqueio técnico que inviabilize a implementação da especificação atual de forma segura e coerente:
- O uso de "gambiarras" (workarounds estruturais) é **proibido**.
- A implementação deve ser **interrompida**.
- O fluxo retorna à Fase 1 (Especificação). A especificação deve ser atualizada e re-aprovada pelo usuário, gerando subsequentemente um novo plano antes da retomada do código.

### 2.2 Memória Contínua de Projeto (Project Memory)
- É introduzido o arquivo `docs/PROJECT_MEMORY.md` (Memória Contínua).
- O `AGENTS.md` exigirá que **toda sessão de agente inicie lendo este arquivo**.
- Ao final de tarefas complexas, o agente responsável **deve atualizar** o `PROJECT_MEMORY.md` adicionando os novos aprendizados de forma concisa.

## 3. Orquestração do `sdd-lifecycle` (SKILL.md)

### 3.1 Fase 1.5 - Gatekeeper de Arquitetura e Contratos
Logo após a aprovação humana da especificação e *antes* da geração do plano de implementação, o fluxo SDD deve invocar um checkpoint:
- Invocar a skill `doubt-driven-development` para identificar quebras de contrato (esquema de DB ou contratos de API).
- Se houver alterações destrutivas sem aprovação prévia, invocar `documentation-and-adrs` para rascunhar a ADR.
- Pausar o fluxo e solicitar a aprovação humana da ADR.
