-- Reinsere o catálogo completo de motivos de parada usando U&'...' Unicode escapes.
-- Seguro para qualquer terminal Windows (CP437, CP850, CP1252, etc.) pois
-- não transmite bytes acentuados: toda acentuação está em \XXXX hex ASCII.
--
-- Como usar:
--   psql $DATABASE_URL -f 029_motivo_parada_reinsert_ascii_safe.sql
-- OU colar no terminal Railway:
--   Copie e cole o conteúdo completo no psql do Railway.

DELETE FROM input_justificativa WHERE codigo_motivo IS NOT NULL;
DELETE FROM motivo_parada;

INSERT INTO motivo_parada (codigo, descricao, origem, responsavel) VALUES
-- ── ADMINISTRATIVA ───────────────────────────────────────────────────────────
    ('A1',  'Atraso de Rota',                                          'Administrativa',   'RH'),
    ('A2',  U&'Refei\00E7\00E3o',                                      'Administrativa',   'RH'),
    ('A3',  U&'Reuni\00E3o de Qualidade',                              'Administrativa',   'Qualidade'),
    ('A4',  U&'Absente\00EDsmo',                                       'Administrativa',   'RH'),
    ('A5',  U&'Reuni\00E3o de Produ\00E7\00E3o',                       'Administrativa',   'Manufatura'),
    ('A6',  U&'Aus\00EAncia de Colaborador',                           'Administrativa',   'RH'),
    ('A7',  'Falha no Planejamento',                                   'Administrativa',   'PCP'),
    ('A8',  U&'In\00EDcio de Turno',                                   'Administrativa',   'Manufatura'),
    ('A9',  'Final de Turno',                                          'Administrativa',   'Manufatura'),
    ('A10', 'Falta de Embalagem Coletiva',                             'Administrativa',   'Almoxarifado'),

-- ── FACILITES ────────────────────────────────────────────────────────────────
    ('F1',  U&'Manuten\00E7\00E3o Preventiva',                         'Facilites',        U&'Manuten\00E7\00E3o Predial'),
    ('F2',  U&'Manuten\00E7\00E3o Corretiva',                          'Facilites',        U&'Manuten\00E7\00E3o Predial'),
    ('F3',  U&'Falta de Energia El\00E9trica',                         'Facilites',        U&'Manuten\00E7\00E3o Predial'),
    ('F4',  'Falta de Ar Comprimido',                                  'Facilites',        U&'Manuten\00E7\00E3o Predial'),
    ('F5',  U&'Falta de Exaust\00E3o',                                 'Facilites',        U&'Manuten\00E7\00E3o Predial'),

-- ── FORNECEDOR ───────────────────────────────────────────────────────────────
    ('FO1', U&'Qualidade na Mat\00E9ria Prima',                        'Fornecedor',       'IQC'),
    ('FO2', U&'Material Fora da Especifica\00E7\00E3o',                'Fornecedor',       'IQC'),

-- ── MÁQUINA · Engª Teste ─────────────────────────────────────────────────────
    ('M1',  'Teste Funcional',                                         U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M2',  U&'M\00E1quina de Solda',                                  U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M3',  'Esteira',                                                 U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M4',  'Teste ICT',                                               U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M5',  'Teste Hipot',                                             U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M6',  'Teste de LED',                                            U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M7',  'Teste Estanqueidade',                                     U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M8',  'Teste de Luz',                                            U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M9',  'Teste de Movimento',                                      U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M10', 'Teste Burn-In',                                           U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M11', 'Teste Bluetooth',                                         U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M12', 'Teste de Run-In',                                         U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M13', U&'Esta\00E7\00E3o Autom. de Solda',                       U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M22', 'Teste Double Check',                                      U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M23', 'Teste de Voz',                                            U&'M\00E1quina',    U&'Eng\00AA Teste'),
    ('M24', 'Teste do MAC',                                            U&'M\00E1quina',    U&'Eng\00AA Teste'),

-- ── MÁQUINA · Engª de Processo ───────────────────────────────────────────────
    ('M14', 'Aplicador de Cola',                                       U&'M\00E1quina',    U&'Eng\00AA de Processo'),
    ('M15', U&'M\00E1quina Remanche',                                  U&'M\00E1quina',    U&'Eng\00AA de Processo'),
    ('M16', U&'M\00E1quina Knob',                                      U&'M\00E1quina',    U&'Eng\00AA de Processo'),
    ('M17', 'Seladora',                                                U&'M\00E1quina',    U&'Eng\00AA de Processo'),
    ('M18', 'Parafusadeira',                                           U&'M\00E1quina',    U&'Eng\00AA de Processo'),
    ('M19', U&'M\00E1quina de Prensagem de Tampa',                     U&'M\00E1quina',    U&'Eng\00AA de Processo'),
    ('M20', 'Forno UV',                                                U&'M\00E1quina',    U&'Eng\00AA de Processo'),
    ('M21', 'Ultrassom',                                               U&'M\00E1quina',    U&'Eng\00AA de Processo'),

-- ── MÁQUINA · Manutenção SMT ─────────────────────────────────────────────────
    ('M25', 'MPM',                                                     U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M26', 'DEK',                                                     U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M27', 'CM',                                                      U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M28', 'AOI',                                                     U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M29', 'SPI',                                                     U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M30', 'F4',                                                      U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M31', 'F5',                                                      U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M32', 'NXT',                                                     U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M33', 'XP',                                                      U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M34', U&'Forno de Refus\00E3o',                                  U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M35', 'Jumper',                                                  U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M36', U&'Ilh\00F3s',                                             U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M37', 'Axial',                                                   U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M38', 'Radial',                                                  U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M39', 'Adesivadora',                                             U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M40', 'Router',                                                  U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M41', 'Loader',                                                  U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),
    ('M42', 'Aimex',                                                   U&'M\00E1quina',    U&'Manuten\00E7\00E3o SMT'),

