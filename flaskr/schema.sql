DROP TABLE IF EXISTS volunteer;
DROP TABLE IF EXISTS customer;


CREATE TABLE customer (
id INTEGER PRIMARY KEY AUTOINCREMENT,
created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
name TEXT NOT NULL,
assistancetype TEXT NOT NULL,
neighborhood TEXT NOT NULL,
latlng TEXT NOT NULL,
email TEXT NOT NULL,
phone TEXT NOT NULL,
preference INTEGER,
gender TEXT NOT NULL,
language TEXT,
priority TEXT,
longterm INTEGER,
payment INTEGER,
served INTEGER
);


CREATE TABLE volunteer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  name TEXT NOT NULL,
  area TEXT NOT NULL,
  latlng TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  gender TEXT NOT NULL,
  language TEXT,
  longterm INTEGER,
  conditions INTEGER
  );