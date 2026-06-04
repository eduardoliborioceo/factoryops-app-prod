-- Sessão de embalagem: agrupa os scans de um operador em uma linha/OP
CREATE TABLE IF NOT EXISTS pci_embalagem_sessao (
    id            SERIAL       PRIMARY KEY,
    linha         VARCHAR(50)  NOT NULL,
    usuario       VARCHAR(100) NOT NULL,
    op            VARCHAR(100) NOT NULL,
    modelo        VARCHAR(100),
    cliente       VARCHAR(100),
    data          DATE         NOT NULL DEFAULT CURRENT_DATE,
    turno         VARCHAR(20),
    iniciado_em   TIMESTAMP    NOT NULL DEFAULT NOW(),
    finalizado_em TIMESTAMP,
    status        VARCHAR(20)  NOT NULL DEFAULT 'ativo'
);

-- Registro individual de cada placa bipada
CREATE TABLE IF NOT EXISTS pci_embalagem_scan (
    id          SERIAL       PRIMARY KEY,
    sessao_id   INTEGER      NOT NULL REFERENCES pci_embalagem_sessao(id) ON DELETE CASCADE,
    serial      VARCHAR(200) NOT NULL,
    scaneado_em TIMESTAMP    NOT NULL DEFAULT NOW(),
    impresso    BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_pci_scan_sessao ON pci_embalagem_scan(sessao_id);
CREATE INDEX IF NOT EXISTS idx_pci_sessao_op   ON pci_embalagem_sessao(op, data);
