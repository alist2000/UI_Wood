import sqlite3


class shearWallSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('../../Output/ShearWall_Input.db')
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

    def createTable(self):
        self.cursor.execute("DROP TABLE IF EXISTS WallTable")

        # Create table
        self.cursor.execute("""
            CREATE TABLE WallTable (
                ID INT,
                Story TEXT,
                Coordinate_start TEXT,
                Coordinate_end TEXT,
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


class SeismicParamsSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('../../Output/Seismic/SeismicParameters.db')
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

    def seismicParams(self):
        self.cursor.execute("DROP TABLE IF EXISTS seismicParams")

        # Create table
        self.cursor.execute("""
            CREATE TABLE seismicParams (
                S1 FLOAT,
                Ss FLOAT,
                Fa FLOAT,
                Fv FLOAT,
                I FLOAT,
                T_model FLOAT,
                R_factor FLOAT,
                risk_category TEXT,
                Regular_Building TEXT
            )
        """)

        self.conn.commit()

    def loadData(self, storyName):
        tableName = f"Total_Load_Story_{storyName}"
        self.cursor.execute(f"DROP TABLE IF EXISTS {tableName}")

        # Create table
        self.cursor.execute(f"""
            CREATE TABLE {tableName} (
                Story TEXT,
                joist_area FLOAT,
                load_area FLOAT,
                load_magnitude FLOAT
            )
        """)

        self.conn.commit()
        return tableName


class MidlineSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('../../Output/Seismic/Midline.db')
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

    def loadData(self, storyName, line):
        tableName = f"Story_{storyName}_Line_{line}"
        self.cursor.execute(f"DROP TABLE IF EXISTS {tableName}")

        # Create table
        self.cursor.execute(f"""
            CREATE TABLE {tableName} (
                Story TEXT,
                Line TEXT,
                load_area FLOAT,
                load_magnitude FLOAT
            )
        """)

        self.conn.commit()
        return tableName
