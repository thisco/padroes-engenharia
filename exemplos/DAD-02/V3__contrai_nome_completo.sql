-- Contrair: só depois de todos os consumidores lerem e gravarem em "nome".
DROP TRIGGER cliente_sincroniza_nome ON cliente;
DROP FUNCTION cliente_sincroniza_nome();
ALTER TABLE cliente ALTER COLUMN nome SET NOT NULL;
ALTER TABLE cliente DROP COLUMN nome_completo;
