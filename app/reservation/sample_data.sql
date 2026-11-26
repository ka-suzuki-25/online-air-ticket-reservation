INSERT INTO Airline VALUES ('Jet Blue'), ('Delta Air Lines'), ('Etihad Airways');

INSERT INTO Airport VALUES
('JFK', 'New York', 'USA', 'both'),
('PVG', 'Shanghai', 'China', 'international'),
('LAX', 'Los Angeles', 'USA', 'domestic'),
('ATL', 'Atlanta', 'USA', 'domestic'),
('AUH', 'Abu Dhabi', 'UAE', 'international');

INSERT INTO Airplane VALUES
('Jet Blue', '1', 4, 'Airbus', 5),
('Jet Blue', '2', 200, 'Boeing', 8),
('Jet Blue', '3', 180, 'Airbus', 3),
('Delta Air Lines', '1', 220, 'Boeing', 6),
('Etihad Airways', '1', 300, 'Airbus', 2);

INSERT INTO Flight VALUES
('Jet Blue', 'B6101', 'JFK', '2027-01-16 10:00:00', 'PVG', '2027-01-17 06:00:00', '1', 'on time', 350.00),
('Jet Blue', 'B6201', 'PVG', '2027-01-16 13:00:00', 'JFK', '2027-01-16 17:00:00', '2', 'delayed', 300.00),
('Jet Blue', 'B6101', 'JFK', '2026-09-10 10:00:00', 'PVG', '2026-09-11 06:00:00', '1', 'on time', 320.00),
('Jet Blue', 'B6102', 'JFK', '2026-10-05 14:00:00', 'LAX', '2026-10-05 17:30:00', '3', 'on time', 280.00),
('Jet Blue', 'B6301', 'JFK', '2026-12-20 09:00:00', 'LAX', '2026-12-20 12:30:00', '3', 'on time', 250.00),
('Delta Air Lines', 'DL101', 'ATL', '2027-03-14 08:00:00', 'JFK', '2027-03-14 10:30:00', '1', 'on time', 480.00),
('Delta Air Lines', 'DL102', 'JFK', '2027-05-03 11:00:00', 'ATL', '2027-05-03 13:30:00', '1', 'delayed', 520.00),
('Etihad Airways', 'EY100', 'JFK', '2027-06-17 22:00:00', 'AUH', '2027-06-18 19:00:00', '1', 'on time', 950.00),
('Etihad Airways', 'EY101', 'AUH', '2028-01-16 09:00:00', 'JFK', '2028-01-16 15:00:00', '1', 'on time', 900.00);

INSERT INTO Customer VALUES
('alice@gmail.com', 'Alice Wang', MD5('alice123'), '10', 'MetroTech Center', 'Brooklyn', 'NY',
 '212-555-0101', 'P1234567', '2030-05-01', 'USA', '2000-03-15'),
('bob@gmail.com', 'Bob Chen', MD5('bob123'), '25', 'Broadway', 'New York', 'NY',
 '212-555-0102', 'P2345678', '2029-08-20', 'USA', '1998-11-02'),
('carol@gmail.com', 'Carol Li', MD5('carol123'), '7', 'Nanjing Road', 'Shanghai', 'Shanghai',
 '86-21-5550103', 'E3456789', '2031-01-10', 'China', '2001-07-30');

INSERT INTO Staff VALUES
('jb_staff1', MD5('staff123'), 'Eesha', 'Rao', '1990-04-12', 'staff1@jetblue.com', 'Jet Blue'),
('dl_staff1', MD5('staff123'), 'Dan', 'Lee', '1988-09-09', 'staff1@delta.com', 'Delta Air Lines');

INSERT INTO Staff_Phone VALUES
('jb_staff1', '718-555-0201'),
('jb_staff1', '718-555-0202');

INSERT INTO Ticket VALUES
(1001, 'Jet Blue', 'B6101', '2027-01-16 10:00:00', 'alice@gmail.com', 350.00,
 'credit', '4111111111111111', 'Alice Wang', '2028-06-30', '2026-11-01 10:30:00'),
(1002, 'Jet Blue', 'B6201', '2027-01-16 13:00:00', 'bob@gmail.com', 300.00,
 'debit', '5500000000000004', 'Bob Chen', '2027-09-30', '2026-11-02 14:15:00'),
(1003, 'Delta Air Lines', 'DL101', '2027-03-14 08:00:00', 'carol@gmail.com', 480.00,
 'credit', '4000000000000002', 'Carol Li', '2029-01-31', '2026-11-03 09:00:00'),
(1004, 'Delta Air Lines', 'DL102', '2027-05-03 11:00:00', 'alice@gmail.com', 520.00,
 'credit', '4111111111111111', 'Alice Wang', '2028-06-30', '2026-11-04 18:45:00'),
(1005, 'Etihad Airways', 'EY100', '2027-06-17 22:00:00', 'bob@gmail.com', 950.00,
 'debit', '5500000000000004', 'Bob Chen', '2027-09-30', '2026-11-05 12:00:00'),
(1006, 'Etihad Airways', 'EY101', '2028-01-16 09:00:00', NULL, NULL,
 NULL, NULL, NULL, NULL, NULL),
(1007, 'Jet Blue', 'B6101', '2026-09-10 10:00:00', 'carol@gmail.com', 320.00,
 'credit', '4000000000000002', 'Carol Li', '2029-01-31', '2026-08-20 08:30:00'),
(1008, 'Jet Blue', 'B6102', '2026-10-05 14:00:00', 'alice@gmail.com', 280.00,
 'debit', '4111111111111111', 'Alice Wang', '2028-06-30', '2026-09-15 16:00:00'),
(1009, 'Jet Blue', 'B6102', '2026-10-05 14:00:00', 'bob@gmail.com', 280.00,
 'credit', '5500000000000004', 'Bob Chen', '2027-09-30', '2026-09-16 11:20:00');