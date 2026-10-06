-- Desfaz a contração com uma migration nova: recria a coluna antiga e copia o dado de "nome".
ALTER TABLE cliente ADD COLUMN nome_completo VARCHAR(120);
UPDATE cliente SET nome_completo = nome;
ALTER TABLE cliente ALTER COLUMN nome_completo SET NOT NULL;
