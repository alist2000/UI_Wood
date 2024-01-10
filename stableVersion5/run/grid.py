from UI_Wood.stableVersion5.line import LineDrawHandler


class GridDraw:
    def __init__(self, x_grid, y_grid, grid_base):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.grid_base = grid_base

    def Draw(self, scene):
        line = LineDrawHandler(self.x_grid, self.y_grid, scene, None, None, self.grid_base)
