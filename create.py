
import sqlite3

# Kobler til databasen i 'instance'-mappen
conn = sqlite3.connect("./instance/database.db")
cursor = conn.cursor()

cursor.executescript(
    """
-- SQLite Script for the project

-- Dropper tabeller hvis de eksisterer for å sikre en ren start (valgfritt, men nyttig under utvikling)
-- Kommentarer ut hvis du vil beholde data ved re-kjøring uten å slette filen først
DROP TABLE IF EXISTS "Groups";
DROP TABLE IF EXISTS "Comments";
DROP TABLE IF EXISTS "Files";
DROP TABLE IF EXISTS "sessions";
DROP TABLE IF EXISTS "Live_chat";
DROP TABLE IF EXISTS "high_scores";
DROP TABLE IF EXISTS "note";
DROP TABLE IF EXISTS "user";

-- -----------------------------------------------------
-- Table `user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "user" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "username" TEXT UNIQUE NOT NULL, -- Lagt til NOT NULL
  "password" TEXT NOT NULL,        -- Lagt til NOT NULL
  "salt" TEXT NOT NULL,
  "profile_description" TEXT,
  "last_updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "time_created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "user_role" TEXT NOT NULL        -- Lagt til NOT NULL
);

-- -----------------------------------------------------
-- Table `Sessions` (Jeg la denne til fordi det er nice)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "sessions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "token" TEXT NOT NULL,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE
);


-- -----------------------------------------------------
-- Table `note`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "note" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "data" TEXT NOT NULL,                      -- Lagt til NOT NULL
  "user_id" INTEGER NOT NULL,                -- Lagt til NOT NULL
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Bruker default timestamp
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION -- Lagt til ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table `high_scores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "high_scores" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "score" INTEGER NOT NULL,                  -- Lagt til NOT NULL
  "user_id" INTEGER NOT NULL,                -- Lagt til NOT NULL
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Bruker default timestamp
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION -- Lagt til ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table `Live_chat` (Beholdt som den var, vurder om den trengs)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Live_chat" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "message_text" TEXT,
  "timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE SET NULL ON UPDATE NO ACTION -- Endret til SET NULL hvis bruker slettes
);

-- -----------------------------------------------------
-- Table `Files`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Files" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,               -- Lagt til NOT NULL
  "filename" TEXT NOT NULL,                 -- Lagt til NOT NULL
  "uploaded_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Bruker default timestamp
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION -- Lagt til ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table `Comments` (REVIDERT)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Comments" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,                 -- Sikrer at kommentaren har en bruker
  "page" TEXT NOT NULL,                     -- Lagt til kolonne for å identifisere siden kommentaren tilhører
  "content" TEXT NOT NULL,                    -- Endret fra comment_text, sikrer at kommentaren har innhold
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Bruker default timestamp
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION -- Sletter kommentar hvis bruker slettes
);

-- -----------------------------------------------------
-- Table `Groups` (Beholdt som den var, vurder om den trengs)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Groups" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "group_name" TEXT UNIQUE NOT NULL, -- Lagt til UNIQUE og NOT NULL
  "created_by" INTEGER,
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Bruker default timestamp
  FOREIGN KEY ("created_by") REFERENCES "user" ("id") ON DELETE SET NULL ON UPDATE NO ACTION -- Hva skal skje hvis brukeren som lagde gruppen slettes? SET NULL?
);
    """
)

conn.commit()
conn.close()