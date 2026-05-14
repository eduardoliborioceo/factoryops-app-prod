CREATE TABLE IF NOT EXISTS conferencia_arquivo (
    id              SERIAL PRIMARY KEY,
    planejamento_id INTEGER      NOT NULL REFERENCES planejamento(id) ON DELETE CASCADE,
    filename        VARCHAR(255) NOT NULL,
    mimetype        VARCHAR(100) NOT NULL,
    conteudo        BYTEA        NOT NULL,
    componentes     JSONB,
    uploaded_por    VARCHAR(100) NOT NULL,
    uploaded_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conferencia_arquivo_plan
    ON conferencia_arquivo (planejamento_id, uploaded_em DESC);

ALTER TABLE conferencia_material
    ADD COLUMN IF NOT EXISTS componentes_confirmados JSONB;
