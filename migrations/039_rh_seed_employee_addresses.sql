-- Cria users inativos + user_profiles com endereços de Manaus
-- para os 25 funcionários seed (chapas 9001–9025).
-- Usuários ficam is_active = FALSE (não conseguem fazer login).
-- Idempotente: WHERE NOT EXISTS + ON CONFLICT DO UPDATE.

INSERT INTO users (
    username, email, full_name, matricula, setor,
    password_hash, provider, is_active, is_admin, user_type, employee_id
)
SELECT
    'seed_' || e.employee_code,
    e.employee_code || '@seed.venttos.local',
    e.full_name,
    e.employee_code,
    e.department,
    NULL,
    'local',
    FALSE,
    FALSE,
    'CLT',
    e.id
FROM employees e
WHERE e.employee_code IN (
    '9001','9002','9003','9004','9005',
    '9006','9007','9008','9009','9010',
    '9011','9012','9013','9014','9015',
    '9016','9017','9018','9019','9020',
    '9021','9022','9023','9024','9025'
)
AND NOT EXISTS (
    SELECT 1 FROM users u WHERE u.employee_id = e.id
);

WITH addr (code, street, number, neighborhood, zip) AS (
    VALUES
    ('9001', 'Av. Recife',               '127', 'Compensa',                 '69035-005'),
    ('9002', 'Rua Ajuricaba',            '45',  'São Jorge',                '69036-030'),
    ('9003', 'Av. Paraíba',              '89',  'Presidente Vargas',        '69025-010'),
    ('9004', 'Rua Coaracy Nunes',        '312', 'Compensa',                 '69035-180'),
    ('9005', 'Rua Nael Pinheiro',        '78',  'Nova Esperança',           '69049-060'),
    ('9006', 'Rua Floriano Peixoto',     '156', 'Centro',                   '69020-080'),
    ('9007', 'Rua Júlio Moreira',        '33',  'Colônia Oliveira Machado', '69043-090'),
    ('9008', 'Rua João Alfredo',         '67',  'Praça 14',                 '69040-040'),
    ('9009', 'Rua 13 de Setembro',       '201', 'Flores',                   '69058-020'),
    ('9010', 'Rua Santos Dumont',        '415', 'São Jorge',                '69036-060'),
    ('9011', 'Rua Lauro Cavalcante',     '88',  'Nova Esperança',           '69049-100'),
    ('9012', 'Av. Constantino Nery',     '789', 'Chapada',                  '69050-000'),
    ('9013', 'Rua Leonardo Malcher',     '344', 'São Francisco',            '69010-080'),
    ('9014', 'Rua Manaus Moderna',       '55',  'Educandos',                '69065-020'),
    ('9015', 'Rua Rio Branco',           '193', 'Centro',                   '69010-050'),
    ('9016', 'Rua Álvaro Maia',          '66',  'Cidade Nova',              '69095-170'),
    ('9017', 'Rua Ipiranga',             '142', 'Cachoeirinha',             '69065-590'),
    ('9018', 'Rua Belém',                '78',  'Aleixo',                   '69060-020'),
    ('9019', 'Rua Coari',                '254', 'Petrópolis',               '69055-010'),
    ('9020', 'Av. Mário Ypiranga',       '39',  'Adrianópolis',             '69057-001'),
    ('9021', 'Rua Manicoré',             '115', 'São Geraldo',              '69053-110'),
    ('9022', 'Rua Codajás',              '487', 'Dom Pedro',                '69040-100'),
    ('9023', 'Av. Djalma Batista',       '982', 'Chapada',                  '69050-010'),
    ('9024', 'Rua do Aleixo',            '201', 'Aleixo',                   '69060-080'),
    ('9025', 'Rua Curuçá',               '33',  'Planalto',                 '69040-290')
)
INSERT INTO user_profiles (user_id, street, number, neighborhood, city, state, zip_code)
SELECT
    u.id,
    a.street,
    a.number,
    a.neighborhood,
    'Manaus',
    'AM',
    a.zip
FROM users u
JOIN employees e ON e.id = u.employee_id
JOIN addr a ON a.code = e.employee_code
WHERE e.employee_code IN (
    '9001','9002','9003','9004','9005',
    '9006','9007','9008','9009','9010',
    '9011','9012','9013','9014','9015',
    '9016','9017','9018','9019','9020',
    '9021','9022','9023','9024','9025'
)
ON CONFLICT (user_id) DO UPDATE SET
    street       = EXCLUDED.street,
    number       = EXCLUDED.number,
    neighborhood = EXCLUDED.neighborhood,
    city         = EXCLUDED.city,
    state        = EXCLUDED.state,
    zip_code     = EXCLUDED.zip_code;
