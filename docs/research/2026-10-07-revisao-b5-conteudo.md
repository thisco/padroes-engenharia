# Revisão de produto de conteúdo da fase B.5

**Data:** 2026-10-07 · **Alvo:** portal servido em http://localhost:8000 (build da branch `feat/2026-10-01-portal-fase-a`, commit 0ccf67e) · **Papel:** revisor independente, em sessão nova, no lugar de quem entrega com IA amanhã e de um agente que lê `llms.txt`.

**Escopo e limites.** Li o portal servido (HTML e `.md` gêmeos, `llms.txt`, `roteamento.json`, `catalogo.json`) e rodei os Exemplos da fonte com o Python de `padroes-engenharia/.venv`. Não li `docs/plans/`. Não alterei nada além deste relatório e não apaguei nada. Nenhum container `rev-` foi necessário. O que **não** executei:

- o guia "Do zero à primeira MR", porque a execução do passo 1 (clone da tag do scaffold, ambiente virtual e `pip install`) foi negada pelo classificador de permissões da sessão. O guia foi lido de ponta a ponta, sem rodar;
- as receitas com Docker, `npx gitlab-ci-local` ou o gateway de IA (sobem imagens e executam código de terceiros);
- o roteiro de DAD-01, que é piloto e estava fora do escopo.

Para o ARQ-03, que exige `import-linter` (ausente no `.venv` indicado), criei um ambiente descartável em `/tmp/rev-venv` a partir do mesmo Python.

## 0. Os seis critérios

Os critérios da revisão de 2026-10-02 não estão nomeados em `docs/specs/2026-10-02-portal-v1-1-delta.md` nem em `docs/research/`. O §1 do delta rotula só três notas: "práticas aplicáveis 4/10", "caminho do zero 1/10" e "catálogo de ferramentas 2/10" (mais "frontend 4,5/10" e "Conceitos 2,5/10", que são de design, fora deste escopo). **Defini, portanto, seis critérios equivalentes**: utilidade, evidência, executabilidade, cobertura do §10, clareza e consistência. A coluna "antes" usa as três notas rotuladas, ligadas ao critério mais próximo. As três restantes (5, 2 e 2, na ordem em que foram informadas) não têm rótulo em lugar nenhum; atribuí-as por ordem a evidência, clareza e consistência, e essa atribuição é incerta.

## 1. Notas

| Critério | Antes (2026-10-02) | Agora | Justificativa |
|---|---|---|---|
| Utilidade | 4 (práticas aplicáveis) | **8** | Toda prática tem Exemplo com antes e depois, regra pronta para o `AGENTS.md` e prompt para o agente; 48 de 48 trazem exemplos em `exemplos/`. Seis pontos de entrada servem a quem está no meio de uma mudança (home por momento, espinha, domínio). Perde pontos por páginas longas (OBS-01 e API-01 passam de 2,7 mil e 3,7 mil palavras) e pelo "antes" que às vezes não existe como arquivo (LGPD-01). |
| Evidência | 5 (sem rótulo) | **9** | 20 afirmações com `[ref:]` conferidas na fonte, em 12 páginas: 20 de 20 estão lá (seção 6). 170 referências `[V]` e 2 `[S]`; a única fonte secundária relevante (portaria citada em Pessoas e normas) é declarada como `[S]` e o texto avisa que a norma não foi lida na origem. Não achei afirmação sem lastro. |
| Executabilidade | 1 (caminho do zero) | **8** | Três Exemplos pedidos mais três extras reproduzem a saída da página (seção 2). Os roteiros dos pilotos e as receitas citam comandos reais, limite de espera e "Se der errado". Perde pontos pelo marcador de inclusão que vaza numa receita (M1), pelo guia com lacunas de branch e de arquivos provisórios (M2), pelo layout de pastas não dito no ARQ-03 (M3) e pelo `{URL do portal}` que o leitor tem de trocar à mão em 87 pontos de 11 páginas. |
| Cobertura do §10 | 2 (catálogo de ferramentas) | **7** | Todos os mínimos de faixa estão cumpridos, mas exatamente no mínimo: 48 práticas contra mínimo 48 e meta 55 (seção 4). 8 receitas, 4 guias, 2 starters, 6 skills, 15 conceitos, 14 ferramentas, glossário com 32 termos e Pessoas e normas com as 5 normas estão publicados. Falta `pytest-bdd` no radar, há 1 só caso, e 15 das 48 células seguem "a definir", sem dizer o que falta (M6). |
| Clareza | 2 (sem rótulo) | **7** | A home explica o que é o portal, para quem e como ler força e momento (contagens 17, 14, 11 e 6 batem com o catálogo). O texto é direto e honesto sobre limites ("não prova que o log está livre de dado pessoal"). Perde pontos pelo tamanho das páginas, com o verificador inteiro embutido em "Como verificar", e por "a definir" sem nenhuma explicação. |
| Consistência | 2 (sem rótulo) | **8** | Contagens batem entre home, espinha, roteamento, `llms.txt` e catálogo (48 práticas, 15 células vazias, 8 receitas, 4 guias). Nenhum link interno quebrado em 128 páginas e 464 links. Hashes de mecanismo conferem com a tag. Desvios pequenos: commit do `llms.txt`, domínios do gitleaks, vocabulário "orienta" contra "só orienta" (baixos). |

