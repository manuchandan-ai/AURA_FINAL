import sqlite3
import os

DB_PATH = 'f:/AURA_FINAL/database/aura.db'

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create Conversations
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT 'New Conversation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')

        # Create Messages
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender TEXT NOT NULL, -- 'user' or 'aura'
            content TEXT NOT NULL,
            metadata TEXT, -- JSON for modules used, signals, confidence
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );
        ''')

        # Create Goals
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            progress INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            roadmap TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')

        # Create Reminders
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            due_date TIMESTAMP,
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')

        # Insert new modules
        modules = [
            ('AURA Create', 'create', 'Generative Design & Content', 'bi-palette'),
            ('AURA Money', 'money', 'Financial Planning & Guidance', 'bi-cash-stack'),
            ('AURA Travel', 'travel', 'Itineraries & Exploration', 'bi-airplane'),
            ('AURA Health', 'health', 'Wellness & Fitness Tracking', 'bi-heart-pulse'),
            ('AURA Learn', 'learn', 'Study Plans & Skill Growth', 'bi-book'),
            ('AURA Shop', 'shop', 'Smart Purchases & Comparisons', 'bi-cart'),
            ('AURA Project', 'project', 'Build & Develop', 'bi-code-slash'),
            ('AURA Future', 'future', 'Scenario Planning & Logic', 'bi-compass')
        ]
        
        for m in modules:
            cursor.execute('INSERT OR IGNORE INTO modules (name, slug, description, icon) VALUES (?, ?, ?, ?)', m)

        conn.commit()
        print("Migration completed successfully.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
