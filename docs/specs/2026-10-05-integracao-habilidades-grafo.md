# Integração local de habilidades e grafo de código

**Data:** 2026-10-05 · **Status:** aprovada pelo dono do projeto  
**Tier:** 2 · integração de ferramentas no harness local  
**Escopo:** somente o repositório `padroes-engenharia`; sem alterar a configuração global do harness.

## Problema

Graphify está instalado e tem hooks Git ativos, mas o harness de projeto não recebe sua skill, servidor MCP ou orientação automática de consulta. A skill `caveman` está instalada somente no diretório de outra ferramenta local. Antes de adicionar hooks ao harness, é preciso saber se instruções de skill e ferramentas MCP bastam para induzir consultas úteis ao grafo.

## Requisitos

1. Disponibilizar a skill `caveman` no caminho de skill de projeto `.agents/skills/caveman/`, preservando seu conteúdo e licença de origem.
2. Configurar o servidor MCP local do Graphify para servir `graphify-out/graph.json` ao harness sem habilitar ferramentas de escrita.
3. Instruir o agente, por skill de projeto, a consultar Graphify antes de buscas e leituras exploratórias de código quando a pergunta envolver arquitetura, fluxo ou impacto de mudanças. A resposta deve tratar resultados do grafo como pistas e confirmar fatos nos arquivos.
4. Testar em sessão nova, sem hooks do harness: as skills devem ser descobertas, a conexão MCP deve iniciar, e uma chamada à ferramenta de consulta deve retornar nós existentes do projeto.
5. Testar uma pergunta exploratória sem hooks e verificar se o harness consulta o MCP antes de ler ou buscar arquivos. Se não fizer isso de forma consistente, registrar a evidência e propor hook local compatível, sem instalá-lo silenciosamente.
6. Manter os hooks Git Graphify existentes (`post-commit` e `post-checkout`) para atualizar o grafo. Eles não substituem hooks do ciclo de ferramentas do harness.

## Critérios de aceite

- O harness reconhece `caveman` e Graphify como skills de projeto.
- O harness conecta ao MCP Graphify e conclui uma consulta ao grafo deste repositório.
- Sessão de teste sem hook de ferramenta demonstra a consulta prévia; caso contrário, a limitação e a decisão sobre hook ficam registradas antes de habilitá-lo.
- Nenhuma alteração em configuração global, `AGENTS.md`, constituição, ADR existente ou configuração de outra ferramenta local.
- `python scripts/validar.py` e `python scripts/gerar.py` terminam com código 0 se arquivos do portal forem alterados; para configuração local do harness, registrar a validação aplicável no plano.

## Impacto arquitetural

- Compose local: N/A.
- IaC: N/A.
- Diagrama e manifesto de arquitetura: N/A; o repositório não mantém esses artefatos.
- Configuração nova: arquivo local do harness e, se o teste exigir, arquivo local de hooks, carregados somente para este repositório confiável.

## Fora de escopo

- Instalar Graphify, atualizar sua versão ou reconstruir o grafo sem necessidade demonstrada.
- Alterar hooks globais do usuário, configuração de outra ferramenta local, MCP Docker ou permissões globais.
- Tornar a skill `caveman` ativa por padrão. O usuário a ativa explicitamente quando quiser.
- Habilitar hook de ferramenta antes do teste sem hooks ou sem evidência registrada de que as instruções e MCP não bastam.
- Publicar Graphify ou caveman no catálogo do portal.
