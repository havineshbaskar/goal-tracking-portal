DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS checkins;
DROP TABLE IF EXISTS comments;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    uom TEXT,
    target REAL,
    weightage INTEGER,
    status TEXT DEFAULT 'Pending',
    manager_comment TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER,
    quarter TEXT,
    achievement REAL,
    progress REAL,
    FOREIGN KEY (goal_id) REFERENCES goals (id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER,
    manager_comment TEXT,
    FOREIGN KEY (goal_id) REFERENCES goals (id)
);

INSERT INTO users (username, password, role) VALUES
('employee', '123', 'employee'),
('manager', '123', 'manager'),
('admin', '123', 'admin');