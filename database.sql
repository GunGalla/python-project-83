DROP TABLE IF EXISTS urls, url_checks;
DROP TABLE IF EXISTS url_checks;
CREATE TABLE urls (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name varchar(255) UNIQUE,
  created_at DATE
);

CREATE TABLE url_checks (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  url_id bigint REFERENCES urls(id),
  status_code integer,
  h1 varchar(255),
  title varchar(255),
  description varchar(500),
  created_at DATE
);