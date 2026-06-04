-- Substitui os códigos genéricos pelos motivos de parada reais da Venttos Electronics
-- Categorias: A (Administrativa), F (Facilites), FO (Fornecedor), M (Máquina),
--             MA (Material), P (Processo), S (Setup), T (Tecnologia)

DELETE FROM motivo_parada
WHERE codigo IN (
    'MANUT_PREV','MANUT_CORR','SETUP','ABAST_MAT','FALT_MAT',
    'QUAL_INSP','RETRABALHO','ENG','TREINO','AUSENCIA',
    'NP','PARADA_PROG','PROCESSO','OUTROS'
);

INSERT INTO motivo_parada (codigo, descricao, origem, responsavel) VALUES
-- ── ADMINISTRATIVA ──────────────────────────────────────────────────────
('A1',  'Atraso de Rota',                           'Administrativa',   'RH'),
('A2',  'Refeição',                                  'Administrativa',   'RH'),
('A3',  'Reunião de Qualidade',                      'Administrativa',   'Qualidade'),
('A4',  'Absenteísmo',                               'Administrativa',   'RH'),
('A5',  'Reunião de Produção',                       'Administrativa',   'Manufatura'),
('A6',  'Ausência de Colaborador',                   'Administrativa',   'RH'),
('A7',  'Falha no Planejamento',                     'Administrativa',   'PCP'),
('A8',  'Início de Turno',                           'Administrativa',   'Manufatura'),
('A9',  'Final de Turno',                            'Administrativa',   'Manufatura'),
('A10', 'Falta de Embalagem Coletiva',               'Administrativa',   'Almoxarifado'),

-- ── FACILITES ───────────────────────────────────────────────────────────
('F1',  'Manutenção Preventiva',                     'Facilites',        'Manutenção Predial'),
('F2',  'Manutenção Corretiva',                      'Facilites',        'Manutenção Predial'),
('F3',  'Falta de Energia Elétrica',                 'Facilites',        'Manutenção Predial'),
('F4',  'Falta de Ar Comprimido',                    'Facilites',        'Manutenção Predial'),
('F5',  'Falta de Exaustão',                         'Facilites',        'Manutenção Predial'),

-- ── FORNECEDOR ──────────────────────────────────────────────────────────
('FO1', 'Qualidade na Matéria Prima',                'Fornecedor',       'IQC'),
('FO2', 'Material Fora da Especificação',            'Fornecedor',       'IQC'),

-- ── MÁQUINA — Engenharia de Teste ───────────────────────────────────────
('M1',  'Teste Funcional',                           'Máquina',          'Engª Teste'),
('M2',  'Máquina de Solda',                          'Máquina',          'Engª Teste'),
('M3',  'Esteira',                                   'Máquina',          'Engª Teste'),
('M4',  'Teste ICT',                                 'Máquina',          'Engª Teste'),
('M5',  'Teste Hipot',                               'Máquina',          'Engª Teste'),
('M6',  'Teste de LED',                              'Máquina',          'Engª Teste'),
('M7',  'Teste Estanqueidade',                       'Máquina',          'Engª Teste'),
('M8',  'Teste de Luz',                              'Máquina',          'Engª Teste'),
('M9',  'Teste de Movimento',                        'Máquina',          'Engª Teste'),
('M10', 'Teste Burn-In',                             'Máquina',          'Engª Teste'),
('M11', 'Teste Bluetooth',                           'Máquina',          'Engª Teste'),
('M12', 'Teste de Run-In',                           'Máquina',          'Engª Teste'),
('M13', 'Estação Autom. de Solda',                   'Máquina',          'Engª Teste'),
('M22', 'Teste Double Check',                        'Máquina',          'Engª Teste'),
('M23', 'Teste de Voz',                              'Máquina',          'Engª Teste'),
('M24', 'Teste do MAC',                              'Máquina',          'Engª Teste'),

-- ── MÁQUINA — Engenharia de Processo ────────────────────────────────────
('M14', 'Aplicador de Cola',                         'Máquina',          'Engª de Processo'),
('M15', 'Máquina Remanche',                          'Máquina',          'Engª de Processo'),
('M16', 'Máquina Knob',                              'Máquina',          'Engª de Processo'),
('M17', 'Seladora',                                  'Máquina',          'Engª de Processo'),
('M18', 'Parafusadeira',                             'Máquina',          'Engª de Processo'),
('M19', 'Máquina de Prensagem de Tampa',             'Máquina',          'Engª de Processo'),
('M20', 'Forno UV',                                  'Máquina',          'Engª de Processo'),
('M21', 'Ultrassom',                                 'Máquina',          'Engª de Processo'),

