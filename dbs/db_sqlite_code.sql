CREATE TABLE IF NOT EXISTS stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (LENGTH(name) <= 50),
    base_quantity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS location_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (LENGTH(name) <= 50),
);

CREATE TABLE IF NOT EXISTS stock_ids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_data_id INTEGER NOT NULL,
    FOREIGN KEY (stock_data_id) REFERENCES stock_data(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS current_inventory (
    stock_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    current_quantity INTEGER NOT NULL,
    occured_at TEXT CHECK (occured_at LIKE '%-%-%, %:%:%'),
    FOREIGN KEY (stock_id) REFERENCES stock_ids(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES location_data(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    activity_type TEXT CHECK (activity_type IN ('Created', 'Removed', 'Updated')),
    quantity_change INTEGER,
    FOREIGN KEY (stock_id) REFERENCES stock_ids(id) ON DELETE CASCADE
);