## 2. Teste "consigo aplicar amanhã?": Exemplos rodados

Faixas e práticas escolhidas, todas fora das pilotos: Observabilidade (OBS-01), Privacidade e LGPD (LGPD-02) e Arquitetura (ARQ-03). Rodei também SEG-01, LGPD-01 e API-01/API-02 como conferência extra.

| Prática | Estado | Comando | Saída | Bate com a página? |
|---|---|---|---|---|
| OBS-01 | antes | `emitir-logs-antes.py > a.jsonl; verificar-log.py a.jsonl` | saída 1, 13 linhas de achados (timestamp, nivel, request_id, payload, CPF, e-mail) e `3 de 3 linhas fora do padrão` | Sim, linha a linha igual ao bloco da página |
| OBS-01 | depois | `emitir-logs.py > d.jsonl; verificar-log.py d.jsonl` | saída 0, `3 linhas, todas com os campos obrigatórios e sem dado pessoal`; as 3 linhas com o mesmo `request_id` | Sim. `duracao_ms` deu 0 contra 282 do exemplo estático; a página já avisa que hora e id mudam |
| OBS-01 | arquivos estáticos | `verificar-log.py log-exemplo-ruim.jsonl` / `log-exemplo.jsonl` | saída 1 com 7 achados e saída 0 | Sim |
| OBS-01 | verificador inline | diff do script da página contra `exemplos/OBS-01/verificar-log.py` | idêntico | Sim |
| LGPD-02 | antes | `verificar-dado-em-claro.py --raiz antes` | saída 1; CPF e e-mail em claro em `tests/fixtures/cliente.json:1`, `logs/atendimento.log:1` e `prompts/segunda-via.txt:1`; sem imprimir o dado | Sim, idêntico |
| LGPD-02 | depois | `... --raiz depois` | saída 0, `4 arquivos varridos, nenhum CPF ou e-mail em claro`; o protocolo de 11 dígitos não é acusado | Sim, idêntico |
| LGPD-02 | verificador inline | diff contra o arquivo | idêntico | Sim |
| ARQ-03 | antes | montei `boletos/{dominio,aplicacao,adaptadores}` com `dominio-antes.py` e `verificar-camadas.py` (import-linter 2.15) | saída 1; `O dominio nao importa framework nem banco BROKEN`; `boletos.dominio.boleto -> flask (l.6)` e `-> sqlalchemy (l.7)` | Sim, idêntico |
| ARQ-03 | depois | idem, com `dominio.py` | saída 0; `2 contratos cumpridos` | Sim |
| SEG-01 (extra) | antes e depois | `verificar-threat-model.py spec-antes.md` / `spec.md` | saída 1 com 4 problemas e saída 0 | Sim |
| LGPD-01 (extra) | antes e depois | cópia de `dados.md` sem as 3 linhas, depois o original | saída 1 com os 3 campos e saída 0 com 5 campos | Sim (o "antes" teve de ser montado à mão) |
| API-01 e API-02 (extra) | receita de contrato | `comparar-contratos.py` com `proposta-sem-versao`, `proposta-compativel`; `unittest` do teste de contrato com contrato que exige `email` | saída 1 com 2 incompatíveis; saída 0 com 3 compatíveis; teste passa e depois falha como a receita mostra | Sim |

