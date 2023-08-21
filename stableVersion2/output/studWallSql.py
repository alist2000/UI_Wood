import sqlite3


class studWallSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('../../Output/StudWall_Input.db')
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

    def createTable(self, tableName='WallTable'):
        self.cursor.execute(f"DROP TABLE IF EXISTS {tableName}")

        # Create table
        self.cursor.execute(f"""
            CREATE TABLE {tableName} (
                ID INT,
                Story TEXT,
                Wall_Label TEXT,
                Wall_Length FLOAT,
                Story_Height FLOAT,
                Int_Ext TEXT,
                Wall_Self_Weight TEXT,
                Wall_Width INT,
                start TEXT,
                end TEXT,
                Rd TEXT,
                Rl TEXT,
                Rlr TEXT,
                Rs TEXT,
                Wall_Orientation TEXT
            )
        """)

        self.conn.commit()
