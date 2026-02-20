DROP TABLE IF EXISTS Item;

CREATE TABLE IF NOT EXISTS Item (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    low_level INTEGER NOT NULL DEFAULT 5,

-- CHECK here prevents an attribute from turning negative. 
    CHECK (stock >= 0)
);

-- Adding items to db. These are the original values, check after changes from your *.py programme
INSERT INTO Item (name, stock, low_level) VALUES
('Pencils', 10, 5),
('Notebooks', 3, 5),
('Erasers', 0, 2);