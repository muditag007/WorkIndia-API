CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role ENUM('user', 'admin') NOT NULL
);

CREATE TABLE shorts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50),
    title VARCHAR(255),
    author VARCHAR(50),
    publish_date DATETIME,
    content TEXT,
    actual_content_link VARCHAR(255),
    image VARCHAR(255),
    upvotes INT DEFAULT 0,
    downvotes INT DEFAULT 0
);