-- ── MÁQUINA — Manutenção SMT ────────────────────────────────────────────
('M25', 'MPM',                                       'Máquina',          'Manutenção SMT'),
('M26', 'DEK',                                       'Máquina',          'Manutenção SMT'),
('M27', 'CM',                                        'Máquina',          'Manutenção SMT'),
('M28', 'AOI',                                       'Máquina',          'Manutenção SMT'),
('M29', 'SPI',                                       'Máquina',          'Manutenção SMT'),
('M30', 'F4',                                        'Máquina',          'Manutenção SMT'),
('M31', 'F5',                                        'Máquina',          'Manutenção SMT'),
('M32', 'NXT',                                       'Máquina',          'Manutenção SMT'),
('M33', 'XP',                                        'Máquina',          'Manutenção SMT'),
('M34', 'Forno de Refusão',                          'Máquina',          'Manutenção SMT'),
('M35', 'Jumper',                                    'Máquina',          'Manutenção SMT'),
('M36', 'Ilhós',                                     'Máquina',          'Manutenção SMT'),
('M37', 'Axial',                                     'Máquina',          'Manutenção SMT'),
('M38', 'Radial',                                    'Máquina',          'Manutenção SMT'),
('M39', 'Adesivadora',                               'Máquina',          'Manutenção SMT'),
('M40', 'Router',                                    'Máquina',          'Manutenção SMT'),
('M41', 'Loader',                                    'Máquina',          'Manutenção SMT'),
('M42', 'Aimex',                                     'Máquina',          'Manutenção SMT'),

-- ── MATERIAL ────────────────────────────────────────────────────────────
('MA1',  'Montagem SMT/PTH',                         'Material',         'SMT/PTH'),
('MA2',  'Falta de Cola',                            'Material',         'Almoxarifado'),
('MA3',  'Falta de Solda (Pasta, Fio, Barra)',        'Material',         'Almoxarifado'),
('MA4',  'Falta de Álcool Isopropílico',             'Material',         'Almoxarifado'),
('MA5',  'Falta de Fluxo',                           'Material',         'Almoxarifado'),
('MA6',  'Aguardando Placas do SMT/PTH',             'Material',         'SMT/PTH'),
('MA7',  'Placas Aguardando Inspeção da Qualidade',  'Material',         'Qualidade'),
('MA8',  'Falta de Material',                        'Material',         'Almoxarifado'),
('MA9',  'Aguardando Placas do IM',                  'Material',         'Manufatura IM'),
('MA10', 'Falta de Embalagem Coletiva',              'Material',         'Almoxarifado'),

-- ── PROCESSO ────────────────────────────────────────────────────────────
('P1',  'Fechamento de Kit',                         'Processo',         'Manufatura'),
('P2',  'Falta Ordem de Produção',                   'Processo',         'PCP'),
('P3',  'Troca de Jig e Dispositivo',                'Processo',         'Engª Processo'),
('P4',  'Falta de Documentação',                     'Processo',         'Manufatura'),
('P5',  'Conferência de Material',                   'Processo',         'Almoxarifado'),
('P6',  'Falta de Jig ou Dispositivo',               'Processo',         'Engª Processo'),
('P7',  'Curva de Crescimento (Ramp Up)',             'Processo',         'Engª Processo'),
('P8',  'Meta em Análise da Engenharia',             'Processo',         'Engª Processo'),
('P9',  'Validação de Jig',                          'Processo',         'Engª Processo'),
('P10', 'Falta de Ferro de Soldar',                  'Processo',         'Engª Processo'),
('P11', 'Problema com o Ferro de Soldar',            'Processo',         'Engª Processo'),
('P12', 'Falta de Insumos (Alicate, Pinça, etc.)',   'Processo',         'Engª Processo'),
('P13', 'Ajuste no Layout',                          'Processo',         'Engª Processo'),
('P14', 'Balanceamento',                             'Processo',         'Engª Processo'),
('P15', 'Atraso de Produção',                        'Processo',         'Manufatura'),
('P16', 'Retrabalho',                                'Processo',         'Manufatura'),
('P17', 'Revisando Material Acumulado',              'Processo',         'Manufatura'),
('P18', 'Falta de Balança',                          'Processo',         'Engª Processo'),
('P19', 'Retirando Acúmulo',                         'Processo',         'Manufatura'),
('P20', 'Recuperando Metas',                         'Processo',         'Manufatura'),
('P22', 'Mudança de Plano de Voo',                   'Processo',         'PCP'),
('P23', 'Produzido Maior que a Meta',                'Processo',         'Manufatura'),
('P24', 'Aplicação do Verniz',                       'Processo',         'Manufatura'),
('P25', 'Limpeza de Noozle',                         'Processo',         'Manufatura'),
('P26', 'Alimentação de Linha',                      'Processo',         'Manufatura'),

-- ── SETUP ───────────────────────────────────────────────────────────────
('S1',  'Troca de Setup (Produto)',                   'Setup',            'PCP'),
('S2',  'Validação do Processo',                     'Setup',            'Manufatura'),
('S3',  'NPI',                                       'NPI',              'PCP / Engª Produto'),
('S4',  'Setup Não Planejado',                       'Setup',            'PCP'),
('S5',  'Preenchimento de Processo',                 'Setup',            'Manufatura'),

-- ── TECNOLOGIA ──────────────────────────────────────────────────────────
('T1',  'Falha de Impressão do QR Code',             'Tecnologia',       'TI'),
('T2',  'Falta de Monitor',                          'Tecnologia',       'TI'),
('T3',  'Falta de Scanner',                          'Tecnologia',       'TI'),
('T4',  'Sistema Inoperante',                        'Tecnologia',       'TI'),
('T5',  'Falta de Impressora',                       'Tecnologia',       'TI')

ON CONFLICT (codigo) DO UPDATE SET
    descricao   = EXCLUDED.descricao,
    origem      = EXCLUDED.origem,
    responsavel = EXCLUDED.responsavel;