-- ── MATERIAL ─────────────────────────────────────────────────────────────────
    ('MA1',  'Montagem SMT/PTH',                                       'Material',         'SMT/PTH'),
    ('MA2',  'Falta de Cola',                                          'Material',         'Almoxarifado'),
    ('MA3',  'Falta de Solda (Pasta, Fio, Barra)',                     'Material',         'Almoxarifado'),
    ('MA4',  U&'Falta de \00C1lcool Isoprop\00EDlico',                 'Material',         'Almoxarifado'),
    ('MA5',  'Falta de Fluxo',                                         'Material',         'Almoxarifado'),
    ('MA6',  'Aguardando Placas do SMT/PTH',                           'Material',         'SMT/PTH'),
    ('MA7',  U&'Placas Aguardando Inspe\00E7\00E3o da Qualidade',      'Material',         'Qualidade'),
    ('MA8',  'Falta de Material',                                      'Material',         'Almoxarifado'),
    ('MA9',  'Aguardando Placas do IM',                                'Material',         'Manufatura IM'),
    ('MA10', 'Falta de Embalagem Coletiva',                            'Material',         'Almoxarifado'),

-- ── PROCESSO ─────────────────────────────────────────────────────────────────
    ('P1',  'Fechamento de Kit',                                       'Processo',         'Manufatura'),
    ('P2',  U&'Falta Ordem de Produ\00E7\00E3o',                       'Processo',         'PCP'),
    ('P3',  'Troca de Jig e Dispositivo',                              'Processo',         U&'Eng\00AA Processo'),
    ('P4',  U&'Falta de Documenta\00E7\00E3o',                         'Processo',         'Manufatura'),
    ('P5',  U&'Confer\00EAncia de Material',                           'Processo',         'Almoxarifado'),
    ('P6',  'Falta de Jig ou Dispositivo',                             'Processo',         U&'Eng\00AA Processo'),
    ('P7',  'Curva de Crescimento (Ramp Up)',                          'Processo',         U&'Eng\00AA Processo'),
    ('P8',  U&'Meta em An\00E1lise da Engenharia',                     'Processo',         U&'Eng\00AA Processo'),
    ('P9',  U&'Valida\00E7\00E3o de Jig',                              'Processo',         U&'Eng\00AA Processo'),
    ('P10', 'Falta de Ferro de Soldar',                                'Processo',         U&'Eng\00AA Processo'),
    ('P11', 'Problema com o Ferro de Soldar',                          'Processo',         U&'Eng\00AA Processo'),
    ('P12', U&'Falta de Insumos (Alicate, Pin\00E7a, etc.)',           'Processo',         U&'Eng\00AA Processo'),
    ('P13', 'Ajuste no Layout',                                        'Processo',         U&'Eng\00AA Processo'),
    ('P14', 'Balanceamento',                                           'Processo',         U&'Eng\00AA Processo'),
    ('P15', U&'Atraso de Produ\00E7\00E3o',                            'Processo',         'Manufatura'),
    ('P16', 'Retrabalho',                                              'Processo',         'Manufatura'),
    ('P17', 'Revisando Material Acumulado',                            'Processo',         'Manufatura'),
    ('P18', U&'Falta de Balan\00E7a',                                  'Processo',         U&'Eng\00AA Processo'),
    ('P19', U&'Retirando Ac\00FAmulo',                                 'Processo',         'Manufatura'),
    ('P20', 'Recuperando Metas',                                       'Processo',         'Manufatura'),
    ('P22', U&'Mudan\00E7a de Plano de Voo',                           'Processo',         'PCP'),
    ('P23', 'Produzido Maior que a Meta',                              'Processo',         'Manufatura'),
    ('P24', U&'Aplica\00E7\00E3o do Verniz',                           'Processo',         'Manufatura'),
    ('P25', 'Limpeza de Noozle',                                       'Processo',         'Manufatura'),
    ('P26', U&'Alimenta\00E7\00E3o de Linha',                          'Processo',         'Manufatura'),

-- ── SETUP ────────────────────────────────────────────────────────────────────
    ('S1',  'Troca de Setup (Produto)',                                 'Setup',            'PCP'),
    ('S2',  U&'Valida\00E7\00E3o do Processo',                         'Setup',            'Manufatura'),
    ('S3',  'NPI',                                                     'NPI',              U&'PCP / Eng\00AA Produto'),
    ('S4',  U&'Setup N\00E3o Planejado',                               'Setup',            'PCP'),
    ('S5',  'Preenchimento de Processo',                               'Setup',            'Manufatura'),

-- ── TECNOLOGIA ───────────────────────────────────────────────────────────────
    ('T1',  U&'Falha de Impress\00E3o do QR Code',                     'Tecnologia',       'TI'),
    ('T2',  'Falta de Monitor',                                        'Tecnologia',       'TI'),
    ('T3',  'Falta de Scanner',                                        'Tecnologia',       'TI'),
    ('T4',  'Sistema Inoperante',                                      'Tecnologia',       'TI'),
    ('T5',  'Falta de Impressora',                                     'Tecnologia',       'TI');
