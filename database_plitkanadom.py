import sqlite3
import aiosqlite

DATABASE = 'bot_stats_plitkanadom.db'

async def create_connection():
    conn = await aiosqlite.connect(DATABASE)
    return conn

async def create_table():
    conn = await create_connection()
    try:
        cursor = await conn.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                last_access TEXT
            )
        ''')
        await conn.commit()
    finally:
        await cursor.close()
        await conn.close()

async def add_user(user_id, username, first_name, last_name, last_access):
    conn = await create_connection()
    try:
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_access)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, last_access))
        await conn.commit()
    finally:
        await cursor.close()
        await conn.close()