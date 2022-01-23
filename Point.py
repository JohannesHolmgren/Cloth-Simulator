import pygame
import math


def get_angle(p1, p2):
    x = p1.x - p2.x
    y = p1.y - p2.y
    if x == 0:
        if p1.y > p2.y:
            return -math.pi
        return math.pi
    return math.atan(y/x)


class Force:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def inverse(self):
        return Force(-self.x, -self.y)

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError()

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y == value
        else:
            raise IndexError()

class Point:
    
    RADIUS          = 3
    GRAVITY         = 0.5
    MASS            = 1
    USE_COLLISION   = False

    def __init__(self, x, y, static=False):
        self.static = static
        self.start_pos = (x, y)
        self.x = x
        self.y = y
        self.vel_y = 0
        self.vel_x = 0
        self.acc_x = 0
        self.acc_y = 0
        self.radius = self.RADIUS
        self.mass = self.MASS
        self.force = Force(0, 0)

        # Add gravity
        self.add_force(Force(0, self.mass*self.GRAVITY))

    def draw(self, win):
        pygame.draw.circle(win, (0, 0, 0), (self.x, self.y), self.radius)

    def update(self, points):
        if self.static:
            return
        
        if self.USE_COLLISION:
            for p in points:
                self.collide_point(p)

        # Add all physics
        self.add_force(Force(0, self.mass*self.GRAVITY))
        self.acc_x   = self.mass * self.force.x
        self.vel_x  += self.acc_x
        self.x      += self.vel_x
        self.x       = int(self.x)
        self.acc_y   = self.mass * self.force.y
        self.vel_y  += self.acc_y
        self.y      += self.vel_y
        self.y       = int(self.y)
        if self.x > 10000:
            self.x = 10000
        if self.y > 10000:
            self.y = 10000

        # Reset forces (since they should only be applied once)
        self.reset_force()
    
    def collide_point(self, p):
        """ If distance between points are less than radius * 2 they collide """
        if p is self:
            return
        dist = math.sqrt((p.x - self.x)**2 + (p.y - self.y)**2)
        overlap = (self.radius + p.radius) - dist
        if overlap < 0:
            return
        angle = get_angle(self, p)
        to_move_x = abs(math.cos(angle) * overlap) # if abs(math.cos(angle) * overlap) > 10 else 0
        to_move_y = abs(math.sin(angle) * overlap) # if abs(math.sin(angle) * overlap) > 10 else 0
        if self.x >= p.x:
            self.x += to_move_x
            if self.y <= p.y:
                self.y -= to_move_y
            else:
                self.y += to_move_y
        else:
            self.x -= to_move_x
            if self.y <= p.y:
                self.y -= to_move_y
            else:
                self.y += to_move_y
        
                


    def add_force(self, force):
        self.force.x += force.x
        self.force.y += force.y

    def reset_force(self):
        self.force.x = 0
        self.force.y = 0

    def set_start_pos(self, x, y):
        self.start_pos[0] = x
        self.start_pos[1] = y



class Spring:

    METER           = 1
    DAMPING         = 0.1

    def __init__(self, p1:Point, p2:Point, constant, rest_length):
        self.p1 = p1
        self.p2 = p2
        self.constant = constant
        self.rest_length = rest_length
    def draw(self, win):
        pygame.draw.line(win, (0, 0, 0), (self.p1.x, self.p1.y), (self.p2.x, self.p2.y))

    def update(self):
        # Get directions
        try:
            dir_x = -(self.p1.x - self.p2.x) / abs(self.p1.x - self.p2.x)
        except Exception as E:
            dir_x = 1
        try:
            dir_y = -(self.p1.y - self.p2.y) / abs(self.p1.y - self.p2.y)
        except Exception as E:
            dir_y = 1
        # Get distances
        rest_length_x = abs(self.rest_length * math.cos(get_angle(self.p1, self.p2)))
        rest_length_y = abs(self.rest_length * math.sin(get_angle(self.p1, self.p2)))
        dist_x = abs(self.p1.x - self.p2.x) - rest_length_x
        if self.p1.x - self.p2.x == 0:
            dist_x = 0
        dist_y = abs(self.p1.y - self.p2.y) - rest_length_y
        if self.p1.y - self.p2.y == 0:
            dist_y = 0
        # Create and add force
        f1 = Force(dir_x * self.constant * dist_x/self.METER, dir_y * self.constant * dist_y/self.METER)
        self.p1.add_force(f1)
        self.p2.add_force(f1.inverse())

        damping_force_y1 = Force(-self.DAMPING * self.p1.vel_x, -self.DAMPING * self.p1.vel_y)
        self.p1.add_force(damping_force_y1)
        damping_force_y2 = Force(-self.DAMPING * self.p2.vel_x, -self.DAMPING * self.p2.vel_y)
        self.p1.add_force(damping_force_y2)