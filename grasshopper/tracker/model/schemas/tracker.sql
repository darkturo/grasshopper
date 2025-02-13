DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS test_run;
DROP TABLE IF EXISTS cpu_usage;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE test_run (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,

    name VARCHAR(255) NOT NULL,
    description TEXT,
    threshold FLOAT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE cpu_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_run_id INTEGER NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage FLOAT NOT NULL,

    FOREIGN KEY (test_run_id) REFERENCES test_run(id)
);
