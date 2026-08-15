-- Run in MySQL Workbench after 01_schema.sql
-- Deterministic seed data for Phase 1 test scenarios A-E.
-- Safe to re-run: clears seeded rows first.

USE student_support;

SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM support_tickets;
DELETE FROM submissions;
DELETE FROM certificates;
DELETE FROM payments;
DELETE FROM enrollments;
DELETE FROM assignments;
DELETE FROM courses;
DELETE FROM students;

SET FOREIGN_KEY_CHECKS = 1;

-- Courses (fixed IDs)
INSERT INTO courses (id, external_id, title, description, status) VALUES
    (1, 'crs_ds', 'Data Science Bootcamp', 'Foundations of data science and analytics.', 'active'),
    (2, 'crs_ml', 'Machine Learning Mastery', 'Supervised and unsupervised learning.', 'active');

-- Students A-E (fixed IDs)
INSERT INTO students (id, external_id, name, email, status) VALUES
    (1, 'stu_A', 'Student A', 'student.a@example.com', 'active'),
    (2, 'stu_B', 'Student B', 'student.b@example.com', 'active'),
    (3, 'stu_C', 'Student C', 'student.c@example.com', 'active'),
    (4, 'stu_D', 'Student D', 'student.d@example.com', 'active'),
    (5, 'stu_E', 'Student E', 'student.e@example.com', 'active');

-- Enrollments
-- A: active | B: pending | C: active | D: pending (failed payment) | E: active
INSERT INTO enrollments (student_id, course_id, status, enrolled_at) VALUES
    (1, 1, 'active', '2026-01-10 09:00:00'),
    (2, 1, 'pending', '2026-01-15 10:00:00'),
    (3, 1, 'active', '2026-01-12 11:00:00'),
    (4, 1, 'pending', '2026-02-01 08:00:00'),
    (5, 2, 'active', '2026-01-20 14:00:00');

-- Payments
-- A,B,C: success | D: failed | E: duplicate success payments
INSERT INTO payments (student_id, course_id, transaction_id, amount, currency, status) VALUES
    (1, 1, 'TXN_A_DS_001', 4999.00, 'INR', 'success'),
    (2, 1, 'TXN_B_DS_001', 4999.00, 'INR', 'success'),
    (3, 1, 'TXN_C_DS_001', 4999.00, 'INR', 'success'),
    (4, 1, 'TXN_D_DS_001', 4999.00, 'INR', 'failed'),
    (5, 2, 'TXN_E_ML_001', 5999.00, 'INR', 'success'),
    (5, 2, 'TXN_E_ML_002', 5999.00, 'INR', 'success');

-- Certificates
-- A: issued | C: missing (no row) | E: issued
INSERT INTO certificates (student_id, course_id, status, certificate_url, issued_at) VALUES
    (1, 1, 'issued', 'https://certs.example.com/stu_A/crs_ds', '2026-03-01 12:00:00'),
    (5, 2, 'issued', 'https://certs.example.com/stu_E/crs_ml', '2026-03-05 12:00:00');

-- Assignments
INSERT INTO assignments (id, course_id, title, description, deadline) VALUES
    (1, 1, 'Exploratory Data Analysis', 'Analyze the provided dataset and submit findings.', '2026-04-01 23:59:00');

-- Submissions
INSERT INTO submissions (assignment_id, student_id, status, submitted_at, grade) VALUES
    (1, 1, 'graded', '2026-03-20 18:00:00', 88.50),
    (1, 3, 'submitted', '2026-03-22 10:00:00', NULL);
