import enum
import random


class Compass(enum.IntEnum):
    """
    Represents the different cardinal directions in the maze.
    """
    NORTH = 0b1000
    EAST = 0b0100
    SOUTH = 0b0010
    WEST = 0b0001
    
    @classmethod
    def reverse(cls, direction):
        if direction == cls.NORTH:
            return cls.SOUTH
        if direction == cls.EAST:
            return cls.WEST
        if direction == cls.SOUTH:
            return cls.NORTH
        else:
            return cls.EAST

class Maze(object):
    """
    Represents a maze for the mouse robot to solve.
    
    The maze is made up of 16x16 squares, where (0,0) corresponds to the northwest
    corner and (15,15) corresponds to the southeast corner.

    Mazes may be generated using any of the following algorithms:
     * Wilson's algorithm, using `algorithm="wilson"` (default)
     * recursive backtracking, using `algorithm="backtracking"`
     * Randomized Prim's algorithm, using `algorithm="prim"`
    """

    def __init__(self, width=16, height=16, algorithm="wilson"):
        self.width = width
        self.height = height

        if algorithm == "wilson":
            maze = wilsons_maze(width=width, height=height)
            self._grid = maze._grid
            return
        elif algorithm == "backtracking":
            print("backtrack")
            maze = recursive_backtrack(width=width, height=height)
            self._grid = maze._grid
            return
        elif algorithm == "prim":
            print("prim")
            maze = randomized_prims(width=width, height=height)
            self._grid = maze._grid
            return
        else:
            assert algorithm is None, f"Unknown maze generation algorithm: {algorithm}"
        
        # Internally, cells are a bitfield of four bits indicating whether there is a
        # wall to the north, east, south, or west.
        blocked = Compass.NORTH | Compass.EAST | Compass.SOUTH | Compass.WEST
        self._grid = [[blocked for _ in range(width)] for _ in range(height)]
        
        if width >= 4 and height >= 4:
            # the center 4 units form an open 2x2 square
            centerx = width // 2 - 1
            centery = height // 2 - 1
            
            self._grid[centery][centerx] = Compass.NORTH | Compass.WEST
            self._grid[centery][centerx+1] = Compass.NORTH | Compass.EAST
            self._grid[centery+1][centerx+1] = Compass.SOUTH | Compass.EAST
            self._grid[centery+1][centerx] = Compass.SOUTH | Compass.WEST
    
    def paths(self, x, y):
        """
        Returns a list of the possible directions to go in the maze from unit (x, y).
        """
        return [direction for direction in Compass if ~self._grid[y][x] & direction]
    
    def walls(self, x, y):
        """Returns a list of directions with walls from unit (x, y)."""
        return [direction for direction in Compass if self._grid[y][x] & direction]

    def neighbor(self, x, y, direction):
        """Returns the neighbor of unit (x, y) in the given direction, if it exists."""
        if direction == Compass.NORTH:
            if y > 0:
                return (x, y-1)
        elif direction == Compass.EAST:
            if x < self.width - 1:
                return (x+1, y)
        elif direction == Compass.SOUTH:
            if y < self.height - 1:
                return (x, y+1)
        else:
            if x > 0:
                return (x-1, y)
    
    def neighbors(self, x, y):
        """
        Returns the list of directions in which unit (x, y) has a neighbor.

        This is effectively just a bounds check on the grid—a unit won't have a
        neighbor in a direction if it is on that edge of the board.
        """
        return [
            direction
            for direction in Compass
            if self.neighbor(x, y, direction) is not None
        ]
    
    def break_wall(self, x, y, direction):
        """
        Removes the wall between the unit (x,y) and its neighbor in the given direction.
        """
        self._grid[y][x] &= ~direction
        nx, ny = self.neighbor(x, y, direction)
        self._grid[ny][nx] &= ~Compass.reverse(direction)
    
    def __str__(self):
        return "\n".join(["\t".join(map(str, row)) for row in self._grid])


def recursive_backtrack(width=16, height=16) -> Maze:
    """Generates a random maze using the recursive backtracking algorithm."""
    maze = Maze(width=width, height=height, algorithm=None)
    visited = [[False for _ in range(maze.width)] for _ in range(maze.height)]
    
    # ensure only one entrance to the center squares
    centerx = maze.width // 2 - 1
    centery = maze.height // 2 - 1
    
    visited[centery][centerx] = True
    visited[centery][centerx+1] = True
    visited[centery+1][centerx+1] = False
    visited[centery+1][centerx] = True

    def visit(x, y):
        visited[y][x] = True
        neighbors = maze.neighbors(x, y)
        random.shuffle(neighbors)

        for direction in neighbors:
            nx, ny = maze.neighbor(x, y, direction)
            if not visited[ny][nx]:
                maze.break_wall(x, y, direction)
                nx, ny = maze.neighbor(x, y, direction)
                visit(nx, ny)

    visit(0, 0)
    return maze

def randomized_prims(width=16, height=16) -> Maze:
    """Generates a maze using a randomized version of Prim's Algorithm."""
    maze = Maze(width=width, height=height, algorithm=None)
    visited = [[False for _ in range(maze.width)] for _ in range(maze.height)]

    # ensure only one entrance to the center squares
    centerx = maze.width // 2 - 1
    centery = maze.height // 2 - 1
    
    visited[centery][centerx] = True
    visited[centery][centerx+1] = True
    visited[centery+1][centerx+1] = False
    visited[centery+1][centerx] = True

    visited[0][0] = True
    boundary = [(0,0,Compass.EAST), (0,0,Compass.SOUTH)]

    while boundary:
        x, y, direction = boundary.pop(random.randint(0, len(boundary)-1))
        nx, ny = maze.neighbor(x, y, direction)
        if not visited[ny][nx]:
            maze.break_wall(x, y, direction)
            boundary.extend([(nx,ny,direction) for direction in maze.neighbors(nx, ny)])
            visited[ny][nx] = True
    
    return maze

def wilsons_maze(width=16, height=16) -> Maze:
    """Generates a maze using Wilson's loop-erased random walk algorithm."""
    maze = Maze(width=width, height=height, algorithm=None)
    visited = [[False for _ in range(maze.width)] for _ in range(maze.height)]

    visited[0][0] = True

    def loop_erased_random_walk(x, y):
        """
        Take a random walk from unit (sx,sy) until we run into a visited unit, and
        remove any cycles from the path if/when it intersects itself.
        """
        path = []
        directions = []

        while not visited[y][x]:
            direction = random.choice(maze.neighbors(x, y))
            nx, ny = maze.neighbor(x, y, direction)

            while (nx, ny) in path:
                path.pop()
                directions.pop()
            
            path.append((x, y))
            directions.append(direction)
            x, y = nx, ny
        
        return zip(path, directions)
    
    for x in range(maze.width):
        for y in range(maze.height):
            if visited[y][x]:
                continue
            
            print(f"path from: ({x}, {y})")
            path = list(loop_erased_random_walk(x, y))
            print(path)
            for (xi,yi), direction in path:
                maze.break_wall(xi, yi, direction)
                visited[yi][xi] = True
    
    return maze
