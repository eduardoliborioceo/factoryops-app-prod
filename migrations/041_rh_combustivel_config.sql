-- Adiciona consumo e tipo de combustível ao cadastro de veículos.
-- Cria tabela de configuração de preços de combustível por cidade.

ALTER TABLE rh_veiculo
    ADD COLUMN IF NOT EXISTS consumo_km_l     NUMERIC(5,2) DEFAULT 7.5,
    ADD COLUMN IF NOT EXISTS tipo_combustivel VARCHAR(20)  DEFAULT 'diesel';

CREATE TABLE IF NOT EXISTS rh_combustivel_config (
    id              SERIAL PRIMARY KEY,
    tipo            VARCHAR(20)   NOT NULL,
    preco_litro     NUMERIC(8,3)  NOT NULL,
    cidade          VARCHAR(100)  NOT NULL DEFAULT 'Manaus',
    estado          VARCHAR(5)    NOT NULL DEFAULT 'AM',
    fonte           VARCHAR(200),
    data_referencia DATE          NOT NULL DEFAULT CURRENT_DATE,
    atualizado_em   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT rh_combustivel_config_unico UNIQUE (tipo, cidade)
);

INSERT INTO rh_combustivel_config (tipo, preco_litro, fonte)
VALUES
    ('diesel',     6.20, 'valor_inicial_manual'),
    ('diesel_s10', 6.35, 'valor_inicial_manual'),
    ('gasolina',   6.80, 'valor_inicial_manual'),
    ('etanol',     4.90, 'valor_inicial_manual')
ON CONFLICT (tipo, cidade) DO NOTHING;
