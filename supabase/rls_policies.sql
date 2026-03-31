-- Vaani AI Banking Intelligence — Row Level Security

-- 1. Enable RLS on all tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- 2. Create Policy for service_role (Full Access)
CREATE POLICY "service_role_full_access_customers" ON customers FOR ALL TO service_role USING (true);
CREATE POLICY "service_role_full_access_accounts" ON accounts FOR ALL TO service_role USING (true);
CREATE POLICY "service_role_full_access_transactions" ON transactions FOR ALL TO service_role USING (true);

-- 3. Create banking_readonly role and grant SELECT
-- Note: In Supabase, you usually use policies and the service_role for this
-- This script creates a read-only policy for any authenticated/anon role if needed,
-- but the specifications emphasize read-only SELECT via service_role.

CREATE POLICY "readonly_select_customers" ON customers FOR SELECT TO authenticated, anon USING (true);
CREATE POLICY "readonly_select_accounts" ON accounts FOR SELECT TO authenticated, anon USING (true);
CREATE POLICY "readonly_select_transactions" ON transactions FOR SELECT TO authenticated, anon USING (true);
