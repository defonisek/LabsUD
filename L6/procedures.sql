\c book_shop

CREATE OR REPLACE PROCEDURE truncate_products()
LANGUAGE SQL
AS $$
    TRUNCATE TABLE products;
$$;

GRANT EXECUTE ON PROCEDURE truncate_products() TO admin;

CREATE OR REPLACE FUNCTION add_product(
    p_name VARCHAR(100),
    p_category VARCHAR(50),
    p_price DECIMAL(10,2),
    p_stock INT,
    p_description TEXT
) RETURNS VOID AS $$
    INSERT INTO products(name, category, price, stock, description)
    VALUES (p_name, p_category, p_price, p_stock, p_description);
$$ LANGUAGE SQL;

GRANT EXECUTE ON FUNCTION add_product TO admin;

CREATE OR REPLACE FUNCTION search_products(search_term TEXT)
RETURNS SETOF products AS $$
    SELECT * FROM products 
    WHERE name ILIKE '%' || search_term || '%';
$$ LANGUAGE SQL;

GRANT EXECUTE ON FUNCTION search_products TO guest, admin;

CREATE OR REPLACE FUNCTION update_product(
    p_id INT,
    p_name VARCHAR(100),
    p_price DECIMAL(10,2),
    p_stock INT
) RETURNS VOID AS $$
    UPDATE products
    SET name = p_name,
        price = p_price,
        stock = p_stock
    WHERE id = p_id;
$$ LANGUAGE SQL;

GRANT EXECUTE ON FUNCTION update_product TO admin;

CREATE OR REPLACE FUNCTION delete_by_name(p_name TEXT)
RETURNS VOID AS $$
    DELETE FROM products
    WHERE name = p_name;
$$ LANGUAGE SQL;

GRANT EXECUTE ON FUNCTION delete_by_name TO admin;

CREATE OR REPLACE PROCEDURE create_user(
    username TEXT,
    password TEXT,
    is_admin BOOLEAN
)
SECURITY DEFINER
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('CREATE ROLE %I WITH LOGIN PASSWORD %L', username, password);
    IF is_admin THEN
        EXECUTE format('GRANT admin TO %I', username);
    ELSE
        EXECUTE format('GRANT guest TO %I', username);
    END IF;
END;
$$;

GRANT EXECUTE ON PROCEDURE create_user TO admin;