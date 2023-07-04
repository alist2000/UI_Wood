from PySide6.QtCore import Qt


def deActive(selected, post, beam, joist, shearWall, studWall):
    if selected == post:
        deActive_joist(joist)
        deActive_beam(beam)
        deActive_studWall(studWall)
        deActive_shearWall(shearWall)
    elif selected == beam:
        deActive_post(post)
        deActive_joist(joist)
        deActive_studWall(studWall)
        deActive_shearWall(shearWall)
    elif selected == joist:
        deActive_post(post)
        deActive_beam(beam)
        deActive_studWall(studWall)
        deActive_shearWall(shearWall)
    elif selected == shearWall:
        deActive_post(post)
        deActive_joist(joist)
        deActive_beam(beam)
        deActive_studWall(studWall)
    elif selected == studWall:
        deActive_post(post)
        deActive_joist(joist)
        deActive_beam(beam)
        deActive_shearWall(shearWall)


def deActive_post(post):
    post.post_drawing_mode = 0
    post.postButton.post.setText("POST")
    post.setCursor(Qt.CursorShape.ArrowCursor)


def deActive_beam(beam):
    beam.beam_select_status = 0
    beam.beam.beam.setText("BEAM")
    beam.setCursor(Qt.CursorShape.ArrowCursor)


def deActive_joist(joist):
    joist.joist_status = 0
    joist.joist.joist.setText("JOIST")
    joist.setCursor(Qt.CursorShape.ArrowCursor)


def deActive_shearWall(shearWall):
    shearWall.shearWall_select_status = 0
    shearWall.shearWall.shearWall.setText("SHEAR WALL")
    shearWall.setCursor(Qt.CursorShape.ArrowCursor)


def deActive_studWall(studWall):
    studWall.studWall_select_status = 0
    studWall.studWall.studWall.setText("STUD WALL")
    studWall.setCursor(Qt.CursorShape.ArrowCursor)
