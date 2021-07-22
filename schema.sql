CREATE TABLE customer (
    id integer PRIMARY KEY NOT NULL GENERATED ALWAYS AS IDENTITY,
    username text NOT NULL UNIQUE,
    tg_id text UNIQUE
)