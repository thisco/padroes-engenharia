Trecho sanitizado de ADR, 2026-06-22. Lido em 2026-11-03 no commit fixado no registro de verificação; nomes de tabela, de arquivo, da organização e dos fornecedores retirados ou trocados por papéis.

# Configuração de classificação governada em banco, com histórico, como fonte única

## Contexto

A classificação dos itens dos catálogos dos fornecedores numa categoria canônica, e por ela num tipo, era feita de duas formas, ambas frágeis:

1. **De-para fixo no código dos extratores:** cerca de 250 linhas de mapeamento por identificador de item; cada serviço novo exigia um commit.
2. **Listas de regras em arquivos JSON** lidas pelo classificador: versionáveis, mas editáveis só por desenvolvedor, pelo Git.

A análise da planilha de gestão da organização e a reunião do dia estabeleceram que:

- A organização mantém uma **taxonomia canônica** curta, da ordem de uma dezena de categorias, **cada uma com um tipo fixo**.
- A classificação é **por categoria**, não por item: todo item herda o tipo da sua categoria.
- A própria organização precisa **editar essas regras** (incluir categoria, reassociar o de-para, ajustar o tipo) e também **o prompt do modelo**, pela interface, sem depender de deploy.

A meta é: **mudança de classificação = edição de dado, sem deploy**.

## Decisão

Centralizar **toda a configuração de classificação no banco**, com **versionamento SCD Type 2** (vigência de/até, ativo, autor e auditoria em cada linha), como **fonte única da verdade**. O pipeline (extrator → classificador → exportador) **lê do banco** em tempo de execução.

| Tabela (nome neutralizado) | Conteúdo |
|---|---|
| taxonomia canônica | nome da categoria, tipo, ativo |
| de-para | (fornecedor, categoria nativa) → categoria canônica, com status e origem (importação, manual, modelo) |
| regras determinísticas | regras por fornecedor (chave, alvo, peso) |
| prompt do modelo | prompt de sistema global e contexto por fornecedor, editáveis e versionados. **O contrato de saída (schema e enumeração) é validado em código, fora do prompt.** |

## Razões

| Critério | Banco com histórico (escolhido) | JSON gerado pela interface | No código (antes) |
|---|---|---|---|
| Edição pelo operador sem deploy | vale na próxima execução | exige publicar e deploy | exige commit |
| Fonte única, sem drift | sim | não (banco × arquivo) | — |
| Histórico, auditoria e rollback | nativo | pelo Git | pelo Git |

## Consequências

- O classificador passa a **derivar o tipo da categoria**, não do item.
- Na execução, a configuração ativa é lida uma vez por execução e guardada em memória.
- Todos os fornecedores usam o mesmo motor; as especificidades de cada um ficam em dados, não em código.
- O histórico nas configurações dá **reprodutibilidade**: é possível reprocessar um catálogo antigo com a configuração vigente naquela data.
