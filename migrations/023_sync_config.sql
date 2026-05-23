CREATE TABLE IF NOT EXISTS sync_config (
    chave VARCHAR(50) PRIMARY KEY,
    valor TEXT NOT NULL,
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO sync_config (chave, valor)
VALUES ('automatico_habilitado', 'true')
ON CONFLICT (chave) DO NOTHING;

CREATE TABLE IF NOT EXISTS sync_historico (
    id SERIAL PRIMARY KEY,
    executado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tipo VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    registros_buscados INT DEFAULT 0,
    salvos INT DEFAULT 0,
    erros INT DEFAULT 0,
    mensagem TEXT
);

CREATE INDEX IF NOT EXISTS idx_sync_historico_executado_em
    ON sync_historico (executado_em DESC);
