-- PCI Studio: component library, PCB projects, and BOM items for 3D analysis.

CREATE TABLE pci_componente (
    id            SERIAL PRIMARY KEY,
    part_number   VARCHAR(200) NOT NULL,
    descricao     VARCHAR(500),
    fabricante    VARCHAR(200),
    tipo          VARCHAR(20)  NOT NULL DEFAULT 'smd',     -- smd | pth | conector | outro
    package       VARCHAR(100) NOT NULL DEFAULT 'unknown',
    comp_mm       NUMERIC(8,3),
    larg_mm       NUMERIC(8,3),
    alt_mm        NUMERIC(8,3),
    cor_hex       VARCHAR(10)  NOT NULL DEFAULT '#3b82f6',
    datasheet_url TEXT,
    criado_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pci_componente_package ON pci_componente(UPPER(package));

CREATE TABLE pci_projeto (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(200) NOT NULL,
    codigo      VARCHAR(100),
    descricao   TEXT,
    comp_mm     NUMERIC(10,3) NOT NULL DEFAULT 100,
    larg_mm     NUMERIC(10,3) NOT NULL DEFAULT 80,
    esp_mm      NUMERIC(8,3)  NOT NULL DEFAULT 1.6,
    cor_placa   VARCHAR(10)   NOT NULL DEFAULT '#1d4f2a',
    criado_por  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    criado_em   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pci_bom_item (
    id            SERIAL PRIMARY KEY,
    projeto_id    INTEGER      NOT NULL REFERENCES pci_projeto(id) ON DELETE CASCADE,
    designator    VARCHAR(50)  NOT NULL,
    valor         VARCHAR(200),
    part_number   VARCHAR(200),
    package       VARCHAR(100),
    descricao     VARCHAR(500),
    tipo          VARCHAR(20)  NOT NULL DEFAULT 'smd',
    pos_x         NUMERIC(10,3),
    pos_y         NUMERIC(10,3),
    angulo        NUMERIC(6,2) DEFAULT 0,
    lado          VARCHAR(10)  NOT NULL DEFAULT 'top',
    componente_id INTEGER REFERENCES pci_componente(id) ON DELETE SET NULL,
    ativo         BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pci_bom_projeto    ON pci_bom_item(projeto_id);
CREATE INDEX idx_pci_bom_componente ON pci_bom_item(componente_id);

-- Seed: common SMD / PTH / connector packages
INSERT INTO pci_componente (part_number, descricao, fabricante, tipo, package, comp_mm, larg_mm, alt_mm, cor_hex) VALUES
('RES-0402',   'Resistor SMD 0402',             'Genérico', 'smd',     '0402',    1.0,  0.5,  0.35, '#f97316'),
('RES-0603',   'Resistor SMD 0603',             'Genérico', 'smd',     '0603',    1.6,  0.8,  0.45, '#f97316'),
('RES-0805',   'Resistor SMD 0805',             'Genérico', 'smd',     '0805',    2.0,  1.25, 0.45, '#f97316'),
('RES-1206',   'Resistor SMD 1206',             'Genérico', 'smd',     '1206',    3.2,  1.6,  0.55, '#f97316'),
('CAP-0402',   'Capacitor SMD 0402',            'Genérico', 'smd',     '0402',    1.0,  0.5,  0.5,  '#3b82f6'),
('CAP-0603',   'Capacitor SMD 0603',            'Genérico', 'smd',     '0603',    1.6,  0.8,  0.8,  '#3b82f6'),
('CAP-0805',   'Capacitor SMD 0805',            'Genérico', 'smd',     '0805',    2.0,  1.25, 1.0,  '#3b82f6'),
('CAP-1206',   'Capacitor SMD 1206',            'Genérico', 'smd',     '1206',    3.2,  1.6,  1.5,  '#3b82f6'),
('CAP-1210',   'Capacitor SMD 1210',            'Genérico', 'smd',     '1210',    3.2,  2.5,  1.5,  '#3b82f6'),
('IND-0402',   'Indutor SMD 0402',              'Genérico', 'smd',     '0402',    1.0,  0.5,  0.5,  '#a855f7'),
('IND-0603',   'Indutor SMD 0603',              'Genérico', 'smd',     '0603',    1.6,  0.8,  0.8,  '#a855f7'),
('SOT-23',     'Transistor/Diodo SOT-23',       'Genérico', 'smd',     'SOT-23',  2.9,  1.6,  1.45, '#22c55e'),
('SOT-89',     'Transistor SOT-89',             'Genérico', 'smd',     'SOT-89',  4.5,  2.5,  1.5,  '#22c55e'),
('SOT-223',    'Regulador SOT-223',             'Genérico', 'smd',     'SOT-223', 6.5,  3.5,  1.8,  '#22c55e'),
('SOIC-8',     'IC SOIC-8',                     'Genérico', 'smd',     'SOIC-8',  5.0,  4.0,  1.75, '#0ea5e9'),
('SOIC-16',    'IC SOIC-16',                    'Genérico', 'smd',     'SOIC-16', 10.3, 4.0,  1.75, '#0ea5e9'),
('QFP-32',     'IC QFP-32',                     'Genérico', 'smd',     'QFP-32',  9.0,  9.0,  1.5,  '#0ea5e9'),
('QFP-64',     'IC QFP-64',                     'Genérico', 'smd',     'QFP-64',  14.0, 14.0, 1.5,  '#0ea5e9'),
('QFP-100',    'IC QFP-100',                    'Genérico', 'smd',     'QFP-100', 16.0, 16.0, 1.5,  '#0ea5e9'),
('BGA-64',     'IC BGA-64',                     'Genérico', 'smd',     'BGA-64',  8.0,  8.0,  1.2,  '#6366f1'),
('BGA-256',    'IC BGA-256',                    'Genérico', 'smd',     'BGA-256', 17.0, 17.0, 1.2,  '#6366f1'),
('DIP-8',      'IC DIP-8',                      'Genérico', 'pth',     'DIP-8',   9.7,  7.6,  5.0,  '#dc2626'),
('DIP-14',     'IC DIP-14',                     'Genérico', 'pth',     'DIP-14',  18.5, 7.6,  5.0,  '#dc2626'),
('DIP-16',     'IC DIP-16',                     'Genérico', 'pth',     'DIP-16',  21.3, 7.6,  5.0,  '#dc2626'),
('TO-92',      'Transistor TO-92',              'Genérico', 'pth',     'TO-92',   3.0,  3.0,  8.0,  '#854d0e'),
('TO-220',     'Transistor/Regulador TO-220',   'Genérico', 'pth',     'TO-220',  10.0, 4.5,  15.0, '#854d0e'),
('CONN-2P',    'Conector 2 pinos',              'Genérico', 'conector','CONN-2P', 5.0,  2.5,  5.0,  '#64748b'),
('CONN-4P',    'Conector 4 pinos',              'Genérico', 'conector','CONN-4P', 10.0, 2.5,  5.0,  '#64748b'),
('USB-C',      'Conector USB-C SMD',            'Genérico', 'smd',     'USB-C',   8.9,  7.6,  3.1,  '#64748b'),
('USB-A-TH',   'Conector USB-A PTH',            'Genérico', 'conector','USB-A',   14.0, 13.0, 6.5,  '#64748b');