Veredito: **os Exemplos reproduzem**. Nenhum Exemplo rodado falhou em reproduzir o que a página mostra. O atrito que sobra está em montar o cenário (M3, M4), não na saída.

## 3. Receitas e guia lidos de ponta a ponta

Lidos como quem vai seguir: receita "Publicar um contrato OpenAPI versionado com teste no CI", receita "Ligar uma aplicação ao gateway de IA" e guia "Do zero à primeira MR com IA".

**Receita de contrato OpenAPI.** Seguível. Confirmei que todos os arquivos que ela manda baixar existem no portal (`exemplos/API-01/*`, `exemplos/API-02/*`, `executar.sh`) e que o verificador e o teste dão as saídas do "Confira". Onde trava:
- `{URL do portal}` em cada `curl`: o leitor precisa trocar à mão; a página não sabe o próprio endereço (M7).
- Passo 4: o `curl -o .gitlab-ci.yml` **sobrescreve** o pipeline que o projeto já tem, embora o texto diga "ou acrescente-o ao que já existe" (M7).
- Passos 6 e 7 pedem Docker, Node e papel de Maintainer; está dito em "Pré-requisitos", então é só aviso.

**Receita do gateway de IA.** Trava concreta no passo 3: o marcador `<!-- incluir: exemplos/P2-01/cliente.py -->` aparece como texto visível, no HTML (`<p>&lt;!-- incluir: ... --&gt;</p>`) e no `.md` (único marcador solto nas 122 páginas `.md` do `llms.txt`). O código do cliente, que o passo manda "ler a URL e a chave do ambiente", não está na página; só no link da seção Exemplos (M1). O resto é bem amarrado: confere porta e nomes de contêiner antes de subir, dá limite de espera, explica a ordem 403 antes do orçamento e registra o código HTTP que muda com a versão. Não executei (sobe o gateway com Docker e clona repositório de terceiros).

**Guia "Do zero à primeira MR".** Bem escrito, com saídas reais, mas **só lido**. Onde travaria quem segue:
- O passo 3 (Tier 2) nunca manda criar a branch da mudança; o passo 4 termina com "traga a `main` para a branch do CPF", uma branch que não existe no texto (M2).
- O passo 2 diz "Faça o merge" sem o comando (o `git merge --no-ff` só aparece no fim, em "O que a execução não cobriu") (M2).
- O passo 3.4 depende de um `app/pedidos.py` "provisório", do PRD e do plano de Tier 2 que o guia descreve em prosa e não mostra (M2).
- O passo 1 manda criar `app/__init__.py`, `app/precos.py` e a migration, mas o `.gitignore` do `.gitlab-ci-local/` e o `pytest` fora do `requirements.txt` ficam por conta do leitor, ambos avisados no texto; ok.
- O guia diz com franqueza que foi uma execução sem agente e que a revisão independente foi feita pelo mesmo executor (§6.1). Isso é correto, mas quem quer "com agente" não tem um passo a passo equivalente.

## 4. Cobertura do §10 contra o publicado

