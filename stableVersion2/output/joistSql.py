import sqlite3


class joistSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('../../Output/joist_Input.db')
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

        self.createTable()

        self.distLoadData()

    def createTable(self):
        self.cursor.execute("DROP TABLE IF EXISTS joistTable")

        # Create table
        self.cursor.execute("""
            CREATE TABLE joistTable (
                ID INT,
                Story TEXT,
                Label TEXT,
                Orientation TEXT,
                Length FLOAT,
                Coordinate_start TEXT,
                Coordinate_end TEXT
            )
        """)

        self.conn.commit()

    def distLoadData(self):
        self.cursor.execute("DROP TABLE IF EXISTS DistLoad")

        # Create table
        self.cursor.execute("""
            CREATE TABLE DistLoad (
                ID_joist INT,
                Number INT,
                Start FLOAT,
                End FLOAT,
                Load_magnitude FLOAT,
                Load_type TEXT
            )
        """)

        self.conn.commit()


class WriteJoistInputSQL:
    def __init__(self, joistProp, joistID, db):
        self.joistProp = joistProp
        self.joistID = joistID
        self.db = db
        self.mainTable()

    def mainTable(self):
        label = self.joistProp["label"]
        length = self.joistProp["length"]
        story = self.joistProp["story"]
        direction = self.joistProp["direction"]
        start = self.joistProp["coordinate"][0]
        end = self.joistProp["coordinate"][2]
        self.db.cursor.execute(
            'INSERT INTO joistTable (ID, Story, Label,Orientation, Length,'
            'Coordinate_start, Coordinate_end) values(?, ?, ?, ?, ?, ?, ?)',
            [
                self.joistID, str(story), label, direction, length, str(start),
                str(end)
            ])
        self.db.conn.commit()

    def distLoadTable(self, number, joistItem):
        pointLoads = joistItem["load"]

        for locLoad in pointLoads:
            start = locLoad["start"]
            end = locLoad["end"]
            for load in locLoad["load"]:
                mag = load["magnitude"]
                loadType = load["type"]
                self.db.cursor.execute(
                    'INSERT INTO DistLoad (ID_joist,Number, Start,End,  Load_magnitude, Load_type) values(?, ?, ?, ?, ?, ?)',
                    [
                        self.joistID, number, start, end, mag, loadType
                    ])
                self.db.conn.commit()
