CREATE TABLE IF NOT EXISTS empresa_config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    nome_empresa TEXT NOT NULL DEFAULT 'Venttos Electronics',
    nome_exibicao TEXT,
    cnpj TEXT,
    logo_url TEXT,
    filiais JSONB NOT NULL DEFAULT '["VTE","VTT"]',
    menu_visivel JSONB NOT NULL DEFAULT '{
        "funcionalidades": true,
        "producao": true,
        "engenharia": true,
        "pcp": true,
        "logistica": true,
        "configuracoes": true
    }',
    setores_por_filial JSONB NOT NULL DEFAULT '{
        "VTE": ["SMD", "PTH", "IM/PA"],
        "VTT": ["SMD"]
    }',
    atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO empresa_config (id)
VALUES (1)
ON CONFLICT DO NOTHING;
