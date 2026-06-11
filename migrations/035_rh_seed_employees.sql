-- Seed data: 25 colaboradores fictícios para testes de rotas de transporte em Manaus.
-- Matrícula range 9001–9025 (separado das chapas reais da planilha de funcionários).
-- Execute uma única vez. Ao importar os dados reais, estes registros podem ser removidos.

INSERT INTO employees (employee_code, full_name, job_title, department, hired_at, status, branch_name)
VALUES
  ('9001', 'Carlos Eduardo Santos',   'Operador de Produção',             'Produção',     '2021-03-15', 'ACTIVE', 'VTT'),
  ('9002', 'Ana Paula Ferreira',       'Técnica de Manutenção',            'Manutenção',   '2020-07-10', 'ACTIVE', 'VTT'),
  ('9003', 'João Roberto Oliveira',    'Analista de Qualidade',            'Qualidade',    '2022-01-20', 'ACTIVE', 'VTT'),
  ('9004', 'Maria Claudia Lima',       'Auxiliar de Logística',            'Logística',    '2021-11-05', 'ACTIVE', 'VTT'),
  ('9005', 'Pedro Henrique Costa',     'Supervisor de Produção',           'Produção',     '2019-04-22', 'ACTIVE', 'VTT'),
  ('9006', 'Fernanda Cristina Souza',  'Inspetora de Qualidade',           'Qualidade',    '2022-08-18', 'ACTIVE', 'VTT'),
  ('9007', 'Lucas Rodrigues Alves',    'Operador de SMD',                  'Produção',     '2023-02-14', 'ACTIVE', 'VTT'),
  ('9008', 'Juliana Silva Martins',    'Analista de Planejamento',         'Planejamento', '2020-09-30', 'ACTIVE', 'VTT'),
  ('9009', 'Marcos Antônio Pereira',   'Técnico em Eletrônica',            'Manutenção',   '2021-06-12', 'ACTIVE', 'VTT'),
  ('9010', 'Renata Gomes Vieira',      'Auxiliar Administrativo',          'RH',           '2022-04-07', 'ACTIVE', 'VTT'),
  ('9011', 'Anderson Lima Cruz',       'Operador de Produção',             'Produção',     '2023-05-19', 'ACTIVE', 'VTT'),
  ('9012', 'Tatiana Mendes Barbosa',   'Técnica de Segurança do Trabalho', 'Segurança',    '2021-08-25', 'ACTIVE', 'VTT'),
  ('9013', 'Rodrigo Cardoso Nunes',    'Engenheiro de Processo',           'Engenharia',   '2020-03-11', 'ACTIVE', 'VTT'),
  ('9014', 'Carla Helena Ribeiro',     'Operadora de SMD',                 'Produção',     '2022-10-03', 'ACTIVE', 'VTT'),
  ('9015', 'Diego Ferreira Borges',    'Técnico de Manutenção',            'Manutenção',   '2023-01-09', 'ACTIVE', 'VTT'),
  ('9016', 'Simone Aparecida Castro',  'Analista de Qualidade',            'Qualidade',    '2021-02-28', 'ACTIVE', 'VTT'),
  ('9017', 'Rafael Augusto Monteiro',  'Auxiliar de Logística',            'Logística',    '2020-11-16', 'ACTIVE', 'VTT'),
  ('9018', 'Eliane Cristina Moraes',   'Operadora de Produção',            'Produção',     '2022-07-21', 'ACTIVE', 'VTT'),
  ('9019', 'Thiago Henrique Pinto',    'Operador de CNC',                  'Produção',     '2023-03-08', 'ACTIVE', 'VTT'),
  ('9020', 'Vanessa Santos Azevedo',   'Analista de RH',                   'RH',           '2021-09-14', 'ACTIVE', 'VTT'),
  ('9021', 'Edmilson Rocha Junior',    'Supervisor de Manutenção',         'Manutenção',   '2019-12-01', 'ACTIVE', 'VTT'),
  ('9022', 'Gabriela Matos Leal',      'Inspetora de Qualidade',           'Qualidade',    '2022-05-26', 'ACTIVE', 'VTT'),
  ('9023', 'Wagner Souza Teixeira',    'Operador de Produção',             'Produção',     '2023-06-17', 'ACTIVE', 'VTT'),
  ('9024', 'Cristiane Duarte Campos',  'Técnica em Eletrônica',            'Manutenção',   '2020-08-04', 'ACTIVE', 'VTT'),
  ('9025', 'Fábio Luiz Corrêa',        'Engenheiro de Qualidade',          'Qualidade',    '2021-05-10', 'ACTIVE', 'VTT');
