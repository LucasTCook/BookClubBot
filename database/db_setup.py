import sqlite3
import settings

logger = settings.logging.getLogger("bot")

def verify_and_create_tables():
    try:
        with sqlite3.connect(settings.SQL_DB) as conn:
            cursor = conn.cursor()

            # Reading_group table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reading_group (
                group_id INTEGER PRIMARY KEY,
                group_name TEXT NOT NULL UNIQUE,
                description TEXT,
                current_book_id INTEGER,
                users_in_group TEXT,
                home_channel_id INTEGER NOT NULL
            );
            ''')

            # Suggested_books table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suggested_books (
                id	INTEGER,
                title	TEXT,
                author	TEXT,
                user_id	INTEGER,
                upvotes	INTEGER DEFAULT 0,
                downvotes	INTEGER DEFAULT 0,
                cover	TEXT,
                keywords	TEXT,
                desc	TEXT DEFAULT 'No Description Available',
                pageCount	INTEGER,
                PRIMARY KEY(id AUTOINCREMENT)
                );
            ''')

            # Add more table creation statements here as needed

            conn.commit()

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
