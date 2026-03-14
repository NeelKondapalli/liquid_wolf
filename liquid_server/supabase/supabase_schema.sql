-- Users table
-- Stores basic user information, identified by phone number
CREATE TABLE users (
    phone_number VARCHAR(20) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Liquid Keys table
-- Stores Liquid API credentials for users who have provided them
CREATE TABLE liquid_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) NOT NULL REFERENCES users(phone_number) ON DELETE CASCADE,
    api_key VARCHAR(255) NOT NULL, -- lq_... format
    api_secret TEXT NOT NULL, -- Encrypted/hashed in production
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(phone_number) -- One set of keys per user
);

-- Create indexes for faster queries
-- Note: phone_number already has an implicit index from UNIQUE constraint
CREATE INDEX idx_liquid_keys_active ON liquid_keys(phone_number, is_active);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE liquid_keys ENABLE ROW LEVEL SECURITY;

-- RLS Policies (adjust based on your auth setup)
-- Users can only read their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.jwt()->>'phone' = phone_number);

-- Users can only view their own keys
CREATE POLICY "Users can view own keys" ON liquid_keys
    FOR SELECT USING (auth.jwt()->>'phone' = phone_number);

-- Service role can do everything (for your backend)
CREATE POLICY "Service role has full access to users" ON users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to keys" ON liquid_keys
    FOR ALL USING (auth.role() = 'service_role');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to auto-update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_liquid_keys_updated_at
    BEFORE UPDATE ON liquid_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
