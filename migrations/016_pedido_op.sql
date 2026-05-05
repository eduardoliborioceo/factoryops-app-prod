CREATE TABLE IF NOT EXISTS pedido_op (
    pedido_id INTEGER NOT NULL REFERENCES pedido_cliente(id) ON DELETE CASCADE,
    op_id     INTEGER NOT NULL REFERENCES controle_ops(id)   ON DELETE CASCADE,
    PRIMARY KEY (pedido_id, op_id)
);
