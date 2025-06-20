-- Initialize database schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'unknown',
    last_checked TIMESTAMP,
    response_time REAL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create health_checks table
CREATE TABLE IF NOT EXISTS health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    response_time REAL,
    status_code INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create services table for project bridge
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    path_prefix VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    auth_required BOOLEAN DEFAULT false,
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create request_logs table
CREATE TABLE IF NOT EXISTS request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    status_code INTEGER,
    response_time REAL,
    user_agent TEXT,
    ip_address INET,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_health_checks_project_id ON health_checks(project_id);
CREATE INDEX IF NOT EXISTS idx_health_checks_checked_at ON health_checks(checked_at);
CREATE INDEX IF NOT EXISTS idx_services_path_prefix ON services(path_prefix);
CREATE INDEX IF NOT EXISTS idx_request_logs_service_id ON request_logs(service_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_timestamp ON request_logs(timestamp);

-- Insert sample data
INSERT INTO projects (name, url, description) VALUES
('E-commerce Platform', 'https://demo-ecommerce.example.com', 'Plateforme e-commerce moderne avec paiements intégrés'),
('AI Chat Assistant', 'https://chat-ai.example.com', 'Assistant conversationnel intelligent utilisant l''IA'),
('Analytics Dashboard', 'https://analytics.example.com', 'Tableau de bord analytique en temps réel'),
('IoT Monitoring System', 'https://iot-monitor.example.com', 'Système de monitoring IoT pour équipements industriels'),
('Blockchain Wallet', 'https://crypto-wallet.example.com', 'Portefeuille crypto sécurisé avec support multi-chaînes'),
('Video Streaming Platform', 'https://video-stream.example.com', 'Plateforme de streaming vidéo avec transcoding automatique')
ON CONFLICT DO NOTHING;

INSERT INTO services (name, type, target_url, path_prefix, rate_limit) VALUES
('E-commerce API', 'api', 'https://api.ecommerce.example.com', '/api/ecommerce', 1000),
('AI Chat Service', 'api', 'https://chat-api.example.com', '/api/chat', 500),
('Analytics Service', 'api', 'https://analytics-api.example.com', '/api/analytics', 200),
('IoT Data Collector', 'api', 'https://iot-api.example.com', '/api/iot', 2000),
('Crypto Wallet API', 'api', 'https://wallet-api.example.com', '/api/wallet', 100),
('Video Processing', 'api', 'https://video-api.example.com', '/api/video', 50)
ON CONFLICT DO NOTHING;

