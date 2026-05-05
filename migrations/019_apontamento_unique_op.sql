DROP INDEX IF EXISTS uq_apontamento_grupo;
DROP INDEX IF EXISTS uq_apontamento;

CREATE UNIQUE INDEX uq_apontamento
    ON apontamento (data, turno, modelo, linha, op_id, COALESCE(fase, ''));
