-- Expandir: a coluna nova convive com a antiga. Nada é removido.
ALTER TABLE cliente ADD COLUMN nome VARCHAR(120);

-- Backfill das linhas que já existem.
UPDATE cliente SET nome = nome_completo;

-- Escrita dupla no banco: quem ainda grava na coluna antiga (e quem já grava na nova)
-- mantém as duas iguais durante a transição.
CREATE FUNCTION cliente_sincroniza_nome() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.nome IS NULL THEN
            NEW.nome := NEW.nome_completo;
        ELSIF NEW.nome_completo IS NULL THEN
            NEW.nome_completo := NEW.nome;
        END IF;
    ELSIF NEW.nome IS DISTINCT FROM OLD.nome THEN
        NEW.nome_completo := NEW.nome;
    ELSIF NEW.nome_completo IS DISTINCT FROM OLD.nome_completo THEN
        NEW.nome := NEW.nome_completo;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cliente_sincroniza_nome
    BEFORE INSERT OR UPDATE ON cliente
    FOR EACH ROW EXECUTE FUNCTION cliente_sincroniza_nome();
