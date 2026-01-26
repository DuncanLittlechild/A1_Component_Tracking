CREATE TABLE IF NOT EXISTS stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (LENGTH(name) <= 50),
    restock_quantity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS location_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (LENGTH(name) <= 50)
);

CREATE TABLE IF NOT EXISTS current_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    current_quantity INTEGER NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stock_data(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES location_data(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    stock_name TEXT NOT NULL CHECK (LENGTH(stock_name) <= 50),
    location_id INTEGER NOT NULL,
    location_name TEXT NOT NULL CHECK (LENGTH(location_name) <= 50),
    activity_type TEXT CHECK (activity_type IN ('Created', 'Removed', 'Updated')),
    update_details TEXT CHECK (update_details IN ('N/A', 'Location', 'Quantity', 'Both')) DEFAULT ('N/A'),
    quantity_change INTEGER,
    date_occured TEXT NOT NULL CHECK (date_occured LIKE "%-%-% %:%:%") DEFAULT (datetime('now')),
    FOREIGN KEY (stock_id) REFERENCES stock_data(id)
);