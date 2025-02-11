-- So we want to store on the one hand users, which will have a JWT token after login in.
-- We want to store the user's email, password.
-- On the other hand we have test runs, which are associated to a user. There will be as many test runs as the user wants.
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE test_run (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,

    name VARCHAR(255) NOT NULL,
    description TEXT,
    threshold FLOAT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE cpu_usage (
    id UUID PRIMARY KEY,
    test_run_id UUID NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage FLOAT NOT NULL,

    FOREIGN KEY (test_run_id) REFERENCES test_run(id)
);
