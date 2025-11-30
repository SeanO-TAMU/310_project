CREATE DATABASE IF NOT EXISTS library;
USE library;

DROP TABLE IF EXISTS OrderItems;
DROP TABLE IF EXISTS Billings;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    userID INT Primary Key AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255),
    auth_token VARCHAR(255),
    role ENUM('manager', 'customer') DEFAULT 'customer'
);

CREATE TABLE Books (
    bookID INT Primary Key AUTO_INCREMENT,
    title VARCHAR(255),
    author VARCHAR(100),
    rental_price DECIMAL(10, 2),
    buy_price DECIMAL(10, 2),
    quantity INT
);

CREATE TABLE Billings (
    billingID INT Primary Key AUTO_INCREMENT,
    userID INT NOT NULL,
    order_date DATETIME NOT NULL,
    total_cost DECIMAL(10, 2),
    status ENUM('pending', 'paid') DEFAULT 'paid',
    FOREIGN KEY (userID) REFERENCES Users(userID)
);

CREATE TABLE OrderItems (
    orderitemID INT Primary Key AUTO_INCREMENT,
    bookID INT NOT NULL,
    billingID INT NOT NULL,
    price DECIMAL(10, 2),
    order_type ENUM('buy', 'rent'),
    FOREIGN KEY (bookID) REFERENCES Books(bookID),
    FOREIGN KEY (billingID) REFERENCES Billings(billingID)
);

INSERT INTO Books (bookID, title, author, rental_price, buy_price, quantity) VALUES
(1, 'The Great Gatsby', 'F. Scott Fitzgerald', 2.99, 10.99, 5),
(2, 'To Kill a Mockingbird', 'Harper Lee', 2.49, 9.99, 4),
(3, '1984', 'George Orwell', 1.99, 8.99, 6),
(4, 'The Hobbit', 'J.R.R. Tolkien', 3.49, 12.99, 3),
(5, 'The Catcher in the Rye', 'J.D. Salinger', 2.29, 9.49, 2),
(6, 'The Hunger Games', 'Suzanne Collins', 2.99, 11.49, 7),
(7, 'Harry Potter and the Sorcerer''s Stone', 'J.K. Rowling', 3.99, 14.99, 10),
(8, 'Pride and Prejudice', 'Jane Austen', 1.49, 7.99, 4),
(9, 'The Fault in Our Stars', 'John Green', 2.19, 10.49, 3),
(10, 'Dune', 'Frank Herbert', 3.99, 15.99, 5);

