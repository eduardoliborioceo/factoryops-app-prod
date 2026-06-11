-- Tabelas de gerenciamento de rotas de transporte para colaboradores.

CREATE TABLE rh_rota (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(30)  NOT NULL,
    nome            VARCHAR(150) NOT NULL,
    filial          VARCHAR(100),
    turno           VARCHAR(10)  NOT NULL DEFAULT '1',
    sentido         VARCHAR(20)  NOT NULL DEFAULT 'ambos',
    regra_descida   VARCHAR(30)  NOT NULL DEFAULT 'agrupado',
    veiculo         VARCHAR(100),
    motorista       VARCHAR(150),
    cor             VARCHAR(10)  NOT NULL DEFAULT '#0d6efd',
    partida_nome    VARCHAR(200) NOT NULL DEFAULT 'Venttos — Polo Industrial de Manaus',
    partida_lat     NUMERIC(10,7)        DEFAULT -3.0965000,
    partida_lng     NUMERIC(10,7)        DEFAULT -60.0208000,
    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT rh_rota_codigo_unique UNIQUE (codigo)
);

CREATE TABLE rh_rota_colaborador (
    id               SERIAL PRIMARY KEY,
    rota_id          INTEGER      NOT NULL REFERENCES rh_rota(id) ON DELETE CASCADE,
    employee_id      INTEGER               REFERENCES employees(id) ON DELETE SET NULL,
    nome             VARCHAR(200) NOT NULL,
    endereco_rua     VARCHAR(200),
    endereco_numero  VARCHAR(20),
    endereco_bairro  VARCHAR(100),
    endereco_cidade  VARCHAR(100) NOT NULL DEFAULT 'Manaus',
    endereco_estado  VARCHAR(5)   NOT NULL DEFAULT 'AM',
    lat              NUMERIC(10,7),
    lng              NUMERIC(10,7),
    geocodificado    BOOLEAN      NOT NULL DEFAULT FALSE,
    ordem            INTEGER      NOT NULL DEFAULT 0,
    tipo_parada      VARCHAR(30)  NOT NULL DEFAULT 'embarque_descida',
    observacao       TEXT,
    criado_em        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rh_rota_colaborador_rota     ON rh_rota_colaborador(rota_id);
CREATE INDEX idx_rh_rota_colaborador_employee ON rh_rota_colaborador(employee_id);
