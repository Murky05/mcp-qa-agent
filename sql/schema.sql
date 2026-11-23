-- Test database for the MCP QA agent
CREATE DATABASE IF NOT EXISTS vikhyatacademy;
USE vikhyatacademy;

-- Source data the agent registers on the website
CREATE TABLE IF NOT EXISTS RegistrationDetails (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50),
  phone VARCHAR(10),
  occupation VARCHAR(30),   -- may be NULL: the agent fills gaps itself
  gender VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS Usernames (
  id INT AUTO_INCREMENT PRIMARY KEY,
  registration_id INT NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  FOREIGN KEY (registration_id) REFERENCES RegistrationDetails(id)
);

INSERT INTO RegistrationDetails (first_name, last_name, phone, occupation, gender) VALUES
  ('Aarav', 'Mehta',  '9812345670', 'Engineer', 'Male'),
  ('Priya', 'Nair',   '9823456781', NULL,       'Female'),
  ('Rohan', 'Kapoor', '9834567892', 'Doctor',   'Male');

-- Change the suffix if these emails are already registered on the site
INSERT INTO Usernames (registration_id, email) VALUES
  (1, 'aarav.mehta.va2311@example.com'),
  (2, 'priya.nair.va2311@example.com'),
  (3, 'rohan.kapoor.va2311@example.com');

-- Used by the local registration site (registration-site/app.py)
CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  phone VARCHAR(15) NOT NULL,
  gender ENUM('Male','Female','Other') NOT NULL,
  dob DATE NOT NULL,
  course VARCHAR(50) NOT NULL,
  city VARCHAR(60) NOT NULL,
  experience_years TINYINT UNSIGNED NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The query the agent runs for "last 2 records"
-- SELECT r.*, u.email FROM RegistrationDetails r
-- JOIN Usernames u ON u.registration_id = r.id
-- ORDER BY r.id DESC LIMIT 2;
