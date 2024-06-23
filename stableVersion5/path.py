import os
import sys


def PathHandler(database_relative_path):
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the provided relative path
    database_path = os.path.abspath(os.path.join(script_directory, database_relative_path))

    print(f"Database Path: {database_path}")  # For debugging
    return database_path


# outputPath for output, sync and other folders
# beamReportPath = "../../output/beam_Input.db"
# beamReportPath = "../../output/beam_report.db"
# postInputPath = "../../output/post_Input.db"
# compactPath = "../../output/CompactDatabase.db"
# joistInputPath = "../../output/joist_Input.db"
# shearWallInputPath = "../../output/ShearWall_Input.db"
# shearWallOutputPath = "../../output/ShearWall_output.db"
# studWallInputPath = "../../output/StudWall_Input.db"
# studWallOutputPath = "../../output/stud_report.db"
# midlinePath = "../../output/Seismic/Midline.db"
# seismicParamsPath = "../../output/Seismic/SeismicParameters.db"

# in UI_Wood\stableVersion
beamInputPath = os.path.join(os.getcwd(), r"database_output\beam_Input.db")
beamReportPath = os.path.join(os.getcwd(), r"database_output\beam_report.db")
postInputPath = os.path.join(os.getcwd(), r"database_output\post_Input.db")
compactPath = os.path.join(os.getcwd(), r"database_output\CompactDatabase.db")
joistInputPath = os.path.join(os.getcwd(), r"database_output\joist_Input.db")
shearWallInputPath = os.path.join(os.getcwd(), r"database_output\ShearWall_Input.db")
shearWallOutputPath = os.path.join(os.getcwd(), r"database_output\ShearWall_output.db")
studWallInputPath = os.path.join(os.getcwd(), r"database_output\StudWall_Input.db")
studWallOutputPath = os.path.join(os.getcwd(), r"database_output\stud_report.db")
midlinePath = os.path.join(os.getcwd(), r"database_output\Seismic\Midline.db")
seismicParamsPath = os.path.join(os.getcwd(), r"database_output\Seismic\SeismicParameters.db")
# compactPath = "../output/CompactDatabase.db"
# joistInputPath = "../output/joist_Input.db"
# shearWallInputPath = "../output/ShearWall_Input.db"
# shearWallOutputPath = "../output/ShearWall_output.db"
# studWallInputPath = "../output/StudWall_Input.db"
# studWallOutputPath = "../output/stud_report.db"
# midlinePath = "../output/Seismic/Midline.db"
# seismicParamsPath = "../output/Seismic/SeismicParameters.db"
directories = ["database_output", "database_output/Seismic", "images", "images/beam", "images/post", "images/output",
               "images/joist", "Final_Report"]


def main_path():
    directory_to_add = [os.path.join(os.getcwd(), 'images'), os.path.join(os.getcwd(), 'output'),
                        os.path.join(os.getcwd(), 'output_database')]
    for directory in directory_to_add:
        if directory not in sys.path:
            sys.path.append(directory)

    # To add the parent directory of the current script
    parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))
    if parent_directory not in sys.path:
        sys.path.append(parent_directory)
    # To add the grandparent directory
    grandparent_directory = os.path.abspath(os.path.join(os.getcwd(), '../..'))
    if grandparent_directory not in sys.path:
        sys.path.append(grandparent_directory)


class HandleDirectories:
    def __init__(self, directories):
        self.directories = directories

    def make_all(self):
        for directory in self.directories:
            self.make_directory(directory)

    @staticmethod
    def make_directory(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)


output = os.path.join(os.getcwd(), "database_output/")
