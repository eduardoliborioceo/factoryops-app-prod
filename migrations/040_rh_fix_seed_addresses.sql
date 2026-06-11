-- Corrige endereços dos 25 funcionários seed (chapas 9001–9025).
-- Substitui ruas fictícias por avenidas principais de Manaus
-- que existem no OpenStreetMap e são geocodificáveis via Nominatim.
-- Idempotente: ON CONFLICT (user_id) DO UPDATE.

WITH addr (code, street, number, neighborhood, zip) AS (
    VALUES
    ('9001', 'Avenida Constantino Nery',          '1234', 'Chapada',               '69050-000'),
    ('9002', 'Avenida Djalma Batista',             '2100', 'Parque Dez de Novembro','69055-000'),
    ('9003', 'Avenida Torquato Tapajós',           '7200', 'Dom Pedro',             '69040-000'),
    ('9004', 'Avenida Ephigênio Salles',           '1500', 'Parque Dez de Novembro','69055-010'),
    ('9005', 'Avenida Mário Ypiranga Monteiro',    '2000', 'Adrianópolis',          '69057-001'),
    ('9006', 'Avenida Sete de Setembro',           '800',  'Centro',                '69005-141'),
    ('9007', 'Avenida Eduardo Ribeiro',            '520',  'Centro',                '69010-001'),
    ('9008', 'Avenida Recife',                     '500',  'Compensa',              '69035-005'),
    ('9009', 'Avenida Grande Circular',            '1000', 'Flores',                '69058-000'),
    ('9010', 'Avenida Autaz Mirim',                '3500', 'Coroado',               '69083-000'),
    ('9011', 'Avenida Max Teixeira',               '2800', 'Nova Cidade',           '69097-000'),
    ('9012', 'Avenida Cosme Ferreira',             '4000', 'São José Operário',     '69083-010'),
    ('9013', 'Avenida Rodrigo Otávio',             '3000', 'Japiim',                '69077-000'),
    ('9014', 'Avenida Brasil',                     '400',  'Centro',                '69010-035'),
    ('9015', 'Avenida Getúlio Vargas',             '260',  'Centro',                '69025-030'),
    ('9016', 'Avenida Nações Unidas',              '1100', 'Chapada',               '69050-020'),
    ('9017', 'Avenida André Araújo',               '1500', 'Aleixo',                '69060-001'),
    ('9018', 'Avenida Mário Ypiranga Monteiro',    '3200', 'Adrianópolis',          '69057-060'),
    ('9019', 'Avenida Djalma Batista',             '690',  'Chapada',               '69050-010'),
    ('9020', 'Avenida Constantino Nery',           '3000', 'Chapada',               '69050-001'),
    ('9021', 'Avenida Torquato Tapajós',           '4800', 'Dom Pedro',             '69040-020'),
    ('9022', 'Avenida Brasil',                     '650',  'Centro',                '69010-036'),
    ('9023', 'Avenida Autaz Mirim',                '5600', 'Coroado',               '69083-012'),
    ('9024', 'Avenida Recife',                     '1300', 'Compensa',              '69035-010'),
    ('9025', 'Avenida Ephigênio Salles',           '800',  'Parque Dez de Novembro','69055-005')
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
