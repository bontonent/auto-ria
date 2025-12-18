CREATE TABLE IF NOT EXISTS car (
    id UUID PRIMARY KEY,
    url TEXT,
    title TEXT,
    price_usd FLOAT,
    odometer FLOAT,
    username TEXT,
    phone_number BIGINT, 
    images_count INTEGER,
    car_number VARCHAR(40),
    car_vin VARCHAR(40),
    datetime_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
    UNIQUE(price_usd, url)
);

CREATE TABLE IF NOT EXISTS car_images (
    id UUID PRIMARY KEY,
    car_id UUID REFERENCES car(id),
    image_url TEXT UNIQUE,
    CONSTRAINT fk_car FOREIGN KEY(car_id) REFERENCES car(id) ON DELETE CASCADE
);