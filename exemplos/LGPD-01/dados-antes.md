# Classificação dos dados

Classes: público, interno, pessoal, sensível. Todo campo de schema entra aqui antes da migration.
Campo pessoal ou sensível diz a finalidade em uma frase.

| Campo | Classe | Finalidade |
|---|---|---|
| cliente.id | interno | chave interna, sem significado fora do sistema |
| cliente.nome | pessoal | identificar o cliente no atendimento |
