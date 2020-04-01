from maze import Compass

def right_of(direction):
    if direction == Compass.NORTH:
        return Compass.EAST
    elif direction == Compass.EAST:
        return Compass.SOUTH
    elif direction == Compass.SOUTH:
        return Compass.WEST
    else:
        return Compass.NORTH

def left_of(direction):
    if direction == Compass.NORTH:
        return Compass.WEST
    elif direction == Compass.EAST:
        return Compass.NORTH
    elif direction == Compass.SOUTH:
        return Compass.EAST
    else:
        return Compass.SOUTH

# The direction the turtle moved last
direction = Compass.EAST

def right_handed_wall_hugger(options):
    global direction
    if right_of(direction) in options:
        direction = right_of(direction)
    else:
        if direction in options:
            # follow the wall straight!
            pass
        else:
            if left_of(direction) in options:
                direction = left_of(direction)
            else:
                direction = right_of(right_of(direction))
    return direction
