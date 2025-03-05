CREATE TABLE IF NOT EXISTS books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    genre VARCHAR(100),
    isbn VARCHAR(20) UNIQUE,
    price DECIMAL(10, 2),
    quantity INTEGER
);


CREATE OR REPLACE FUNCTION clear_books_table_func()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE books RESTART IDENTITY CASCADE;
    RAISE NOTICE 'Таблица books успешно очищена.';
END;
$$;


CREATE OR REPLACE FUNCTION add_new_book_func(
    _title VARCHAR(255),
    _author VARCHAR(255),
    _genre VARCHAR(100),
    _isbn VARCHAR(20),
    _price DECIMAL(10, 2),
    _quantity INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO books (title, author, genre, isbn, price, quantity)
    VALUES (_title, _author, _genre, _isbn, _price, _quantity);
    RAISE NOTICE 'Книга "%" успешно добавлена.', _title;
END;
$$;


CREATE OR REPLACE FUNCTION search_books_by_title_func(_search_title VARCHAR(255))
RETURNS TABLE (
    book_id INTEGER,
    title VARCHAR(255),
    author VARCHAR(255),
    genre VARCHAR(100),
    isbn VARCHAR(20),
    price DECIMAL(10, 2),
    quantity INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT b.book_id, b.title, b.author, b.genre, b.isbn, b.price, b.quantity
    FROM books b
    WHERE b.title ILIKE '%' || _search_title || '%';
END;
$$;


CREATE OR REPLACE FUNCTION update_book_info_func(
    _book_id INTEGER,
    _title VARCHAR(255),
    _author VARCHAR(255),
    _genre VARCHAR(100),
    _isbn VARCHAR(20),
    _price DECIMAL(10, 2),
    _quantity INTEGER
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE books
    SET title = _title,
        author = _author,
        genre = _genre,
        isbn = _isbn,
        price = _price,
        quantity = _quantity
    WHERE book_id = _book_id;
    RAISE NOTICE 'Информация о книге с ID % обновлена.', _book_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Книга с ID % не найдена.', _book_id;
    END IF;
END;
$$;


CREATE OR REPLACE FUNCTION delete_book_by_title_func(_title_to_delete VARCHAR(255))
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM books
    WHERE title ILIKE '%' || _title_to_delete || '%';
    RAISE NOTICE 'Книги с названием, содержащим "%", удалены.', _title_to_delete;
    IF NOT FOUND THEN
        RAISE NOTICE 'Книги с названием, содержащим "%", не найдены для удаления.', _title_to_delete;
    END IF;
END;
$$;