CREATE TABLE cliente (
    id             BIGSERIAL PRIMARY KEY,
    nome           VARCHAR(120) NOT NULL,
    cpf            CHAR(11) NOT NULL UNIQUE,
    email          VARCHAR(160) NOT NULL,
    condicao_saude VARCHAR(200)
);
