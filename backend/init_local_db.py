"""
Vaani AI Banking Intelligence — Local SQLite Database Initializer

Creates and seeds a local SQLite database with realistic banking data.
Run: python init_local_db.py
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = "local_vault.db"


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Schema ──
    print("Creating tables...")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
        account_number TEXT UNIQUE NOT NULL,
        account_type TEXT NOT NULL CHECK (account_type IN ('savings','current','fixed_deposit')),
        balance NUMERIC(15,2) NOT NULL DEFAULT 0.00,
        status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive','frozen')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ('credit','debit')),
        amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ── Indexes ──
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_account_id ON transactions(account_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_created_at ON transactions(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_txn_amount ON transactions(amount)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_acc_customer_id ON accounts(customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_acc_number ON accounts(account_number)')

    # ── Seed: Customers ──
    print("Seeding 5 customers...")
    customers = [
        ('Arun Kumar', 'arun.kumar@example.com', '+91 98765 43210'),
        ('Priya Sharma', 'priya.sharma@example.com', '+91 87654 32109'),
        ('Vikram Singh', 'vikram.singh@example.com', '+91 76543 21098'),
        ('Anjali Gupta', 'anjali.gupta@example.com', '+91 65432 10987'),
        ('Rohan Mehta', 'rohan.mehta@example.com', '+91 54321 09876')
    ]
    cursor.executemany('INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)', customers)

    # ── Seed: Accounts ──
    print("Seeding 10 accounts...")
    accounts = [
        (1, '5001', 'savings', 75000.00),
        (1, '5002', 'current', 125000.00),
        (2, '6001', 'savings', 45000.00),
        (3, '7001', 'savings', 320000.00),
        (3, '7002', 'fixed_deposit', 500000.00),
        (4, '8001', 'current', 15000.00),
        (5, '9001', 'savings', 22000.00),
        (5, '9002', 'savings', 8000.00),
        (2, '6002', 'current', 95000.00),
        (4, '8002', 'savings', 55000.00)
    ]
    cursor.executemany(
        'INSERT INTO accounts (customer_id, account_number, account_type, balance) VALUES (?, ?, ?, ?)',
        accounts
    )

    # ── Seed: Transactions (60 total) ──
    print("Seeding 60 transactions...")
    now = datetime.now()

    # 20 hand-crafted transactions with realistic descriptions and varied amounts
    static_txns = [
        # Today's transactions
        (1, 'credit', 15000.00, 'Monthly Salary Credit', now.strftime('%Y-%m-%d %H:%M:%S')),
        (3, 'debit', 25000.00, 'Rent Payment - April', now.strftime('%Y-%m-%d %H:%M:%S')),
        (6, 'credit', 12000.00, 'Freelance Project Payment', now.strftime('%Y-%m-%d %H:%M:%S')),
        (7, 'credit', 8500.00, 'Online Sale Revenue', now.strftime('%Y-%m-%d %H:%M:%S')),
        (10, 'debit', 3200.00, 'Mobile Recharge & Broadband', now.strftime('%Y-%m-%d %H:%M:%S')),

        # This week transactions
        (2, 'debit', 65000.00, 'Laptop Purchase - Amazon', (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')),
        (4, 'credit', 55000.00, 'Fixed Deposit Interest Q4', (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')),
        (9, 'debit', 12000.00, 'Health Insurance Premium', (now - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')),
        (7, 'credit', 4500.00, 'GST Refund', (now - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')),
        (1, 'debit', 18000.00, 'EMI Payment - Car Loan', (now - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')),

        # Large transactions (> 50,000)
        (4, 'credit', 100000.00, 'Annual Bonus Credit', (now - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')),
        (5, 'debit', 75000.00, 'Home Renovation Payment', (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')),
        (2, 'credit', 85000.00, 'Consulting Fee Received', (now - timedelta(days=12)).strftime('%Y-%m-%d %H:%M:%S')),
        (3, 'debit', 62000.00, 'Gold Jewelry Purchase', (now - timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')),

        # Older transactions
        (1, 'debit', 2000.00, 'Grocery Store - BigBasket', (now - timedelta(days=18)).strftime('%Y-%m-%d %H:%M:%S')),
        (2, 'debit', 550.00, 'Coffee Shop - Starbucks', (now - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S')),
        (3, 'credit', 10000.00, 'Birthday Gift from Parent', (now - timedelta(days=25)).strftime('%Y-%m-%d %H:%M:%S')),
        (8, 'debit', 3500.00, 'Electricity Bill - Q3', (now - timedelta(days=28)).strftime('%Y-%m-%d %H:%M:%S')),
        (6, 'credit', 45000.00, 'Salary Credit - March', (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')),
        (10, 'debit', 7800.00, 'School Fee Payment', (now - timedelta(days=35)).strftime('%Y-%m-%d %H:%M:%S')),
    ]
    cursor.executemany(
        'INSERT INTO transactions (account_id, transaction_type, amount, description, created_at) VALUES (?, ?, ?, ?, ?)',
        static_txns
    )

    # 40 random transactions to reach 60 total
    descriptions_credit = [
        'Salary Credit', 'Investment Return', 'Refund Received', 'Interest Credit',
        'Freelance Payment', 'Dividend Income', 'Gift Received', 'Cashback Reward',
        'Rental Income', 'Commission Earned', 'Tax Refund', 'Insurance Claim'
    ]
    descriptions_debit = [
        'ATM Withdrawal', 'Online Shopping', 'Utility Bill', 'Restaurant Payment',
        'Fuel Purchase', 'Medical Expense', 'Subscription Fee', 'Travel Booking',
        'Grocery Purchase', 'Gym Membership', 'Phone Bill', 'Loan EMI Payment'
    ]

    for _ in range(40):
        acc_id = random.randint(1, 10)
        txn_type = random.choice(['credit', 'debit'])

        # Mix of amount ranges: small (100-5000), medium (5000-20000), large (20000-80000)
        range_choice = random.random()
        if range_choice < 0.4:
            amt = round(random.uniform(100, 5000), 2)
        elif range_choice < 0.8:
            amt = round(random.uniform(5000, 20000), 2)
        else:
            amt = round(random.uniform(20000, 80000), 2)

        days_ago = random.randint(0, 55)
        dt = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

        desc = random.choice(descriptions_credit if txn_type == 'credit' else descriptions_debit)

        cursor.execute(
            'INSERT INTO transactions (account_id, transaction_type, amount, description, created_at) VALUES (?, ?, ?, ?, ?)',
            (acc_id, txn_type, amt, desc, dt)
        )

    conn.commit()

    # ── Verification ──
    cursor.execute("SELECT COUNT(*) FROM customers")
    cust_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM accounts")
    acc_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM transactions")
    txn_count = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(amount) FROM transactions")
    max_amt = cursor.fetchone()[0]

    conn.close()

    print(f"\n✓ Database initialized: {DB_PATH}")
    print(f"  Customers:    {cust_count}")
    print(f"  Accounts:     {acc_count}")
    print(f"  Transactions: {txn_count}")
    print(f"  Max amount:   ₹{max_amt:,.2f}")


if __name__ == "__main__":
    init_db()
