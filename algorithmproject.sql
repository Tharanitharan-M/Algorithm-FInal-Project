use algoproject;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    encrypted_password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    age VARCHAR(255),
    gender VARCHAR(255),
    address1 VARCHAR(255),
    address2 VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    pincode VARCHAR(255),
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    health_condition VARCHAR(255),
    insurance_plan VARCHAR(255)
);


-- Create a table to store doctors' information
CREATE TABLE doctors (
    ID INT PRIMARY KEY,
    Name VARCHAR(255),
    Specialization VARCHAR(255),
    Availability VARCHAR(50),
    Insurance VARCHAR(255),
    Latitude DECIMAL(10, 8),
    Longitude DECIMAL(11, 8),
    Ratings INT,
    Waiting INT
);

-- Insert data into the doctors table
INSERT INTO doctors (ID, Name, Specialization, Availability, Insurance, Latitude, Longitude, Ratings, Waiting)
VALUES
    (101, 'Dr. Jennifer Adams', 'Cardiology', 'M-F 9-5', 'Aetna', 43.67885134, -70.30979342, 3, 30),
    (102, 'Dr. Daniel Brown', 'Dermatology', 'M-T 9-12', 'UnitedHealthcare Humana', 43.66387282, -70.25421412, 3, 30),
    (103, 'Dr. Sarah Clark', 'Psychiatry', 'M-F 9-5', 'Medicaid Aetna', 43.67416821, -70.29782681, 7, 30),
    (104, 'Dr. Matthew Davis', 'Orthopedics', 'W-F 9-5', 'Humana', 43.64781636, -70.33346495, 9, 0),
    (105, 'Dr. Emily Evans', 'Dermatology', 'M-F 9-5', 'Anthem', 43.68694854, -70.27632040, 10, 30),
    (106, 'Dr. Christopher Foster', 'Orthopedics', 'M-F 12-5', 'UnitedHealthcare', 43.66236922, -70.26117500, 3, 15),
    (107, 'Dr. Jessica Green', 'Cardiology', 'M-F 10-4', 'Medicaid Aetna UnitedHealthcare', 43.65603414, -70.26116933, 7, 15),
    (108, 'Dr. Ryan Hill', 'Dermatology', 'M-F 9-5', 'Humana Anthem', 43.66109673, -70.25329892, 8, 0),
    (109, 'Dr. Kimberly Jackson', 'Orthopedics', 'M-F 12-5', 'Aetna Humana', 43.66221030, -70.26188004, 7, 30),
    (110, 'Dr. Andrew Kim', 'Orthopedics', 'M-F 9-5', 'UnitedHealthcare Medicaid', 43.68196719, -70.26480346, 5, 15),
    (111, 'Dr. Lauren Mitchell', 'Cardiology', 'M-F 9-5', 'Medicaid Anthem', 43.68254304, -70.25357839, 10, 30),
    (112, 'Dr. Nicholas Nelson', 'Psychiatry', 'M-F 12-5', 'Aetna Humana UnitedHealthcare', 43.65064575, -70.26276438, 9, 0),
    (113, 'Dr. Stephanie Parker', 'Orthopedics', 'M-F 9-5', 'Medicaid UnitedHealthcare', 43.65366764, -70.33101927, 9, 0),
    (114, 'Dr. Justin Reed', 'Dermatology', 'M-F 9-5', 'Aetna Anthem', 43.65084713, -70.26004583, 10, 30),
    (115, 'Dr. Taylor Roberts', 'Cardiology', 'M-W 9-5', 'Humana Medicaid', 43.65429788, -70.33323996, 6, 0),
    (116, 'Dr. Heather Sanchez', 'Psychiatry', 'M-F 9-5', 'UnitedHealthcare Anthem', 43.65875236, -70.29516735, 2, 0),
    (117, 'Dr. Timothy Turner', 'Dermatology', 'M-F 9-5', 'Anthem Aetna', 43.68786490, -70.25027974, 10, 0),
    (118, 'Dr. Rachel Ward', 'Cardiology', 'M-F 9-12', 'UnitedHealthcare', 43.66127585, -70.24547669, 2, 30),
    (119, 'Dr. Kyle Young', 'Orthopedics', 'M-W 9-5', 'Humana Medicaid Aetna', 43.70733721, -70.28019088, 3, 15),
    (120, 'Dr. Morgan Zimmerman', 'Psychiatry', 'M-F 9-5', 'Medicaid Aetna', 43.71604619, -70.30631765, 8, 0);