| Item do §10 / delta | Mínimo | Publicado | Estado |
|---|---|---|---|
| Construir com IA | 10 | 10 (P1-01, P1-03 a P1-11) | cumprido no mínimo |
| Arquitetura | 4 | 4 | cumprido |
| Contratos de API, Frontend e UX, Observabilidade | 2 cada | 2 cada | cumprido |
| Dados e migrations, Privacidade e LGPD | 2 cada | 2 cada | cumprido |
| Qualidade e BDD, Infra e IaC, CI/CD, Segurança | 3 cada | 3 cada | cumprido |
| IA no produto | 12 (P2 ≥ 6, P3 ≥ 6) | 12 (P2-01 a P2-06, P3-01 a P3-06) | cumprido |
| Total | 48 mínimo, meta 55 | **48** | mínimo, meta não atingida |
| Guias | 4 | 4 (Do zero a MR, Instanciar scaffold, Brownfield em 5 passos, Escolher harness) | cumprido |
| Receitas | ≥ 8, uma por grupo de faixas e 4 obrigatórias | 8 | cumprido (grupos Guia, Desenho, Dados, Entrega e operação e IA no produto cobertos; as 4 obrigatórias presentes) |
| Starters | 2 | 2 (`sdd-scaffold`, `gateway-poc`) | cumprido |
| Skills | 6 | 6 em `.well-known/skills` | cumprido |
| Conceitos | 9 + 6 peças | 15 | cumprido |
| Casos | 1 (avaliação do gateway) | 1; números conferidos contra a matriz (45 casos, 42 passam, 3 falha ou gap) | cumprido |
| Radar | ~12 ferramentas, incluindo `pytest-bdd` | 14; **sem `pytest-bdd`** | quase |
| Glossário | termos dos dois ninhos e da espinha | 32 termos | cumprido |
| Pessoas e normas | 5 normas | 5, com práticas mapeadas e lacunas nomeadas (NIST e ISO 42001 sem prática) | cumprido |
| Backlog "a definir" | formar o backlog público | 15 de 48 células, só como contagem | **fraco**: não diz o que falta em cada célula (M6) |

Células vazias por domínio (da espinha): Arquitetura (depois da entrega), Contratos de API (enquanto escreve e depois), Frontend e UX (antes do merge e depois), Dados (antes de escrever e depois), Privacidade (antes do merge e depois), Qualidade (antes de escrever), Infra (enquanto escreve), CI/CD (antes de escrever), Observabilidade (antes de escrever e antes do merge), Segurança (depois da entrega). Total 15, o que bate com a home e com `roteamento.json`.

## 5. Leitura como agente: `llms.txt` e `catalogo.json`

Tarefa de teste: "vou criar uma migration".

- `grep -i migration llms.txt` devolve em uma passada: DAD-01, DAD-02, a receita "Adicionar uma migration corretiva", as ferramentas Alembic e Flyway e a skill `migrations-reversiveis` (com a descrição "Use quando a mudança alterar o esquema do banco..."). Para um agente que busca por texto, **dá para achar**.
- Pelo caminho oficial (`roteamento.json`): domínio `dados-migrations` e momento `enquanto-escreve` devolvem DAD-02 com `links.aplica` (URL da skill), `links.receitas` (a receita certa) e `links.ferramentas` (Flyway e Alembic). `catalogo.json` repete a ligação prática-receita e dá `resumo` por prática. A estrutura é boa e consistente, e os 56 prompts são indexados por prática e momento.
- Onde o agente tropeça (M5):
  1. Não há índice por tarefa ou palavra-chave. O agente só chega a `dados-migrations` se inferir o domínio pelo título da faixa.
  2. O bloco do `AGENTS.md` manda consultar o roteamento "no início (fase 0) e antes de abrir a MR (fase 7)". A célula de Dados em "antes de escrever" é **a definir**, e DAD-02 mora em "enquanto escreve" (fases 4 a 6), que o bloco não manda consultar. Seguindo o texto ao pé da letra, o agente acha nada na fase 0 e só DAD-01 na fase 7.
  3. As linhas de prática no `llms.txt` trazem título, força, status, domínio e momento, mas não o `resumo`; para decidir, o agente precisa abrir cada `.md`.
  4. Pequeno: o JSON diz `forca: "orienta"` e o `.md` e a UI dizem "só orienta".

## 6. Amostra de 20 afirmações com `[ref:]` contra a fonte

Abri a fonte (web, no endereço do registro em `referencias/`; repositórios internos no commit fixado). Todas confirmam o que a página afirma.

