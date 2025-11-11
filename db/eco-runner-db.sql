-- ECO RUNNER - PostgreSQL 

-- Tabela de usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nick_name VARCHAR(12) NOT NULL UNIQUE,
    senha TEXT NOT NULL
);

-- Fase 1 - Coleta de itens
CREATE TABLE fase1 (
    usuario_id      INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
	itens_papel     INT NOT NULL DEFAULT 0,
    itens_plastico  INT NOT NULL DEFAULT 0,
    itens_vidro     INT NOT NULL DEFAULT 0,
    itens_metal     INT NOT NULL DEFAULT 0,
    fase_completa   BOOLEAN NOT NULL DEFAULT FALSE,
    vidas           INT NOT NULL DEFAULT 5 CHECK (vidas BETWEEN 0 AND 5),
    game_over       BOOLEAN NOT NULL DEFAULT FALSE
);

-- Fase 2 - Separação nas lixeiras
CREATE TABLE fase2 (
    usuario_id       INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    lixeira_papel    INT NOT NULL DEFAULT 0,
    lixeira_plastico INT NOT NULL DEFAULT 0,
    lixeira_vidro    INT NOT NULL DEFAULT 0,
    lixeira_metal    INT NOT NULL DEFAULT 0,
    fase_completa    BOOLEAN NOT NULL DEFAULT FALSE
);

-- Fase 3 - Desafio final
CREATE TABLE fase3 (
    usuario_id    INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    derrotar_yluh BOOLEAN NOT NULL DEFAULT FALSE,
    vidas         INT NOT NULL DEFAULT 5 CHECK (vidas BETWEEN 0 AND 5),
    game_over     BOOLEAN NOT NULL DEFAULT FALSE
);

-- Função trigger: marca game_over se vidas <= 0 (usada por fase1 e fase3)
CREATE OR REPLACE FUNCTION fn_gameover()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Se vidas ficou menor ou igual a zero, marca game_over e ajusta vidas para 0
    IF NEW.vidas <= 0 THEN
        NEW.game_over := TRUE;
        NEW.vidas := 0;
    END IF;
    RETURN NEW;
END;
$$;

-- Associa fn_gameover a fase1 e fase3 (antes de gravar)
CREATE TRIGGER trg_fase1_gameover
BEFORE INSERT OR UPDATE ON fase1
FOR EACH ROW EXECUTE FUNCTION fn_gameover();

CREATE TRIGGER trg_fase3_gameover
BEFORE INSERT OR UPDATE ON fase3
FOR EACH ROW EXECUTE FUNCTION fn_gameover();

-- Função trigger: quando fase2.fase_completa = TRUE
-- -> restaura vidas em fase1 e fase3 (5) e limpa game_over
CREATE OR REPLACE FUNCTION fn_fase2_completa()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Só age quando a nova linha (NEW) indica que a fase 2 foi completada
    IF NEW.fase_completa = TRUE THEN
        -- Restaura vidas em fase1 (se existir registro)
        UPDATE fase1
        SET vidas = 5, game_over = FALSE
        WHERE usuario_id = NEW.usuario_id;

        -- Restaura vidas em fase3 (se existir registro)
        UPDATE fase3
        SET vidas = 5, game_over = FALSE
        WHERE usuario_id = NEW.usuario_id;
    END IF;
    RETURN NEW;
END;
$$;

-- Trigger que chama fn_fase2_completa após INSERT/UPDATE em fase2
CREATE TRIGGER trg_fase2_completa
AFTER INSERT OR UPDATE ON fase2
FOR EACH ROW EXECUTE FUNCTION fn_fase2_completa();

-- (Opcional) índices simples para facilitar buscas
CREATE INDEX IF NOT EXISTS idx_usuarios_nick ON usuarios(nick_name);


ALTER TABLE usuarios ADD COLUMN salt TEXT NOT NULL;
