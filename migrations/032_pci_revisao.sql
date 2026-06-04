-- Cabeçalho do relatório de revisão
CREATE TABLE IF NOT EXISTS pci_revisao_relatorio (
    id          SERIAL PRIMARY KEY,
    cliente     VARCHAR(100),
    produto     VARCHAR(100),
    setor       VARCHAR(50),
    linha       VARCHAR(50),
    posto       VARCHAR(50),
    turno       VARCHAR(50),
    tipo_revisao VARCHAR(50),
    identificacao VARCHAR(100),
    meta        INTEGER,
    op          VARCHAR(50),
    data        DATE NOT NULL DEFAULT CURRENT_DATE,
    revisor     VARCHAR(100),
    criado_por  VARCHAR(100),
    -- Checkboxes de processo
    proc_top        BOOLEAN NOT NULL DEFAULT FALSE,
    proc_bot        BOOLEAN NOT NULL DEFAULT FALSE,
    proc_topbot     BOOLEAN NOT NULL DEFAULT FALSE,
    proc_lado01     BOOLEAN NOT NULL DEFAULT FALSE,
    proc_lado02     BOOLEAN NOT NULL DEFAULT FALSE,
    proc_aoi        BOOLEAN NOT NULL DEFAULT FALSE,
    proc_pre_forno  BOOLEAN NOT NULL DEFAULT FALSE,
    proc_pos_forno  BOOLEAN NOT NULL DEFAULT FALSE,
    proc_pre_maq    BOOLEAN NOT NULL DEFAULT FALSE,
    proc_pos_maq    BOOLEAN NOT NULL DEFAULT FALSE,
    proc_adesivo    BOOLEAN NOT NULL DEFAULT FALSE,
    proc_spi        BOOLEAN NOT NULL DEFAULT FALSE,
    -- Totais (calculados e armazenados ao salvar)
    total_produzido INTEGER,
    total_defeitos  INTEGER,
    total_scrap     INTEGER,
    criado_em  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status     VARCHAR(20)  NOT NULL DEFAULT 'rascunho'
);

-- Linhas horárias da tabela de produção
CREATE TABLE IF NOT EXISTS pci_revisao_hora (
    id           SERIAL PRIMARY KEY,
    relatorio_id INTEGER NOT NULL REFERENCES pci_revisao_relatorio(id) ON DELETE CASCADE,
    slot_ordem   SMALLINT NOT NULL,
    hora_ini     VARCHAR(5) NOT NULL,
    hora_fim     VARCHAR(5) NOT NULL,
    selecionado  BOOLEAN NOT NULL DEFAULT FALSE,
    aprovados    INTEGER,
    reprovados   INTEGER,
    defeitos_max INTEGER,
    modelo       VARCHAR(100),
    qtd_produzida INTEGER,
    placa_hh     BOOLEAN,
    fase         VARCHAR(5),
    revisora     VARCHAR(100),
    observacao   TEXT
);

-- Linhas de defeitos (código + qtd por slot de hora em JSONB)
CREATE TABLE IF NOT EXISTS pci_revisao_defeito (
    id              SERIAL PRIMARY KEY,
    relatorio_id    INTEGER NOT NULL REFERENCES pci_revisao_relatorio(id) ON DELETE CASCADE,
    linha_ordem     SMALLINT NOT NULL,
    codigo_defeito  VARCHAR(20),
    posicao_mecanica VARCHAR(50),
    lado            VARCHAR(5),
    qtd_por_hora    JSONB NOT NULL DEFAULT '{}',
    observacao      TEXT
);

CREATE INDEX IF NOT EXISTS idx_pci_revisao_hora_rel   ON pci_revisao_hora(relatorio_id);
CREATE INDEX IF NOT EXISTS idx_pci_revisao_def_rel    ON pci_revisao_defeito(relatorio_id);
CREATE INDEX IF NOT EXISTS idx_pci_revisao_rel_data   ON pci_revisao_relatorio(data);
