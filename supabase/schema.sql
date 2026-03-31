-- Vaani AI Banking Intelligence — Database Schema

-- 1. Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('savings','current','fixed_deposit')),
    balance NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','frozen')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('credit','debit')),
    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Indexes for performance
CREATE INDEX IF NOT EXISTS idx_txn_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_txn_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_txn_amount ON transactions(amount);
CREATE INDEX IF NOT EXISTS idx_acc_customer_id ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_acc_number ON accounts(account_number);
