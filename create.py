import sqlite3
# ADMIN USER
# username: root
# password: root

# Kobler til databasen i 'instance'-mappen
conn = sqlite3.connect("./instance/database.db")
cursor = conn.cursor()

cursor.executescript(
    """

DROP TABLE IF EXISTS "Comments";
DROP TABLE IF EXISTS "Files";
DROP TABLE IF EXISTS "Live_chat";
DROP TABLE IF EXISTS "high_scores";
DROP TABLE IF EXISTS "note";
DROP TABLE IF EXISTS "feedback";
DROP TABLE IF EXISTS "sessions";
DROP TABLE IF EXISTS "user";

CREATE TABLE IF NOT EXISTS "user" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "username" TEXT UNIQUE NOT NULL,
  "password" TEXT NOT NULL,
  "salt" TEXT NOT NULL,
  "profile_description" TEXT,
  "last_updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "time_created" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  "user_role" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "sessions" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "token" TEXT NOT NULL,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "note" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "data" TEXT NOT NULL,                       
  "user_id" INTEGER NOT NULL,                
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS "high_scores" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "score" INTEGER NOT NULL,                   
  "user_id" INTEGER NOT NULL,                 
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION  
);

CREATE TABLE IF NOT EXISTS "Live_chat" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER,
  "message_text" TEXT,
  "timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE SET NULL ON UPDATE NO ACTION
);

CREATE TABLE IF NOT EXISTS "Files" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,                
  "filename" TEXT NOT NULL,                  
  "uploaded_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION  
);

CREATE TABLE IF NOT EXISTS "Comments" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,               
  "page" TEXT NOT NULL,                     
  "content" TEXT NOT NULL,                  
  "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION 
);

CREATE TABLE IF NOT EXISTS "feedback" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user_id" INTEGER NOT NULL,
  "message" TEXT NOT NULL,
  "submitted_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE ON UPDATE NO ACTION 
);

  """)

conn.commit()
conn.close()
from website.queries import *
import shutil
import sys
import os

sys.path.append('.')

uploads_folder = os.path.join(os.getcwd(), 'uploads')
    
if not os.path.exists(uploads_folder):
  os.makedirs(uploads_folder)
else:
  for filename in os.listdir(uploads_folder):
    file_path = os.path.join(uploads_folder, filename)
    if os.path.isfile(file_path):
      os.unlink(file_path)

def pop_users():
  users = ["root", "Adrian", "Bjarte", "Nathaniel", "Stordalen87", "Telephone6", "Cisco867", 
         "Database220", "Apple9", "Openai", "Sindre", "Oppendal", "Merit", "Apple8", 
         "Microsoft38", "Geir98", "lise1947", "tone198", "eirik", "user"]
  passwords = ["root", "password123", "securePass42", "nathanPass", "stordal#2023", 
            "phone123!", "cisco#pass", "d4t4b4se", "apple2023", "gpt4pass", 
            "sindre_pass", "oppendal123", "merit_2023", "apple_pass8", "msft38", 
            "geir1998", "lise_1947!", "tone_198", "eirik2023", "password"]
  ids = [create_user(users[i], passwords[i]) for i in range(len(users))]

  about = ["I am robot", "Software developer", "", "", "Plant enthusiast", "", "", 
           "Database administrator", "", "AI researcher", "Mouth breather", "", 
           "Student at UiS", "", "Tech enthusiast", "", "", "Hobby photographer", "", ""]
  _ = [set_biography(ids[i], about[i]) for i in range(len(users))]

def pop_sessions():
  sessions = [1, 14, 5, 3, 2, 13, 6, 8, 16, 2, 4, 5, 18, 16, 5, 4, 7, 3, 6, 17]
  _ = [create_session(i) for i in sessions]

def pop_chat():
  users = [1, 1, 4, 1, 3, 5, 6, 7, 1, 17, 4, 3, 2, 16, 4, 1, 8, 7, 1, 3]
  chats = ["welcome to my website", "hi", "seen my score?", "great high score dude!", "nice", "I like this website!", "Who is Apple8?",
             "Hello??", "Hi!", "Welcome", "Does anyone know how to change my username?", "You have to make a new account for that",
             "Today is my birthday!", "Congrats", "Yippie", "Has anyone seen that new movie?", "Wow that movie was something",
             "Man I want to travel", "Let us go to Italy", "I like France more"]
  _ = [insert_chat(users[i], chats[i]) for i in range(len(users))]

