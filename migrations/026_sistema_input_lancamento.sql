-- Catálogo de motivos de parada (justificativas)
CREATE TABLE IF NOT EXISTS motivo_parada (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(30) NOT NULL UNIQUE,
    origem      VARCHAR(100) NOT NULL,
    descricao   TEXT NOT NULL,
    responsavel VARCHAR(100) NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO motivo_parada (codigo, origem, descricao, responsavel) VALUES
    ('MANUT_PREV',  'Manutenção',  'Manutenção Preventiva',          'Manutenção'),
    ('MANUT_CORR',  'Manutenção',  'Manutenção Corretiva / Quebra',  'Manutenção'),
    ('SETUP',       'Produção',    'Troca de Modelo / Setup',         'Produção'),
    ('ABAST_MAT',   'Almoxarifado','Abastecimento de Material',       'Almoxarifado'),
    ('FALT_MAT',    'Almoxarifado','Falta de Material',               'Almoxarifado'),
    ('QUAL_INSP',   'Qualidade',   'Inspeção / Análise de Qualidade', 'Qualidade'),
    ('RETRABALHO',  'Qualidade',   'Retrabalho',                      'Qualidade'),
    ('ENG',         'Engenharia',  'Mudança de Engenharia / ECO',     'Engenharia'),
    ('TREINO',      'RH',          'Treinamento',                     'RH'),
    ('AUSENCIA',    'RH',          'Ausência / Falta de Pessoal',     'RH'),
    ('NP',          'PCP',         'Sem Programação / Linha Ociosa',  'PCP'),
    ('PARADA_PROG', 'Produção',    'Parada Programada',               'Produção'),
    ('PROCESSO',    'Produção',    'Problema de Processo',            'Engenharia'),
    ('OUTROS',      'Produção',    'Outros',                          'Produção')
ON CONFLICT (codigo) DO NOTHING;

-- Catálogo de códigos de defeito
CREATE TABLE IF NOT EXISTS codigo_defeito (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(30) NOT NULL UNIQUE,
    descricao   TEXT NOT NULL,
    categoria   VARCHAR(50),
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO codigo_defeito (codigo, descricao, categoria) VALUES
    ('PONTE',       'Ponte de Solda (Solder Bridge)',     'Solda'),
    ('FRIA',        'Solda Fria / Insuficiente',          'Solda'),
    ('EXCESSO',     'Excesso de Solda',                   'Solda'),
    ('SEM_SOLDA',   'Sem Solda / Abertura',               'Solda'),
    ('MISS',        'Componente Faltando (Missing)',       'Componente'),
    ('WRONG',       'Componente Errado (Wrong Part)',      'Componente'),
    ('ROT',         'Componente Rotacionado',              'Componente'),
    ('POLAR',       'Polaridade Invertida',                'Componente'),
    ('LIFT',        'Componente Levantado (Tombstone)',    'Componente'),
    ('DESLOCADO',   'Componente Deslocado',                'Componente'),
    ('DANO_COMP',   'Componente Danificado',               'Componente'),
    ('DANO_PCB',    'Dano na Placa (PCB)',                 'Placa'),
    ('OXIDO',       'Oxidação / Contaminação',             'Placa'),
    ('CURTO',       'Curto-circuito',                     'Elétrico'),
    ('ABERTO',      'Circuito Aberto',                    'Elétrico'),
    ('OUTROS',      'Outros / Não Classificado',           'Outros')
ON CONFLICT (codigo) DO NOTHING;

-- Registros de lançamento hora a hora
CREATE TABLE IF NOT EXISTS input_lancamento (
    id              SERIAL PRIMARY KEY,
    data            DATE NOT NULL,
    filial          VARCHAR(20) NOT NULL,
    setor           VARCHAR(50) NOT NULL,
    linha           VARCHAR(50) NOT NULL,
    turno           VARCHAR(50) NOT NULL,
    hora_inicio     VARCHAR(5) NOT NULL,
    hora_fim        VARCHAR(5) NOT NULL,
    modelo          VARCHAR(100),
    cliente         VARCHAR(200),
    op              VARCHAR(50),
    fase            VARCHAR(20),
    meta_hora       NUMERIC,
    producao_real   INTEGER NOT NULL DEFAULT 0,
    total_defeitos  INTEGER NOT NULL DEFAULT 0,
    planejamento_id INTEGER,
    criado_por      INTEGER,
    criado_em       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (data, setor, linha, turno, hora_inicio)
);

-- Justificativas por lançamento (múltiplas por slot)
CREATE TABLE IF NOT EXISTS input_justificativa (
    id                  SERIAL PRIMARY KEY,
    lancamento_id       INTEGER NOT NULL REFERENCES input_lancamento(id) ON DELETE CASCADE,
    codigo_motivo       VARCHAR(30) REFERENCES motivo_parada(codigo),
    origem              VARCHAR(100),
    descricao           TEXT,
    responsavel         VARCHAR(100),
    justificativa_texto TEXT,
    perda_minutos       INTEGER NOT NULL DEFAULT 0,
    criado_em           TIMESTAMPTZ DEFAULT NOW()
);

-- Defeitos por lançamento (múltiplos por slot)
CREATE TABLE IF NOT EXISTS input_defeito (
    id               SERIAL PRIMARY KEY,
    lancamento_id    INTEGER NOT NULL REFERENCES input_lancamento(id) ON DELETE CASCADE,
    codigo_defeito   VARCHAR(30) REFERENCES codigo_defeito(codigo),
    posicao_mecanica VARCHAR(100),
    quantidade       INTEGER NOT NULL DEFAULT 1,
    criado_em        TIMESTAMPTZ DEFAULT NOW()
);
