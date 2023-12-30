import sqlite3
from UI_Wood.stableVersion4.post_new import magnification_factor


class beamSQL:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('../../Output/beam_Input.db')
        # Create a cursor object
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")

        self.createTable()

        self.pointLoadData()

        self.distLoadData()

        self.supportData()

    def createTable(self):
        self.cursor.execute("DROP TABLE IF EXISTS beamTable")

        # Create table
        self.cursor.execute("""
            CREATE TABLE beamTable (
                ID INT,
                Story TEXT,
                Label TEXT,
                Length FLOAT,
                Coordinate_start TEXT,
                Coordinate_end TEXT
            )
        """)

        self.conn.commit()

    def pointLoadData(self):
        self.cursor.execute("DROP TABLE IF EXISTS PointLoad")

        # Create table
        self.cursor.execute("""
            CREATE TABLE PointLoad (
                ID_beam INT,
                Start FLOAT,
                Load_magnitude FLOAT,
                Load_type TEXT
            )
        """)

        self.conn.commit()

    def distLoadData(self):
        self.cursor.execute("DROP TABLE IF EXISTS DistLoad")

        # Create table
        self.cursor.execute("""
            CREATE TABLE DistLoad (
                ID_beam INT,
                Start FLOAT,
                End FLOAT,
                Load_magnitude FLOAT,
                Load_type TEXT
            )
        """)

        self.conn.commit()

    def supportData(self):
        self.cursor.execute("DROP TABLE IF EXISTS Support")

        # Create table
        self.cursor.execute("""
            CREATE TABLE Support (
                ID_beam INT,
                Start FLOAT,
                Support_type TEXT
            )
        """)

        self.conn.commit()


class WriteBeamInputSQL:
    def __init__(self, beamProp, story, beamID, db):
        self.beamProp = beamProp
        self.story = story
        self.beamID = beamID
        self.db = db
        self.mainTable()
        self.pointLoadTable()
        self.distLoadTable()
        self.supportTable()

    def mainTable(self):
        label = self.beamProp["label"]
        length = self.beamProp["length"]
        startCoord = [i / magnification_factor for i in self.beamProp["coordinate_main"][0]]
        endCoord = [i / magnification_factor for i in self.beamProp["coordinate_main"][1]]
        constantCoordinate = self.beamProp["start"]
        direction = self.beamProp["direction"]
        # if direction == "N-S":
        #     startCoord = (constantCoordinate, start)
        #     endCoord = (constantCoordinate, end)
        # else:
        #     startCoord = (start, constantCoordinate)
        #     endCoord = (end, constantCoordinate)
        self.db.cursor.execute(
            'INSERT INTO beamTable (ID, Story, Label, Length,'
            ' Coordinate_start, Coordinate_end) values(?, ?, ?, ?, ?, ?)',
            [
                self.beamID, str(self.story), label, length, str(startCoord),
                str(endCoord)
            ])
        self.db.conn.commit()

    def pointLoadTable(self):
        pointLoads = self.beamProp["load"]["point"]

        for locLoad in pointLoads:
            start = locLoad["start"]
            for load in locLoad["load"]:
                mag = load["magnitude"]
                loadType = load["type"]
                self.db.cursor.execute(
                    'INSERT INTO PointLoad (ID_beam, Start, Load_magnitude, Load_type) values(?, ?, ?, ?)',
                    [
                        self.beamID, start, mag, loadType
                    ])
                self.db.conn.commit()

    def distLoadTable(self):
        pointLoads = self.beamProp["load"]["distributed"]

        for locLoad in pointLoads:
            start = locLoad["start"]
            end = locLoad["end"]
            for load in locLoad["load"]:
                mag = load["magnitude"]
                loadType = load["type"]
                self.db.cursor.execute(
                    'INSERT INTO DistLoad (ID_beam, Start,End,  Load_magnitude, Load_type) values(?, ?, ?, ?, ?)',
                    [
                        self.beamID, start, end, mag, loadType
                    ])
                self.db.conn.commit()

    def supportTable(self):
        supports = self.beamProp["support"]

        for support in supports:
            coordinate = support[0]
            supportType = support[1]
            if supportType == (1, 1, 1):
                SupportType = "Fixed"
            elif supportType == (1, 1, 0):
                SupportType = "Pinned"
            else:
                SupportType = "Other"

            self.db.cursor.execute(
                'INSERT INTO Support (ID_beam, Start,Support_type) values(?, ?, ?)',
                [
                    self.beamID, coordinate, SupportType
                ])
            self.db.conn.commit()
