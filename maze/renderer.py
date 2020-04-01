from .maze import Compass, Maze
import pyglet

class Rect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._gl = ('v2f', self._vertex_data())
    
    def draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self._gl)
    
    def _vertex_data(self):
        """A tuple of the four vertices of the rectangle"""
        return (self.x,                 self.y,
                self.x + self.width,    self.y,
                self.x + self.width,    self.y + self.height,
                self.x,                 self.y + self.height)


class Unit(object):
    """Represents a single unit of a maze."""
    def __init__(self, walls):
        self.walls = walls
    
    def draw(self, x, y, width):
        vertex_buffer = self._vertex_data(x, y, width)
        pyglet.graphics.draw(
            len(vertex_buffer) // 2,
            pyglet.gl.GL_QUADS,
            ('v2f', vertex_buffer)
        )
    
    def _vertex_data(self, x, y, width):
        thickness = 3
        vertices = ()
        if self.walls & Compass.NORTH:
            vertices += Rect(x, y + width, width + thickness, thickness)._gl[1]
        if self.walls & Compass.EAST:
            vertices += Rect(x + width, y, thickness, width)._gl[1]
        if self.walls & Compass.SOUTH:
            vertices += Rect(x, y, width, thickness)._gl[1]
        if self.walls & Compass.WEST:
            vertices += Rect(x, y, thickness, width)._gl[1]
        return vertices


class Turtle(object):
    """Represents a maze-solving turtle in a maze."""
    image = pyglet.image.load('resources/turtle.png')

    def __init__(self, x: int, y: int, solver):
        self.sprite = pyglet.sprite.Sprite(Turtle.image)
        self.x = x
        self.y = y
        self.solver = solver
    
    def draw(self, x, y, width):
        self.sprite.scale = width / 99.0 # scale to the size of a maze unit
        self.sprite.update(x=x, y=y)
        self.sprite.draw()


class Renderer(object):
    def __init__(self, maze: Maze, solver=None):
        self.maze = maze
        self.turtle = Turtle(0, 0, solver)
        self.window = pyglet.window.Window(resizable=True)
        self.window.event(self.on_draw)

        pyglet.clock.schedule_interval(lambda dt: self.move_turtle(), 0.1)
        pyglet.app.run()
    
    def on_draw(self):
        self.window.clear()
        width = self.window.width
        height = self.window.height

        maze_width = min([width, height]) * 0.8
        unit_width = maze_width / max([self.maze.width, self.maze.height])
        y = height - (height - maze_width) / 2 - unit_width

        for row in self.maze._grid:
            x = (width - maze_width) / 2
            for unit in row:
                # convert from bitfield unit to renderable unit
                Unit(unit).draw(x, y, unit_width)
                x += unit_width
            y -= unit_width
        
        x = (width - maze_width) / 2 + unit_width * self.turtle.x
        y = height - (height - maze_width) / 2 - unit_width - unit_width * self.turtle.y
        self.turtle.draw(x, y, unit_width)
    
    def move_turtle(self):
        x, y = self.turtle.x, self.turtle.y
        options = self.maze.paths(x, y)
        move = self.turtle.solver(options)
        assert move in options, f"Illegal move `{move}` at position ({x}, {y})"
        self.turtle.x, self.turtle.y = self.maze.neighbor(x, y, move)
