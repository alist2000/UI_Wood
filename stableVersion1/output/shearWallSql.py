import sqlite3


class shearWallSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('../../Output/ShearWall_Input.db')
        # Create a cursor object
        self.cursor = self.conn.cursor()

    def createTable(self):
        self.cursor.execute("DROP TABLE IF EXISTS WallTable")

        # Create table
        self.cursor.execute("""
            CREATE TABLE WallTable (
                ID INT,
                Story TEXT,
                Line TEXT,
                Wall_Label TEXT,
                Wall_Length FLOAT,
                Story_Height FLOAT,
                Opening_Width TEXT,
                Int_Ext TEXT,
                Wall_Self_Weight TEXT,
                start TEXT,
                end TEXT,
                Rd TEXT,
                Rl TEXT,
                Rlr TEXT,
                Rs TEXT,
                Left_Bottom_End TEXT,
                Right_Top_End TEXT,
                Po_Left TEXT,
                Pl_Left TEXT,
                Pe_Left TEXT,
                Po_Right TEXT,
                Pl_Right TEXT,
                Pe_Right TEXT,
                Wall_Orientation TEXT
            )
        """)

        self.conn.commit()
