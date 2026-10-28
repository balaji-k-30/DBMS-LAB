
-- ==========================================
-- Student Record Management System
-- Complete SQL Script
-- ==========================================

-- Step 1: Create and select the database
CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Step 2: Create the students table if it does not exist
CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    course VARCHAR(50) NOT NULL,
    semester INT NOT NULL DEFAULT 1,
    CHECK (semester BETWEEN 1 AND 12)
);

-- Step 3: Add semester column if it is missing
SET @column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'student_db'
      AND TABLE_NAME = 'students'
      AND COLUMN_NAME = 'semester'
);

SET @sql = IF(
    @column_exists = 0,
    'ALTER TABLE students ADD COLUMN semester INT NOT NULL DEFAULT 1',
    'SELECT ''Semester column already exists'' AS Message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 4: Insert sample student records
INSERT IGNORE INTO students
    (name, email, course, semester)
VALUES
    ('Rahul', 'rahul.sample@example.com', 'BCA', 3),
    ('Priya', 'priya.sample@example.com', 'BCA', 3);

-- Step 5: Display the table structure
DESCRIBE students;

-- Step 6: Display all student records
SELECT * FROM students;

-- ==========================================
-- End of SQL Script
-- ==========================================
