\c book_shop

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) CHECK(category IN ('book', 'stationery', 'souvenir')),
    price DECIMAL(10,2),
    stock INT,
    description TEXT
);

GRANT ALL PRIVILEGES ON TABLE products TO admin;
GRANT SELECT ON TABLE products TO guest;