-- Substitui completamente o catálogo de motivos de parada
DELETE FROM input_justificativa WHERE codigo_motivo IS NOT NULL;
DELETE FROM motivo_parada;

INSERT INTO motivo_parada (codigo, descricao, origem, responsavel) VALUES
    ('F1',  'Manutenção Preventiva',              'Facilites', 'Manutenção Predial'),
    ('F2',  'Manutenção Corretiva',               'Facilites', 'Manutenção Predial'),
    ('F3',  'Falta de Energia Elétrica',          'Facilites', 'Manutenção Predial'),
    ('F4',  'Falta de Ar Comprimido',             'Facilites', 'Manutenção Predial'),
    ('F5',  'Falta de Exaustão',                  'Facilites', 'Manutenção Predial'),
    ('FO1', 'Qualidade na Matéria Prima',         'Fornecedor', 'IQC'),
    ('FO2', 'Material Fora da Especificação',     'Fornecedor', 'IQC'),
    ('S1',  'Troca de Setup (Produto)',            'Setup',      'PCP'),
    ('S2',  'Validação do Processo',              'Setup',      'Manufatura'),
    ('S3',  'NPI',                                'NPI',        'PCP / Engª Produto'),
    ('S4',  'Setup Não Planejado',                'Setup',      'PCP'),
    ('S5',  'Preenchimento de Processo',          'Setup',      'Manufatura'),
    ('T1',  'Falha de Impressão do QR Code',      'Tecnologia', 'TI'),
    ('T2',  'Falta de Monitor',                   'Tecnologia', 'TI'),
    ('T3',  'Falta de Scanner',                   'Tecnologia', 'TI'),
    ('T4',  'Sistema Inoperante',                 'Tecnologia', 'TI'),
    ('T5',  'Falta de Impressora',                'Tecnologia', 'TI');
