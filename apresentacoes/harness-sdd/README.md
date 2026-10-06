# Harness, SDD e o repositório como fonte de verdade

- **Audiência:** NUJOR, divisões de orçamentação e de execução de projetos, com a gerência
  do departamento na sala
- **Slides:** 19, cerca de 18 min de deck e 20 min de terminal ao vivo
- **Altitude:** dev, com gestor acompanhando

## Assunto

Como construir software com agentes de IA sem perder a arquitetura, e por que o processo
precisa sobreviver à troca de ferramenta. Parte de uma análise dos modelos de SDD existentes,
abre cinco harnesses de coding agent por dentro, e chega ao scaffold agnóstico e às seis
camadas que respondem à pergunta da regressão.

## Roteiro

Ver `roteiro.md`, que traz a fala sugerida por slide, os tempos, as perguntas prováveis e as
cinco coisas que não devem ser afirmadas em público, por serem lacunas declaradas da pesquisa.

## Arquivos

| Arquivo | Papel |
|---|---|
| `index.html` | deck, 19 slides |
| `roteiro.md` | fala por slide, perguntas prováveis, ressalvas |
| `tema.css` | tema próprio, a paleta carrega o argumento (ver abaixo) |
| `apresentacao.yml` | metadados da apresentação no portal |

## Dependências

**Roda 100% offline.** Nenhuma referência a CDN: reveal.js e as duas famílias tipográficas
vêm de `vendor/` do portal, referenciado como `../../vendor/`. A pasta só abre com o portal gerado
(ou com o `vendor/` do portal ao lado de `apresentacoes/`).

## Decisões de design

- **A paleta carrega a tese.** Azul institucional sólido marca o mecanismo que impede, que é
  código rodando fora do modelo. Âmbar tracejado marca o que orienta, que é texto dentro do
  modelo. A distinção do slide 7 vira o sistema visual e reaparece como régua vertical nos
  blocos.
- **Âncora no azul Gov.br**, a mesma paleta que a NUJOR usou no protótipo Panorama.
- **O tipo sinaliza o que você está olhando.** Grotesca pesada para a afirmação, JetBrains
  Mono para a evidência: caminho, schema, exit code, saída de terminal.
- **Numeração só onde o conteúdo é sequência**, ou seja, nas camadas e nos passos de brownfield.
- **Uma única animação** no deck inteiro, a linha de fronteira que se desenha no slide 7. Ela
  respeita `prefers-reduced-motion`.

## Procedência do conteúdo

A pesquisa de internos dos cinco harnesses está em
`serpro-cloud-ia-governance/docs/research/harness-internals/`, um documento por harness com
cada afirmação marcada por origem (`[verificado]`, `[doc oficial]`, `[inferido]`) e as
lacunas declaradas, mais `00-matriz-comparativa.md`.

O estudo do DeepSeek dsh é anterior:
`llama-lab/docs/estudo-harnesses-2026-09-10.md`.

O scaffold e a skill apresentados são `repos/sdd-scaffold` e `repos/sdd-lifecycle`.

## Estado

Deck alinhado ao sdd-scaffold 1.7.1 e à sdd-lifecycle 3.0.0 (atualizado em 2026-10-06): quatro
camadas implementadas, quatro skills e quatro pontos de montagem (`.claude`, `.codex`, `.kiro`,
`.agents`). O slide 14 conta a auditoria (três controles com teste verde que não disparavam, já
corrigidos) e a revisão de segurança do 1.7.1; Kiro e
Codex seguem não confirmados contra o produto, e o deck diz isso. O slide 15 traz o teste da
constituição sem skills, que fez as skills entrarem por reuso e não por correção.
