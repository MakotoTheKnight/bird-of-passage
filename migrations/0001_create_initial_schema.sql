--
-- file: migrations/0001_create_initial_schema.sql
--

create table author
(
    display_name  TEXT PRIMARY KEY,
    inserted_date DATETIME default CURRENT_TIMESTAMP
);

create table author_links
(
    author_display_name TEXT,
    profile_link        TEXT,
    inserted_date       DATETIME default CURRENT_TIMESTAMP,
    primary key (author_display_name, profile_link),
    FOREIGN KEY (author_display_name) references author (display_name)
);

create table tweet_media
(
    tweet_data_id       TEXT,
    author_display_name text,
    media_url           TEXT,
    media_type          TEXT,
    created_date        DATETIME,
    inserted_date       DATETIME default CURRENT_TIMESTAMP,
    primary key (tweet_data_id, author_display_name, media_url, media_type),
    FOREIGN KEY (author_display_name) references author (display_name)
);

create table tweet_body
(
    tweet_data_id       text,
    author_display_name text,
    tweet_body          text,
    created_date        DATETIME,
    inserted_date       DATETIME default CURRENT_TIMESTAMP,
    primary key (author_display_name, tweet_data_id),
    FOREIGN KEY (author_display_name) references author (display_name)
);