import unittest

from maze.maze import Maze, Compass

class MazeTests(unittest.TestCase):
    def test_maze_dimensions(self):
        maze = Maze(width=3, height=2)
        self.assertEqual(len(maze._grid), 2)
        self.assertEqual(len(maze._grid[0]), 3)
    
    def test_maze_walls(self):
        maze = Maze(width=1, height=1)
        maze._grid[0][0] = Compass.NORTH | Compass.WEST
        self.assertEqual(maze.walls(0, 0), {Compass.NORTH, Compass.WEST})
    
    def test_maze_paths(self):
        maze = Maze(width=1, height=1)
        maze._grid[0][0] = Compass.NORTH | Compass.WEST
        self.assertEqual(maze.paths(0, 0), {Compass.SOUTH, Compass.EAST})
    
    def test_maze_has_2x2_center(self):
        maze = Maze(width=6, height=6)
        self.assertSetEqual(maze.paths(2, 2), {Compass.SOUTH, Compass.EAST})
        self.assertSetEqual(maze.paths(3, 2), {Compass.SOUTH, Compass.WEST})
        self.assertSetEqual(maze.paths(3, 3), {Compass.NORTH, Compass.WEST})
        self.assertSetEqual(maze.paths(2, 3), {Compass.NORTH, Compass.EAST})
    
    def test_break_wall(self):
        maze = Maze(width=2, height=1)
        self.assertSetEqual(maze.paths(0, 0), set())
        self.assertSetEqual(maze.paths(1, 0), set())
        maze.break_wall(0, 0, Compass.EAST)
        self.assertSetEqual(maze.paths(0, 0), {Compass.EAST})
        print(maze.paths(1, 0))
        self.assertSetEqual(maze.paths(1, 0), {Compass.WEST})
