---
id: IAC-02
titulo: Infra declarada em código, com o plano de mudança revisado no PR
dominio: infra-iac
subdominio: null
momento: antes-do-merge
forca: orienta
mecanismo: null
status: experimentar
aplica: []
referencias: [sdd-scaffold-infra-devops, opentofu-plan, opentofu-show, opentofu-json-format, opentofu-dependency-lock]
relacionadas: [IAC-01, IAC-03]
dono: engenharia
revisado_em: 2026-10-07
revisar_ate: 2027-04-07
resumo: "A infra vive em código versionado, e todo PR que a muda traz o plano gerado, com a destruição de recurso decidida por uma pessoa."
ferramentas_aprovadas: []
exemplos:
  - exemplos/IAC-02/executar.sh
  - exemplos/IAC-02/modulo-antes/main.tf
  - exemplos/IAC-02/modulo-base/.terraform.lock.hcl
  - exemplos/IAC-02/modulo-base/main.tf
  - exemplos/IAC-02/modulo-depois/main.tf
  - exemplos/IAC-02/verificar-plano.py
---

## O que fazer

Declare a infraestrutura em arquivos versionados e só a altere por pull request que traga o plano
da mudança, gerado pela própria ferramenta. A prática tem três partes.

1. **A infra é código.** Os recursos ficam em arquivos de OpenTofu (ou Terraform) no repositório, e
   a mudança passa pelo mesmo PR que o código. O modelo de steering do scaffold pede registrar, nas
   normas de deploy, a proibição de operações manuais fora do CI/CD, por causa da perda de
   rastreabilidade [ref:sdd-scaffold-infra-devops].
2. **O plano acompanha o PR.** O `tofu plan` cria um plano de execução que mostra o que a
   ferramenta pretende mudar na infraestrutura [ref:opentofu-plan]. Com `-out`, o plano é gravado
   num arquivo que depois pode ser passado ao `tofu apply`, o que serve às automações
   [ref:opentofu-plan]: quem revisa vê o plano, e quem aplica aplica esse mesmo plano. O texto do
   plano (`tofu show`) vai para a descrição do PR.
3. **Destruição é decisão de pessoa.** O `tofu show -json` sobre um plano salvo devolve o plano em
   JSON [ref:opentofu-show], e cada item de `resource_changes` traz as ações previstas em
   `change.actions`; a substituição aparece como `["delete", "create"]`, ou seja, o objeto é
   destruído e recriado em vez de alterado no lugar [ref:opentofu-json-format]. Um verificador
   sobre esse JSON reprova o plano que destrói um recurso que ninguém aprovou na revisão.

## Como aparece quando falta

A infra é mexida à mão, no console ou por um comando solto, e o repositório deixa de descrever o que
existe: ninguém sabe quem mudou o quê, que é a perda de rastreabilidade que o modelo de steering do
scaffold quer evitar [ref:sdd-scaffold-infra-devops]. O mesmo steering lembra de outro sintoma:
atualizações automáticas da nuvem geram falso diff no código declarado, e por isso o plano precisa
ser lido a cada mudança, e não só conferido uma vez [ref:sdd-scaffold-infra-devops].

O defeito mais caro é a destruição escondida. No Exemplo, renomear o arquivo de configuração
parece uma edição de uma linha, mas o plano mostra `must be replaced`: o recurso é destruído e
recriado. Quem aprova o PR só pelo diff do código não vê isso; quem lê o plano vê.

## Como aplicar

1. Escreva a infra em arquivos `.tf` num diretório do repositório, com a versão do provider
   restringida. Rode `tofu init` e versione o `.terraform.lock.hcl`: a documentação recomenda
   incluí-lo no repositório para discutir, em revisão de código, as mudanças nas dependências
   externas [ref:opentofu-dependency-lock].
2. A cada mudança, rode `tofu fmt -check`, `tofu validate` e
   `tofu plan -out=plano.bin` [ref:opentofu-plan].
3. Gere o texto (`tofu show -no-color plano.bin`) e o JSON (`tofu show -json plano.bin`)
   [ref:opentofu-show]. Cole o resumo do texto na descrição do PR e passe o JSON ao verificador.
4. Se o verificador reprovar por destruição, primeiro tente uma mudança que não destrua (acrescente
   um recurso novo em vez de renomear). Se a destruição é mesmo o desejado, a pessoa que revisa
   registra a aprovação no PR, listando o endereço do recurso, e o verificador lê essa lista.
5. Aplique só o plano revisado: `tofu apply plano.bin` [ref:opentofu-plan], e não um plano novo.
   Se a infra mudou entre o plano e a aplicação, gere o plano de novo e revise de novo.
6. Os recursos que o plano destrói e que guardam dado têm rollback declarado antes da aplicação
   (IAC-03).

## Exemplo

### Antes e depois

O Exemplo usa um módulo mínimo do OpenTofu com o provider `local` (que grava arquivos), para que
o plano seja real e não toque em nenhuma nuvem. O estado atual declara um arquivo de configuração:

<!-- incluir: exemplos/IAC-02/modulo-base/main.tf -->

Antes: a mudança troca o nome do arquivo, `saida/config-` por `saida/app-`:

<!-- incluir: exemplos/IAC-02/modulo-antes/main.tf -->

