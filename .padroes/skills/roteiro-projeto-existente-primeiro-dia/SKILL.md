---
name: roteiro-projeto-existente-primeiro-dia
description: "Trazer as regras e as verificações para um repositório que já existe, em três passos: você abre o agente; o agente instala o pacote e conduz a adoção do scaffold, parando para o seu sim."
---

# Projeto existente: o primeiro dia

Porta: projeto-existente. Siga os passos na ordem. Nos passos marcados 'Você decide', pare, mostre o resultado e espere a aprovação da pessoa.

## Prompt inicial

```prompt
Siga o roteiro "Projeto existente: o primeiro dia" do portal de padrões de engenharia, em
<URL do portal>/roteiros/projeto-existente-primeiro-dia.md. Faça os passos marcados "o agente"
sem me perguntar; nos passos marcados "você decide", pare, mostre o resultado e espere meu
sim. Nunca sobrescreva arquivo que já exista e me avise antes de qualquer passo destrutivo.
```

## Passo 1: Abrir o harness no projeto (Você faz)

Abra o agente dentro da pasta do repositório. O que muda de um harness para outro é só o comando
ou o botão. Confira antes que a árvore de trabalho está limpa (`git status`), para que tudo o que
o agente mudar apareça na adoção.

### Kiro

No terminal, entre na pasta do projeto e inicie o Kiro CLI:

```bash
cd ~/projetos/meu-projeto
kiro-cli
```

O Kiro lembra a conversa pela pasta em que ela começou, e `kiro-cli chat --resume` retoma a
conversa da pasta atual. No IDE, abra a pasta do projeto.

### Antigravity

No terminal, entre na pasta do projeto e rode `agy`; na primeira vez, ele pede que você confirme
que confia no diretório antes de indexar os arquivos:

```bash
cd ~/projetos/meu-projeto
agy
```

No app, clique no ícone New Project, depois em Add Folder, escolha a pasta do projeto e clique em
Create.

## Passo 2: Instalar o pacote e as skills (O agente)

O agente instala o pacote do portal e as skills de terceiros adotadas na trilha, numa pasta
`skills/` só, e monta os pontos de montagem de cada harness pela receita
[Instalar as skills por harness](../receitas/instalar-skills-por-harness.html). Num repositório que
ainda não tem o scaffold, é a receita que cria os links.

```prompt
Instale o pacote de padrões de engenharia em <URL do portal>/pacote/ neste repositório: leia
<URL do portal>/pacote/manifesto.json, baixe cada arquivo listado em "arquivos" para a pasta
.padroes/ do projeto e confira o SHA-256 de cada um contra o manifesto; se algum não bater, pare
e me avise. Copie as pastas de .padroes/skills/ para skills/, sem sobrescrever skill que já
exista. Instale também a skill brainstorming da coleção superpowers, como diz
<URL do portal>/ferramentas/sp-brainstorming.md. Depois monte os pontos de montagem das skills
seguindo a receita <URL do portal>/receitas/instalar-skills-por-harness.md. Mostre o ls de cada
ponto de montagem ao terminar.
```

## Passo 3: Adotar o scaffold pelo guia Brownfield (Você decide)

O agente segue a seção "Com o agente" do guia
[Brownfield em 5 passos](../guias/brownfield-em-5-passos.html): diagnóstico, constituição e
steering, hook e permissões, CI e a primeira merge request. Ele para em cada ponto em que o guia
pede o seu sim, mostra o que vai mudar e espera. Você confere cada parada, aprova ou corrige, e no
fim abre a merge request da adoção.

```prompt
Adote o sdd-scaffold neste repositório seguindo a seção "Com o agente" do guia "Brownfield em 5
passos" do portal de padrões de engenharia, em <URL do portal>/guias/brownfield-em-5-passos.md.
Leia o guia inteiro antes de começar e siga o prompt daquela seção passo a passo, sem pular
conferência. Em cada ponto em que o guia pede o meu sim ou manda me avisar, pare, mostre o
resultado e espere a minha resposta. Termine com a lista do que depende de mim, como o guia pede.
```
