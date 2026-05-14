CREATE TABLE IF NOT EXISTS conferencia_material (
    id              SERIAL PRIMARY KEY,
    planejamento_id INTEGER     NOT NULL REFERENCES planejamento(id) ON DELETE CASCADE,
    status          VARCHAR(20) NOT NULL CHECK (status IN ('CONFIRMADO', 'SEM_MATERIAL', 'PARCIAL')),
    observacao      TEXT,
    conferido_por   VARCHAR(100) NOT NULL,
    conferido_em    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conferencia_material_plan
    ON conferencia_material (planejamento_id, conferido_em DESC);