O plano mostra a substituição, e o verificador reprova (saída 1). Saída da execução da curadoria
com o OpenTofu v1.13.1 e o provider `hashicorp/local` v2.9.1:

```text
--- plano.txt, o que vai para a descrição do PR:
  # local_file.config must be replaced
Plan: 1 to add, 0 to change, 1 to destroy.
local_file.config: será destruído (delete+create) sem aprovação
IAC-02: 1 destruição(ões) sem aprovação (1 delete+create).
saída: 1
```

Se a destruição é o desejado e a pessoa que revisa a aprovou no PR (a lista com
`local_file.config`), o mesmo plano passa:

```text
IAC-02: plano sem destruição não aprovada (1 delete+create).
saída: 0
```

Depois: a mudança só acrescenta um recurso, e o plano só cria:

<!-- incluir: exemplos/IAC-02/modulo-depois/main.tf -->

```text
--- plano.txt, o que vai para a descrição do PR:
  # local_file.versao will be created
Plan: 1 to add, 0 to change, 0 to destroy.
IAC-02: plano sem destruição não aprovada (1 create, 1 no-op).
saída: 0
```

O verificador e o roteiro completo, que roda `tofu init`, `validate`, `fmt -check` e `apply` do
estado atual num diretório temporário (o `init` baixa o provider do registro do OpenTofu), e
depois gera e confere os três planos:

<!-- incluir: exemplos/IAC-02/verificar-plano.py -->

<!-- incluir: exemplos/IAC-02/executar.sh -->

O `.terraform.lock.hcl` do módulo base, que fixa o provider e vai para o repositório:

<!-- incluir: exemplos/IAC-02/modulo-base/.terraform.lock.hcl -->

### Para o agente

Regra curta para o `AGENTS.md` do projeto:

```markdown
Infra só muda por PR com o plano. Rode tofu fmt -check, tofu validate e tofu plan -out, cole o
resumo do plano na descrição do PR e passe o JSON ao scripts/verificar-plano.py. Nunca aprove você
mesmo a destruição de um recurso: se o plano destrói, refaça a mudança sem destruir ou pare e
relate. Aplique só o plano revisado.
```

Prompt para fazer uma mudança de infra com o plano revisado:

```prompt
Aplique a prática IAC-02 do portal de padrões de engenharia a esta mudança de infra: {mudança}.
Use um único shell ou refaça as variáveis a cada comando. O módulo do OpenTofu fica em infra/ e
não há remoto: use a branch local main.

1. Crie a branch feat/AAAA-MM-DD-<nome-curto> a partir da main, com a data de hoje. Traga o
   ambiente ao estado do código atual: cd infra && tofu init -input=false && tofu apply
   -input=false -auto-approve. Mostre a saída.
2. Edite só os arquivos .tf de infra/ para fazer a mudança. Não edite scripts/verificar-plano.py.
3. Dentro de infra/, rode e mostre a saída de cada comando: tofu fmt -check, tofu validate e
   tofu plan -input=false -no-color -out=plano.bin. Depois gere tofu show -no-color plano.bin >
   plano.txt e tofu show -json plano.bin > plano.json, e rode
   python3 ../scripts/verificar-plano.py plano.json. A saída precisa ser 0.
4. Se o verificador reprovar por destruição, não crie arquivo de aprovação e não altere o
   verificador: refaça a mudança sem destruir nenhum recurso. Se isso for impossível, pare e
   relate.
5. Crie PR.md na raiz com o título da mudança e, num bloco de texto, as linhas do plano.txt que
   começam por "  #" e a linha que começa por "Plan:". Aplique o plano revisado com
   tofu apply -input=false plano.bin e mostre a saída.
6. Faça um commit só com os arquivos .tf alterados, o .terraform.lock.hcl (se mudou) e o PR.md (não
   adicione plano.bin, plano.txt, plano.json, estado nem a pasta .terraform), com a mensagem
   "feat(infra): <resumo da mudança> (IAC-02)", sem linha de coautoria nem trailer.
```

Antes de rodar, o repositório precisa ter o `tofu` instalado, o módulo em `infra/` (com o
`.terraform.lock.hcl`) e o `scripts/verificar-plano.py` do portal, já commitados na `main`, e um
`.gitignore` para o estado, a pasta `.terraform` e os arquivos do plano.

## Como verificar

Não há mecanismo hospedado pelo portal, e por isso a força é `orienta`. O verificador candidato é o
`verificar-plano.py` do Exemplo, que roda no CI sobre o JSON do plano. Ele reprova (saída 1) o
arquivo ausente, vazio ou que não é um plano em JSON e o recurso com ação `delete` (a substituição
inclusa) que não esteja na lista de aprovações; o arquivo de aprovações informado e ausente também
reprova.

Os limites: o verificador não lê o significado da mudança. Ele não sabe se um `update` no lugar
causa interrupção, se um recurso novo custa caro ou se uma regra de rede ficou aberta demais. A
lista de aprovações é um arquivo de texto, e o portal não verifica quem a escreveu; a trava vale se
a revisão do PR a trata como decisão de pessoa. O plano é o retrato do momento em que foi gerado, e
o estado real pode mudar antes da aplicação. O Exemplo usa o provider `local`; providers de nuvem
têm outros riscos, como credencial e custo, que ficam fora desta prática.
