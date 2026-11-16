---
titulo: Modelo de conhecimento
descricao: 'O que o portal sabe, como esse conhecimento é escrito em dados ligados e como um agente o encontra
  sem ler o catálogo inteiro: três diagramas do grafo do catálogo e do piloto RDF.'
lead: 'O portal guarda o que sabe como entidades e vínculos: práticas, referências, ferramentas e a espinha.
  Em RDF, cada vínculo é uma tripla de sujeito, predicado e objeto, e um conjunto de triplas forma um grafo
  [ref:w3c-rdf11]. Os três diagramas abaixo mostram esse grafo, as formas em que ele é escrito e o caminho
  que um agente percorre para usá-lo.'
referencias:
- owl2vowl
- w3c-jsonld11
- w3c-owl2-primer
- w3c-rdf11
- w3c-rdfs
- w3c-shacl
- w3c-skos-primer
- w3c-turtle
- webvowl
revisado_em: '2026-11-14'
---

## O que o portal sabe

O grafo do catálogo nasce do Markdown e do YAML do repositório: cada prática, referência, ferramenta,
receita, conceito e célula da espinha vira uma entidade, e as ligações que o grafo do catálogo registra viram
vínculos com direção e arquivo de fonte. Exemplos, mecanismos, datas de revisão e a URL e o nível de
verificação das referências não entram no piloto: não viram vínculo nem propriedade.

Em RDF Schema, recursos se agrupam em classes, e a tripla `R rdf:type C` diz que R é instância da
classe C [ref:w3c-rdfs]. Aqui, `Pratica` é a classe; a prática API-01, identificada pelo IRI
`…/id/API-01`, é uma instância dela; o ID `API-01` fica guardado como texto (`pe:identificador`). O
diagrama desenha as classes do vocabulário do portal e as propriedades que as ligam, e cada relação da
lista traz um exemplo tirado do catálogo publicado.

## Como o conhecimento é representado

RDF Schema oferece um vocabulário de modelagem para dados RDF, com rótulos (`rdfs:label`) e
descrições (`rdfs:comment`) que podem ser usados para dar nome e descrição legíveis a um recurso
[ref:w3c-rdfs]. Uma ontologia OWL 2 declara classes,
propriedades e indivíduos [ref:w3c-owl2-primer]. Ferramentas chamadas raciocinadores podem calcular
consequências automaticamente a partir dela [ref:w3c-owl2-primer]; o piloto do portal não executa
nenhum, e o grafo diz só o que o catálogo declarou.

JSON-LD é um formato baseado em JSON para serializar dados ligados; um documento JSON-LD é sempre um
documento JSON válido, e o contexto mapeia termos para IRIs [ref:w3c-jsonld11]. Turtle escreve um grafo
RDF inteiro em forma de texto compacta [ref:w3c-turtle]. Com o piloto ativo, o portal publica os mesmos
dados nas duas formas: são duas escritas do mesmo grafo, e não etapas uma depois da outra. Cada vínculo
também é publicado como afirmação (`rdf:Statement`), com a relação de origem e o arquivo de fonte, para
proveniência: ela registra de onde veio o vínculo, e não que ele foi verificado.

O WebVOWL é uma ferramenta para visualizar ontologias na web [ref:webvowl], e o OWL2VOWL converte uma
ontologia num arquivo JSON para ele [ref:owl2vowl]. O vocabulário do piloto pode ser avaliado com os
dois fora do build; o build não depende deles, e a visualização não prova que os dados estão certos.

Dois padrões ficam fora do piloto. SKOS oferece um modelo para a estrutura de esquemas de conceitos,
com rótulos preferidos e alternativos e relações mais amplas, mais específicas e associativas
[ref:w3c-skos-primer]. SHACL é uma linguagem para validar grafos RDF contra um conjunto de condições, as
shapes [ref:w3c-shacl]. O portal não implementa nenhum dos dois; eles aparecem no diagrama como
possibilidades futuras.

## Como o agente descobre e usa

O agente começa pelo `llms.txt`. Com o piloto ativo, ele anuncia o manifesto semântico, que lista
capacidades, limites e um roteiro curto: descobrir, buscar, ler, seguir vínculo e citar a fonte. Do
índice o agente tira o caminho da entidade; o JSON-LD da entidade traz os vizinhos de um salto, com a
fonte de cada vínculo, sem baixar o catálogo inteiro. A consulta local (`consultar.py`) responde a uma
pergunta com IDs e ponteiros dentro de um orçamento de tokens, com ou sem o piloto.
