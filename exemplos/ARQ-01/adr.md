# ADR 0002: Fila de tarefas no PostgreSQL, sem broker

> **Status:** aceita
> **Data:** 2026-10-07
> **Formato:** Nygard (contexto → decisão → consequências)

## Contexto

O serviço de boletos precisa processar cerca de 200 tarefas por minuto (envio de segunda via e
conciliação). Já operamos um PostgreSQL gerenciado, e o time de três pessoas não opera nenhum
broker de mensagens. Um broker novo traria mais um componente para monitorar, versionar e
reproduzir no ambiente local. A fila precisa sobreviver a reinício e entregar cada tarefa a um
único consumidor.

## Decisão

Vamos usar uma tabela `tarefa` no PostgreSQL como fila, com consumidores que pegam uma linha por
vez com `SELECT ... FOR UPDATE SKIP LOCKED`. Não vamos introduzir um broker enquanto o volume
ficar abaixo de 2 000 tarefas por minuto.

## Consequências

Fica mais fácil: nenhum componente novo no compose nem na nuvem, e a tarefa e o dado de negócio
mudam na mesma transação. Fica mais difícil: o banco passa a receber a carga da fila, então o
volume precisa ser medido; acima de 2 000 tarefas por minuto esta decisão é revista por uma
ADR nova, que a substitui. A tabela `tarefa` entra nas migrations e na Arquitetura Viva.
