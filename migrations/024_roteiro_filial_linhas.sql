ALTER TABLE roteiros ADD COLUMN IF NOT EXISTS filial VARCHAR(20) NOT NULL DEFAULT 'VTE';

CREATE TABLE IF NOT EXISTS roteiro_etapa_linhas (
    id       SERIAL PRIMARY KEY,
    etapa_id INT NOT NULL REFERENCES roteiro_etapas(id) ON DELETE CASCADE,
    linha    VARCHAR(50) NOT NULL,
    ordem    SMALLINT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_roteiro_etapa_linhas_etapa ON roteiro_etapa_linhas(etapa_id);
