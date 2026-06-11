-- Frota de veículos e cadastro de motoristas para o módulo de transporte.

CREATE TABLE rh_veiculo (
    id          SERIAL PRIMARY KEY,
    placa       VARCHAR(20)  NOT NULL,
    modelo      VARCHAR(100),
    ano         SMALLINT,
    capacidade  SMALLINT     NOT NULL DEFAULT 40,
    filial      VARCHAR(100),
    status      VARCHAR(20)  NOT NULL DEFAULT 'ativo',
    observacao  TEXT,
    criado_em   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT rh_veiculo_placa_unique UNIQUE (placa)
);

CREATE TABLE rh_motorista (
    id             SERIAL PRIMARY KEY,
    nome           VARCHAR(200) NOT NULL,
    cnh            VARCHAR(30),
    categoria_cnh  VARCHAR(5),
    validade_cnh   DATE,
    telefone       VARCHAR(20),
    filial         VARCHAR(100),
    status         VARCHAR(20)  NOT NULL DEFAULT 'ativo',
    observacao     TEXT,
    criado_em      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
