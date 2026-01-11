CREATE TABLE IF NOT EXISTS stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (LENGTH(name) <= 50),
    base_quantity INTEGER NOT NULL,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,data._stock_type._name, data._location._name, data._stock_type._name
    stock_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    activity_type TEXT CHECK (activity_type IN ('Created', 'Removed', 'Updated')),
    update_details TEXT CHECK details IN ('N/A', 'Location', 'Quantity') DEFAULT ('N/A')
    quantity_change INTEGER,
    date_occured TEXT NOT NULL CHECK (date_occured LIKE "%-%-% %:%:%") DEFAULT (datetime('now'))
    FOREIGN KEY (stock_id) REFERENCES stock_data(id)
);