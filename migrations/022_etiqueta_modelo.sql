CREATE TABLE IF NOT EXISTS etiqueta_modelo (
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(60) NOT NULL UNIQUE,
    dados         JSONB NOT NULL DEFAULT '{}',
    criado_em     TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
