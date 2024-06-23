import sqlite3
from UI_Wood.stableVersion5.path import postInputPath


class PostSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect(postInputPath)
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

        self.createTable()

        self.pointLoadData()

    def createTable(self):
        self.cursor.execute("DROP TABLE IF EXISTS postTable")

        # Create table
        self.cursor.execute("""
            CREATE TABLE postTable (
                ID INT,
                Story TEXT,
                Label TEXT,
                Height FLOAT,
                Wall_Width INT,
                Coordinate TEXT
            )
        """)

        self.conn.commit()

    def pointLoadData(self):
        self.cursor.execute("DROP TABLE IF EXISTS PointLoad")

        # Create table
        self.cursor.execute("""
            CREATE TABLE PointLoad (
                ID_post INT,
                Load_magnitude FLOAT,
                Load_type TEXT
            )
        """)

        self.conn.commit()


class WritePostInputSQL:
    def __init__(self, postProp, postID, db):
        self.postProp = postProp
        self.postID = postID
        self.db = db
        self.mainTable()
        self.pointLoadTable()

    def mainTable(self):
        label = self.postProp["label"]
        story = self.postProp["story"]
        height = self.postProp["height"]
        coordinate = self.postProp["coordinate"]
        width = int(self.postProp["width"])
        self.db.cursor.execute(
            'INSERT INTO postTable (ID, Story, Label, Height,'
            ' Wall_Width, Coordinate) values(?, ?, ?, ?, ?, ?)',
            [
                self.postID, str(story), label, height, width,
                str(coordinate)
            ])
        self.db.conn.commit()

    def pointLoadTable(self):
        pointLoads = self.postProp["load"]

        for load in pointLoads:
            mag = load["magnitude"]
            loadType = load["type"]
            self.db.cursor.execute(
                'INSERT INTO PointLoad (ID_post, Load_magnitude, Load_type) values(?, ?, ?)',
                [
                    self.postID, mag, loadType
                ])
            self.db.conn.commit()
