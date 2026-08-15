CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_date TEXT,
    transaction_date TEXT,
    transaction_amount REAL,
    surcharge_amount REAL,
    bank_transaction_id TEXT,
    transaction_status TEXT,
    bank_name TEXT,
    payment_method TEXT,
    card_holder_name TEXT,
    email TEXT,
    mobile TEXT,
    address TEXT,
    transaction_description TEXT
);

CREATE INDEX IF NOT EXISTS idx_transactions_date
ON transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_transactions_amount
ON transactions(transaction_amount);

CREATE INDEX IF NOT EXISTS idx_transactions_bank_id
ON transactions(bank_transaction_id);
