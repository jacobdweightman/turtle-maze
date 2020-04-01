from maze import Maze, Renderer
from solvers import random_walk, right_handed_wall_hugger

maze = Maze(algorithm="prim")

Renderer(maze, solver=random_walk)
