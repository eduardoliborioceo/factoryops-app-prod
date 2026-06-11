-- Configurações de transporte por turno: regras de descida, raio e tolerâncias.

CREATE TABLE rh_turno_config (
    id                  SERIAL PRIMARY KEY,
    turno               VARCHAR(10)   NOT NULL,
    filial              VARCHAR(100)  NOT NULL DEFAULT 'VTT',
    tipo_descida        VARCHAR(30)   NOT NULL DEFAULT 'agrupado',
    raio_embarque_m     INTEGER       NOT NULL DEFAULT 500,
    tolerancia_min      SMALLINT      NOT NULL DEFAULT 10,
    horario_saida       TIME,
    observacao          TEXT,
    ativo               BOOLEAN       NOT NULL DEFAULT TRUE,
    criado_em           TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    atualizado_em       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT rh_turno_config_uq UNIQUE (turno, filial)
);

-- Defaults para os três turnos da filial VTT
INSERT INTO rh_turno_config (turno, filial, tipo_descida, raio_embarque_m, tolerancia_min, horario_saida)
VALUES
  ('1', 'VTT', 'agrupado',    500, 10, '05:45'),
  ('2', 'VTT', 'porta_a_porta', 500, 10, '13:45'),
  ('3', 'VTT', 'porta_a_porta', 500, 10, '21:45');
