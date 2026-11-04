---
titulo: Segurança
grupo: Entrega e operação
descricao: "Como a mudança é pensada contra ameaças antes de virar código, e como segredo e dependência são impedidos de entrar no repositório."
steering: [seguranca]
skills: [threat-model]
referencias: [sdd-scaffold-threat-model]
revisado_em: 2026-11-04
---

A skill `threat-model` do scaffold transforma a segurança de uma mudança em três regras que cabem
numa spec: responder por escrito a cinco perguntas, com um parágrafo de mitigação para cada sim,
manter a policy no menor privilégio, e nunca commitar segredo, com o scanner bloqueante no CI
[ref:sdd-scaffold-threat-model]. As práticas desta faixa seguem essa divisão: a SEG-01 é o
threat-model, a SEG-02 é o segredo, e a SEG-03 estende a mesma lógica à dependência que um modelo
propõe. A SEG-04 e a SEG-05 levam a segurança ao código que roda: a configuração insegura não deixa a
aplicação subir em produção, e a rota nasce exigindo credencial e sob limite de taxa. A SEG-06 põe
no mesmo pipeline da SEG-02 a varredura da imagem e o SAST do código, como jobs que reprovam a MR. O
que é específico de cada projeto, como o mecanismo de autenticação e a classificação do
dado, fica no steering `seguranca` do projeto, e não aqui [ref:sdd-scaffold-threat-model]. Dado
pessoal tem faixa própria, a de privacidade e LGPD.
