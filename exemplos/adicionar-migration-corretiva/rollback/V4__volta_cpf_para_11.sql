-- Rollback da V3: volta cpf para VARCHAR(11). Falha se alguma linha já tiver mais de 11 caracteres.
ALTER TABLE cliente ALTER COLUMN cpf TYPE VARCHAR(11);
