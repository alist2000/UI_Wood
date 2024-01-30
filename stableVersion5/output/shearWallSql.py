import sqlite3
import os


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


class DropTables:
    def __init__(self, database_relative_path):
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Combine the script directory with the provided relative path
        database_path = os.path.abspath(os.path.join(script_directory, database_relative_path))

        print(f"Database Path: {database_path}")  # For debugging

        try:
            # Continue with the rest of the function...
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return

        try:
            # Step 2: Query the list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Step 3: Drop each table
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                print(f"Table '{table_name}' dropped.")

            # Commit the changes and close the connection
            connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")

        finally:
            connection.close()


# db = '../../../Output/ShearWall_output.db'
# DropTables(db)
