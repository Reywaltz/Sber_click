CREATE TABLE customer (
    id INTEGER PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    username TEXT NOT NULL UNIQUE,
    tg_id TEXT UNIQUE
);

CREATE TABLE worker (
    id INTEGER PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE task (
    id INTEGER PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    worker_id INTEGER REFERENCES worker(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customer(id) ON DELETE CASCADE
);