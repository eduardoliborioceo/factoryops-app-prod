CREATE TABLE IF NOT EXISTS pci_modelo_padrao (
    id               SERIAL       PRIMARY KEY,
    nome             VARCHAR(100) NOT NULL,
    modelo           VARCHAR(100),
    cliente          VARCHAR(100),
    familia          VARCHAR(100),
    qtd_por_caixa    INTEGER,
    meta_hora        INTEGER,
    mascara_etiqueta TEXT,
    roteiro_id       INTEGER REFERENCES roteiros(id) ON DELETE SET NULL,
    criado_em        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    ativo            BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_pci_modelo_padrao_modelo ON pci_modelo_padrao(modelo);
