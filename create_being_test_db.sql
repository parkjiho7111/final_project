-- Create being_test table
CREATE TABLE IF NOT EXISTS being_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    period VARCHAR(100),
    link VARCHAR(500),
    genre VARCHAR(100),
    region VARCHAR(100),
    original_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_genre ON being_test (genre);

CREATE INDEX idx_region ON being_test (region);

CREATE INDEX idx_original_id ON being_test (original_id);