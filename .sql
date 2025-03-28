-- SQLite Script for the project

-- -----------------------------------------------------
-- Schema Dat220-project
-- -----------------------------------------------------
-- SQLite doesn't use schemas, so the "CREATE SCHEMA" statement is not needed.
-- Instead, we just create the tables directly.

-- -----------------------------------------------------
-- Table `user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "user" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "username" TEXT UNIQUE,
  "password" TEXT,
  "user_role" TEXT
);

-- -----------------------------------------------------
-- Table `note`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "note" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "data" TEXT,
  "user_id" INTEGER,
  "created_at" TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- -----------------------------------------------------
-- Table `high_scores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "high_scores" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "score" INTEGER,
  "user_id" INTEGER,
  "created_at" TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- -----------------------------------------------------
-- Table `Live_chat`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Live_chat" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "message_text" TEXT,
  "timestamp" TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- -----------------------------------------------------
-- Table `Public_Information`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Public_Information" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "profile_description" TEXT,
  "last_updated" TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- -----------------------------------------------------
-- Table `Files`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Files" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "uploaded_at" TIMESTAMP,
  "filename" TEXT,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- -----------------------------------------------------
-- Table `Comments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Comments" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "related_entity_id" INTEGER,
  "comment_text" TEXT,
  "created_at" TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- -----------------------------------------------------
-- Table `Groups`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Groups" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "group_name" TEXT,
  "created_by" INTEGER,
  "created_at" TIMESTAMP,
  FOREIGN KEY ("created_by") REFERENCES "user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION
);