def pop_files():
  examples_folder = os.path.join(os.getcwd(), 'examples')
  uploads_folder = os.path.join(os.getcwd(), 'uploads')

  for i, filename in enumerate(os.listdir(examples_folder)):
    file_path = os.path.join(examples_folder, filename)
    if os.path.isfile(file_path):
      shutil.copy2(file_path, uploads_folder)
      insert_file(i+1, filename)

def pop_notes():
  users = [1, 1, 4, 1, 3, 5, 6, 7, 1, 17, 4, 3, 2, 16, 4, 1, 8, 7, 1, 3]
  notes = [
    "Remember to buy pizza", 
    "Password: root", 
    "Call mom tomorrow", 
    "Meeting with team", 
    "Pick up dry cleaning",
    "Doctor appointment on friday",
    "File taxes before April",
    "Buy birthday gift for Sarah",
    "Grocery list: milk, eggs, bread, cheese",
    "Return library books by Tuesday",
    "Fix leaky faucet in bathroom",
    "Submit project report by Thursday",
    "Dentist appointment next Monday",
    "Pay electricity bill",
    "Call plumber about kitchen sink",
    "Update resume with new skills",
    "Pick up kids from soccer",
    "Remember to water plants",
    "Buy new phone charger",
    "Schedule car maintenance"
  ]
  _ = [new_note(notes[i], users[i]) for i in range(len(notes))]

def pop_scores():
    users = [1, 1, 4, 1, 3, 5, 6, 7, 1, 17, 4, 3, 2, 16, 4, 1, 8, 7, 1, 3]
    scores = [4, 15, 16, 17, 21, 31, 17, 15, 16, 8, 5, 7, 18, 15, 42, 23, 19, 27, 33, 12]

    _ = [new_score(users[i], scores[i]) for i in range(len(scores))]

def pop_feedback():
  users = [2, 14, 5, 3, 2, 13, 6, 8, 16, 2, 4, 5, 18, 16, 5, 4, 7, 3, 6, 17]
  feedback = [
    "Great website",
    "Add more games!",
    "Add chess?",
    "Love the math games",
    "The snake game is too fast",
    "Please add a dark mode option",
    "Mobile version doesn't work well",
    "Would like to see multiplayer games",
    "Great for my kids to practice math",
    "Add more difficulty levels",
    "Need better instructions for new users",
    "Login page sometimes freezes",
    "Can we have a leaderboard?",
    "The interface is very intuitive",
    "Want to see more educational content",
    "Fix the bug in the snake game when reaching score 50",
    "Add achievements system",
    "Add sound effects to games",
    "Would love to see puzzle games added",
    "Consider adding a forum for discussions"
  ]

  _ = [add_feedback(users[i], feedback[i]) for i in range(len(feedback))]

def pop_comments():
  users = [6, 3, 4, 5, 3, 5, 16, 7, 5, 17, 4, 3, 2, 16, 4, 6, 8, 7, 4, 3]
  texts = [
    "I like this game",
    "I have the current high score :)",
    "This helps my kids learn math",
    "Too easy, need harder questions",
    "Great for practicing multiplication",
    "Could use more colorful graphics",
    "Love the challenge mode",
    "Gets really difficult after level 5",
    "My son plays this every day",
    "Can we have more division problems?",
    "Fun way to practice math skills",
    "Beat my old record today!",
    "The timer makes it exciting",
    "Would be better with sound effects",
    "Just reached level 10!",
    "Perfect for elementary school kids",
    "The animations are really smooth",
    "This game helped improve my math",
    "Getting better at multiplication",
    "Just got a perfect score!"
  ]

  _ = [insert_comment(users[i], 'mattespill', texts[i]) for i in range(len(users))]


if len(sys.argv) > 1:
  pop_users()
  pop_sessions()
  pop_chat()
  pop_files()
  pop_notes()
  pop_scores()
  pop_feedback()
  pop_comments()
