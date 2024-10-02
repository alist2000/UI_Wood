import os
import shutil
import sqlite3


# Function to copy and rename SQLite databases
def copy_and_rename_databases(db1, new_name1):
    if not os.path.exists(new_name1):
        os.makedirs(new_name1)

    new_path1 = new_name1
    # Copy the first SQLite database
    shutil.copy(db1, new_path1)
    print(f"Copied {db1} to {new_path1}")


def create_seismic_parameters(database):
    # Connect to SQLite database
    conn = sqlite3.connect(database)
    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM 'seismicParams'")
    S1, Ss, Fa, Fv, I, Tmodel, R, risk, regular = cursor.fetchone()

    cursor.close()
    return {
        'Fa': Fa, 'Fv': Fv, 'I': I, 'R Factor': R, 'Regular Building': regular, 'Risk Category': risk,
        'S1': S1, 'Ss': Ss, 'T model': Tmodel
    }
