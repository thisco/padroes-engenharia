CREATE TABLE cliente (
    id            SERIAL PRIMARY KEY,
    nome_completo VARCHAR(120) NOT NULL
);

INSERT INTO cliente (nome_completo) VALUES ('Ana Souza'), ('Bruno Lima');