| # | Página | Afirmação | Fonte | Resultado |
|---|---|---|---|---|
| 1 | OBS-02 | SLO e orçamento de erro "acompanhado diária ou semanalmente" | SRE book, cap. de SLOs | Confere, texto quase literal |
| 2 | OBS-02 | monitorar o sintoma, não a causa; toda página acionável | SRE book, cap. de monitoramento | Confere |
| 3 | SEG-03 | modo de hash do pip: `--require-hashes`, requisitos fixados com `==`, URL ou caminho | documentação do pip, instalação segura | Confere |
| 4 | SEG-03 | `GET /pypi/<projeto>/json` e `GET /pypi/<projeto>/<versão>/json` | documentação da API JSON do PyPI | Confere |
| 5 | IAC-02 | `tofu plan -out`, `tofu show -json` sobre plano salvo, `resource_changes` com `change.actions` | docs do OpenTofu (plan, show, formato JSON) | Confere (a chave `resource_changes` está na página de formato JSON, citada ao lado) |
| 6 | CICD-03 | `BREAKING CHANGE:` ou `!` correspondem a MAJOR | Conventional Commits 1.0.0 | Confere |
| 7 | ARQ-04 | suporte a C4 no Mermaid é experimental e a sintaxe pode mudar | docs do Mermaid | Confere |
| 8 | QLD-03 | pytest sai com 5 se nenhum teste foi coletado; `ruff check` sai com 1 se há violação | docs do pytest e do Ruff | Confere |
| 9 | UX-01 | estado vazio com três usos (status do sistema, pistas de aprendizado, caminho direto) | Nielsen Norman Group | Confere |
| 10 | UX-01 | WCAG 2.2 critério 3.3.3: sugestões de correção quando conhecidas | W3C, Understanding 3.3.3 | Confere |
| 11 | P3-04 | aprovação humana para ação de alto risco entre as mitigações de injeção de prompt | OWASP LLM01 | Confere ("Require human approval for high-risk actions") |
| 12 | P3-04 | redigir documento sem enviar, ler e buscar sem apagar | guia de segurança do fornecedor | Confere, quase literal |
| 13 | API-02 | `GIT_DEPTH: "0"` desliga o clone raso e o `.gitlab-ci.yml` sobrescreve a configuração | docs do GitLab, configurações de pipeline | Confere ("keep empty or set to 0"; "can be overridden by the GIT_DEPTH variable") |
| 14 | CICD-03 | `if: $CI_COMMIT_TAG` como regra de job | docs do GitLab, job rules | Confere |
| 15 | DAD-01 | `flyway validate` falha com checksum, nome ou tipo diferentes | docs do Flyway | Confere |
| 16 | Pessoas e normas | quem constrói decide "cerca de 70%" do planejamento e "20%" da execução | estudo de sessões de agente de código | Confere ("people make about 70% of the planning decisions but only 20% of the execution decisions") |
| 17 | LGPD-02 | o detector trocou "autorizada" por `<LOCATION>` na resposta | cenário 02 da avaliação do gateway | Confere (linha de evidência TC) |
| 18 | LGPD-02 | chave sem permissão de vector store leu o store inteiro | cenário 04 da avaliação, VS-05 | Confere (3 regras, igual à master key) |
| 19 | Caso do gateway | 45 casos, 42 passam, GR-04, SK-03 e TI-01 em falha ou gap | matriz consolidada | Confere (45 linhas na matriz) |
| 20 | P1-09 e P1-01 | revisão por sessão independente com contexto novo e modelo potente; Tier 1 até cerca de 3 arquivos | skill `sdd-lifecycle` no commit citado | Confere |

Complemento: o hash `616cc4c2...` de `verificar_pr.py` citado em DAD-01 é o do arquivo hospedado no portal e o do arquivo na tag v1.7.1.

## 7. Achados por severidade

Contagem: **alto 0 · médio 7 · baixo 8**.

### Alto (conteúdo errado, Exemplo que não reproduz, afirmação sem a fonte dizer aquilo)

Nenhum. Os seis Exemplos rodados reproduzem, as 20 afirmações conferidas estão na fonte, e não vi número ou comando errado nas páginas lidas. Ressalva: o guia e as receitas com Docker não foram executados por mim (ver "Escopo e limites"), então "nenhum alto" vale para o que li e rodei.

### Médio (trava quem segue)

