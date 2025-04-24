import sqlite3

# Kobler til databasen i 'instance'-mappen
conn = sqlite3.connect("./instance/database.db")
cursor = conn.cursor()

cursor.executescript(
    """
-- SQLite Script for the project

-- Dropper tabeller hvis de eksisterer for å sikre en ren start (valgfritt, men nyttig under utvikling)
-- Kommentarer ut hvis du vil beholde data ved re-kjøring uten å slette filen først
-- DROP TABLE IF EXISTS "Comments";
-- DROP TABLE IF EXISTS "Files";
-- DROP TABLE IF EXISTS "Public_Information";
-- DROP TABLE IF EXISTS "Live_chat";
-- DROP TABLE IF EXISTS "high_scores";
-- DROP TABLE IF EXISTS "note";
-- DROP TABLE IF EXISTS "feedback";
-- DROP TABLE IF EXISTS "user";

-- -----------------------------------------------------
-- Table `user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "user" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "username" TEXT UNIQUE NOT NULL,  
  "password" TEXT NOT NULL,         
  "user_role" TEXT NOT NULL         
);

-- -----------------------------------------------------
-- Table `note`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "note" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "data" TEXT NOT NULL,                       
  "user_id" INTEGER NOT NULL,                
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
);

-- -----------------------------------------------------
-- Table `high_scores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "high_scores" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "score" INTEGER NOT NULL,                   
  "user_id" INTEGER NOT NULL,                 
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Bruker default timestamp
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION  
);

-- -----------------------------------------------------
-- Table `Live_chat` (Beholdt som den var, vurder om den trengs)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Live_chat" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "message_text" TEXT,
  "timestamp" TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE SET NULL ON UPDATE NO ACTION -- Endret til SET NULL hvis bruker slettes
);

-- -----------------------------------------------------
-- Table `Public_Information` (Beholdt som den var, vurder om den trengs)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Public_Information" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER UNIQUE, -- Bør nok være UNIQUE hvis det er en profil per bruker
  "profile_description" TEXT,
  "last_updated" TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION  
);

-- -----------------------------------------------------
-- Table `Files`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Files" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,                
  "filename" TEXT NOT NULL,                  
  "uploaded_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION  
);

-- -----------------------------------------------------
-- Table `Comments` (REVIDERT)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "Comments" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,               
  "page" TEXT NOT NULL,                     
  "content" TEXT NOT NULL,                  
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION 
);

-- -----------------------------------------------------
-- Table `feedback`  <--- NY TABELL HER
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS "feedback" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "message" TEXT NOT NULL,
  "submitted_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION 
);

    """ 
)

conn.commit()
conn.close()

print("Database schema created/updated successfully in instance/database.db")