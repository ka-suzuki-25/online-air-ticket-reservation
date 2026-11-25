CREATE TABLE Airline(
    name 					VARCHAR(100),
    PRIMARY KEY(name)
);

CREATE TABLE Airport(
    name 					VARCHAR(100),
    city 					VARCHAR(100),
    country 				VARCHAR(100),
    type 					VARCHAR(20),
    PRIMARY KEY(name),
    CHECK(type in ('domestic', 'international', 'both'))
);


CREATE TABLE Airplane (
    airline_name 		VARCHAR(100),
    airplane_id 		VARCHAR(50),
    num_seats 			INT,
    manufacturer 		VARCHAR(100),
    age 				INT,
    PRIMARY KEY (airline_name, airplane_id),
    FOREIGN KEY (airline_name) REFERENCES Airline(name)
);

CREATE TABLE Flight(
    airline_name		VARCHAR(100),
    flight_number 		VARCHAR(30),
    dep_airport         VARCHAR(100), 
    dep_datetime 	    DATETIME NOT NULL,
    arr_airport         VARCHAR(100) NOT NULL,
    arr_datetime        DATETIME NOT NULL,
    airplane_id         VARCHAR(50) NOT NULL,
    status              VARCHAR(20),
    base_price          DECIMAL(10,2),
    PRIMARY KEY(airline_name, flight_number, dep_datetime),
    FOREIGN KEY (dep_airport) REFERENCES Airport(name),
    FOREIGN KEY (arr_airport) REFERENCES Airport(name),
    FOREIGN KEY (airline_name, airplane_id) REFERENCES Airplane(airline_name, airplane_id),
    CHECK(status in ('delayed', 'on time', 'canceled'))
);

CREATE TABLE Customer (
    email               VARCHAR(150),
    name                VARCHAR(100)  NOT NULL,
    password            VARCHAR(100) NOT NULL,
    building_number     VARCHAR(50),
    street              VARCHAR(100),
    city                VARCHAR(100),
    state               VARCHAR(100),
    phone_number        VARCHAR(20),
    passport_number     VARCHAR(20),
    passport_expiration DATE,
    passport_country    VARCHAR(100),
    date_of_birth       DATE,
    PRIMARY KEY (email)
);


CREATE TABLE Ticket (
    ticket_id          INT,
    airline_name       VARCHAR(100) NOT NULL,
    flight_number      VARCHAR(30) NOT NULL,
    dep_datetime       DATETIME    NOT NULL,
    customer_email     VARCHAR(150),              -- NULL = unsold / cancelled
    sold_price         DECIMAL(10,2),
    card_type          VARCHAR(10),
    card_number        VARCHAR(20),
    name_on_card       VARCHAR(100),
    card_expiration    DATE,
    purchase_datetime  DATETIME,
    PRIMARY KEY (ticket_id),
    FOREIGN KEY (airline_name, flight_number, dep_datetime) REFERENCES Flight(airline_name, flight_number, dep_datetime),
    FOREIGN KEY (customer_email) REFERENCES Customer(email),
    CHECK (card_type IN ('credit', 'debit'))
);

CREATE TABLE Staff (
    username 			VARCHAR(100),
    password 			VARCHAR(100) NOT NULL,
    first_name 			VARCHAR(100),
    last_name 			VARCHAR(100),
    date_of_birth 		DATE,
    email 				VARCHAR(150) NOT NULL,
    airline_name 		VARCHAR(100) NOT NULL,
    PRIMARY KEY (username),
    FOREIGN KEY (airline_name) REFERENCES Airline(name)
); 

CREATE TABLE Staff_Phone (
    username      		VARCHAR(100),
    phone_number  		VARCHAR(20),
    PRIMARY KEY (username, phone_number),
    FOREIGN KEY (username) REFERENCES Staff(username)
);

CREATE TABLE Review (
    customer_email 		VARCHAR(150),
    airline_name 		VARCHAR(100),
    flight_number 		VARCHAR(30),
    dep_datetime 		DATETIME,
    rate 				DECIMAL(3,1),
    comment 			TEXT,
    PRIMARY KEY (customer_email, airline_name, flight_number, dep_datetime),
    FOREIGN KEY (customer_email) REFERENCES Customer(email),
    FOREIGN KEY (airline_name, flight_number, dep_datetime) REFERENCES Flight(airline_name, flight_number, dep_datetime)
);