- **M1. Marcador de inclusão vaza na receita do gateway.** `receitas/ligar-aplicacao-ao-gateway`, passo 3: `<!-- incluir: exemplos/P2-01/cliente.py -->` sai como texto no HTML e no `.md`, e o código do cliente não aparece no passo. Provável causa: o marcador está dentro de item de lista numerada (recuado), onde o expansor não o reconhece. Único caso nas 128 páginas.
- **M2. Guia "Do zero à primeira MR" tem lacunas para quem segue à mão.** Branch da mudança de Tier 2 nunca criada (e depois referida como "a branch do CPF"); "faça o merge" sem comando; `app/pedidos.py` provisório, PRD e plano de Tier 2 descritos e não mostrados.
- **M3. ARQ-03 não diz como montar as pastas.** Os arquivos do Exemplo têm nomes com hífen (`dominio.py`, `repositorio-sql.py`) e o `importlinter.ini` espera `boletos.dominio.boleto`, `boletos.aplicacao.portas` e `boletos.adaptadores.repositorio_sql`. O leitor deduz o mapa pelos `import`. Falta uma árvore de diretórios de três linhas.
- **M4. Receitas copiam `{URL do portal}` em 87 pontos de 11 páginas, e a do contrato sobrescreve `.gitlab-ci.yml`.** O leitor troca o endereço à mão a cada `curl`; o passo 4 da receita de contrato destrói um pipeline existente apesar de o texto dizer "acrescente". Sugestão: uma variável de shell no topo (`PORTAL=...`) e um `curl` para um nome temporário seguido de `cat >>`.
- **M5. Roteamento para agente é frágil no momento de decidir.** Sem índice por tarefa; o bloco do `AGENTS.md` só manda consultar nas fases 0 e 7; a célula de Dados em "antes de escrever" é vazia, e DAD-02 (enquanto escreve) fica fora da consulta mandada; as linhas do `llms.txt` não trazem o `resumo`.
- **M6. O backlog "a definir" é só uma contagem.** 15 células sem nenhuma indicação do que entraria nelas, quem decide ou quando; o §10 pede que formem "o backlog público". A espinha mostra hachura e a página de domínio mostra "a definir", sem lacuna nomeada como o delta pede para os estados vazios.
- **M7. LGPD-01 não entrega o estado "antes".** O "antes" é um `dados.md` com só 2 linhas num "projeto-modelo" que não existe em `exemplos/LGPD-01/`; o leitor remonta o cenário (consegui, apagando 3 linhas, e a saída bate).

### Baixo (texto)

- **B1.** O commit do `llms.txt` e do `catalogo.json` é `d6af4d6`, e o build servido é `0ccf67e` (a diferença entre os dois é só changelog, README e plano).
- **B2.** A ferramenta gitleaks lista "Dados e migrations, CI/CD" como domínios e não lista Segurança, onde mora SEG-02.
- **B3.** O radar não traz `pytest-bdd`, que o delta pede.
- **B4.** 48 práticas é o mínimo do §10; a meta de 55 não foi atingida e a página não diz isso.
- **B5.** Páginas muito longas: OBS-01 (2,7 mil palavras) e API-01 (3,7 mil) embutem o verificador inteiro em "Como verificar". Um link para o arquivo bastaria para as pessoas, e o agente tem o `.md`.
- **B6.** Vocabulário de força diverge: `orienta` no JSON, "só orienta" na UI e no `.md`.
- **B7.** OBS-01 mostra `duracao_ms: 282` no log de exemplo; a execução real dá 0 a 3 ms. A página só avisa que hora e id mudam.
- **B8.** A página Pessoas e normas diz que o PL 2338 "estava em tramitação em 2026-10-06" e a portaria depende de uma notícia; ambos estão datados e declarados, mas envelhecem rápido e não têm data de revisão própria na página.

## 8. Corrigir antes do merge (só os altos)

Nenhum alto. Recomendação extra, fora da regra "só os altos": M1 é correção de uma linha (recuo do marcador ou expansão dentro de lista) e vale entrar no mesmo merge, porque é a única falha visível a quem abre a página.
