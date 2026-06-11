-- Tabela de histórico de sincronizações com a ANP (preços de combustível).

CREATE TABLE IF NOT EXISTS rh_anp_sync_log (
    id                 SERIAL PRIMARY KEY,
    executado_em       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    status             VARCHAR(20)  NOT NULL,
    precos_atualizados INTEGER      NOT NULL DEFAULT 0,
    semana_referencia  DATE,
    fonte_url          TEXT,
    erro               TEXT
);
