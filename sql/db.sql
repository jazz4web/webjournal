CREATE TABLE users (
    id             serial PRIMARY KEY,
    username       varchar(16) UNIQUE NOT NULL,
    ugroup         varchar(16),
    weight         smallint,
    registered     timestamp with time zone,
    last_visit     timestamp with time zone,
    password_hash  varchar(128),
    description    varchar(500) DEFAULT NULL,
    last_published timestamp with time zone DEFAULT NULL
);

CREATE TABLE accounts (
    id        serial PRIMARY KEY,
    address   varchar(128) UNIQUE,
    swap      varchar(128),
    swexpire  timestamp with time zone,
    requested timestamp with time zone,
    user_id   integer REFERENCES users(id) UNIQUE
);

CREATE TABLE sessions (
    suffix  varchar(13) UNIQUE NOT NULL,
    brkey   varchar(32),
    logedin timestamp with time zone,
    expire  timestamp with time zone,
    user_id integer REFERENCES users(id)
);

CREATE TABLE avatars (
    picture bytea NOT NULL,
    user_id integer REFERENCES users(id) UNIQUE
);

CREATE TABLE captchas (
    picture bytea NOT NULL,
    val     varchar(5) UNIQUE,
    suffix  varchar(7) UNIQUE
);

CREATE TABLE friends (
    author_id integer REFERENCES users(id),
    friend_id integer REFERENCES users(id),
    CONSTRAINT author_friend_uni UNIQUE (author_id, friend_id)
);

CREATE TABLE followers (
    author_id   integer REFERENCES users(id),
    follower_id integer REFERENCES users(id),
    CONSTRAINT author_follower_uni UNIQUE (author_id, follower_id)
);

CREATE TABLE blockers (
    target_id  integer REFERENCES users(id),
    blocker_id integer REFERENCES users(id),
    CONSTRAINT target_blocker_uni UNIQUE (target_id, blocker_id)
);

CREATE TABLE settings(
    indexpage varchar(16) DEFAULT NULL,
    dgroup    varchar(16) DEFAULT NULL,
    counters  text,
    robots    text
);

INSERT INTO settings (indexpage, dgroup, counters, robots)
  VALUES (NULL, NULL, NULL, NULL);

CREATE TABLE aliases (
    url       text,
    created   timestamp with time zone,
    clicked   integer       DEFAULT 0,
    suffix    varchar(10)   UNIQUE,
    author_id integer       REFERENCES users(id),
    CONSTRAINT author_url_uni UNIQUE (author_id, url)
);
