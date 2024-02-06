import os


def PathHandler(database_relative_path):
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the provided relative path
    database_path = os.path.abspath(os.path.join(script_directory, database_relative_path))

    print(f"Database Path: {database_path}")  # For debugging
    return database_path


# outputPath for output, sync and other folders
beamInputPath1 = "../../output/beam_Input.db"
beamReportPath1 = "../../output/beam_report.db"
postInputPath1 = "../../output/post_Input.db"
compactPath1 = "../../output/CompactDatabase.db"
joistInputPath1 = "../../output/joist_Input.db"
shearWallInputPath1 = "../../output/ShearWall_Input.db"
shearWallOutputPath1 = "../../output/ShearWall_output.db"
studWallInputPath1 = "../../output/StudWall_Input.db"
studWallOutputPath1 = "../../output/stud_report.db"
midlinePath1 = "../../output/Seismic/Midline.db"
seismicParamsPath1 = "../../output/Seismic/SeismicParameters.db"

# in UI_Wood\stableVersion
beamInputPath = "../output/beam_Input.db"
beamReportPath = "../output/beam_report.db"
postInputPath = "../output/post_Input.db"
compactPath = "../output/CompactDatabase.db"
joistInputPath = "../output/joist_Input.db"
shearWallInputPath = "../output/ShearWall_Input.db"
shearWallOutputPath = "../output/ShearWall_output.db"
studWallInputPath = "../output/StudWall_Input.db"
studWallOutputPath = "../output/stud_report.db"
midlinePath = "../output/Seismic/Midline.db"
seismicParamsPath = "../output/Seismic/SeismicParameters.db"
