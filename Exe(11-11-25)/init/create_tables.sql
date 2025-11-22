CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    date DATE,
    warehouse VARCHAR(50),
    client_type VARCHAR(50),
    product_line VARCHAR(100),
    quantity INTEGER,
    unit_price NUMERIC(10,2),
    total NUMERIC(10,2),
    payment VARCHAR(50)
);
