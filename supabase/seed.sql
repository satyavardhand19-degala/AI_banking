-- Vaani AI Banking Intelligence — Seed Data

-- 1. Insert Customers
INSERT INTO customers (name, email, phone) VALUES
('Arun Kumar', 'arun.kumar@example.com', '+91 98765 43210'),
('Priya Sharma', 'priya.sharma@example.com', '+91 87654 32109'),
('Vikram Singh', 'vikram.singh@example.com', '+91 76543 21098'),
('Anjali Gupta', 'anjali.gupta@example.com', '+91 65432 10987'),
('Rohan Mehta', 'rohan.mehta@example.com', '+91 54321 09876');

-- 2. Insert Accounts
INSERT INTO accounts (customer_id, account_number, account_type, balance) VALUES
(1, '5001', 'savings', 75000.00),
(1, '5002', 'current', 125000.00),
(2, '6001', 'savings', 45000.00),
(3, '7001', 'savings', 320000.00),
(3, '7002', 'fixed_deposit', 500000.00),
(4, '8001', 'current', 15000.00),
(5, '9001', 'savings', 22000.00),
(5, '9002', 'savings', 8000.00),
(2, '6002', 'current', 95000.00),
(4, '8002', 'savings', 55000.00);

-- 3. Insert Transactions (Mix of dates)
-- Transactions for today
INSERT INTO transactions (account_id, transaction_type, amount, description, created_at) VALUES
(1, 'credit', 15000.00, 'Monthly Salary', NOW()),
(3, 'debit', 25000.00, 'Rent Payment', NOW()),
(6, 'credit', 12000.00, 'Freelance Project', NOW());

-- Transactions this week
INSERT INTO transactions (account_id, transaction_type, amount, description, created_at) VALUES
(2, 'debit', 65000.00, 'Laptop Purchase', NOW() - INTERVAL '2 days'),
(4, 'credit', 50000.00, 'Fixed Deposit Interest', NOW() - INTERVAL '3 days'),
(9, 'debit', 12000.00, 'Insurance Premium', NOW() - INTERVAL '4 days'),
(7, 'credit', 4500.00, 'Refund', NOW() - INTERVAL '5 days');

-- Large transactions (> 50,000)
INSERT INTO transactions (account_id, transaction_type, amount, description, created_at) VALUES
(4, 'credit', 100000.00, 'Bonus Payment', NOW() - INTERVAL '10 days'),
(5, 'debit', 75000.00, 'Home Renovation', NOW() - INTERVAL '15 days');

-- Older transactions
INSERT INTO transactions (account_id, transaction_type, amount, description, created_at) VALUES
(1, 'debit', 2000.00, 'Grocery Store', NOW() - INTERVAL '20 days'),
(2, 'debit', 500.00, 'Coffee Shop', NOW() - INTERVAL '22 days'),
(3, 'credit', 10000.00, 'Gift', NOW() - INTERVAL '25 days'),
(8, 'debit', 3500.00, 'Electricity Bill', NOW() - INTERVAL '30 days');

-- More realistic data spread
INSERT INTO transactions (account_id, transaction_type, amount, description, created_at)
SELECT 
    (random() * 9 + 1)::int, 
    CASE WHEN random() > 0.5 THEN 'credit' ELSE 'debit' END,
    (random() * 20000 + 100)::numeric(15,2),
    'Auto-generated transaction',
    NOW() - (random() * INTERVAL '60 days')
FROM generate_series(1, 40);
