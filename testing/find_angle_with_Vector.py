# -*- coding: utf8 -*-
import pygame, math, time
import numpy as np
from vector import MoveVector

""" TOIMII! """

class Vector:
    """ 
    Classi johon voi tallettaa vektorin joko kulma- tai summamuodossa ja tekee konversiot automaattisesti.
    HUOM! Angle radiaaneina!
    """
    def __init__(self, x=None, y=None, magnitude=None, angle=None):
        if x is not None and y is not None:
            self.set_xy(x, y)
        elif magnitude is not None and angle is not None:
            self.set_magnitude_angle(magnitude, angle)
        else:
            raise ValueError("x and y OR magnitude and angle need to be set!")

    def set_xy(self, x, y):
        """ Sets x and y directly, calculates magnitude and angle """
        self.x = x
        self.y = y
        self.magnitude = math.hypot(x, y)
        self.angle = math.atan2(y, x)

    def set_magnitude_angle(self, magnitude, angle):
        """ Sets magnitude and angle directly, calculates x and y """
        self.magnitude = magnitude
        self.angle = angle
        self.x = math.cos(angle * magnitude)
        self.y = math.sin(angle * magnitude)

    def get_xy(self):
        return (self.x, self.y)

    def get_magnitude(self):
        return self.magnitude

    def get_angle(self):
        return self.angle


pygame.init()
win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Angle finding test")


def show_text(pos, text, color=(255, 255, 255), bgcolor=(0, 0, 0), fontSize=24):
    """ Utility-metodi tekstin näyttämiseen ruudulla """
    global win
    font = pygame.font.Font(None, fontSize)
    textimg = font.render(text, 1, color, bgcolor)
    win.blit(textimg, pos)

def get_angle_in_radians(point1, point2):
    x_difference = point1[0] - point2[0]
    y_difference = point1[1] - point2[1]
    return math.atan2(y_difference, x_difference)

center_point = (400,300)

yellow = (255, 255, 0)
red = (255, 0, 0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_position = pygame.mouse.get_pos()
    # angle = angle_between(center_point, mouse_position)

    x_difference = mouse_position[0] - center_point[0]
    y_difference = mouse_position[1] - center_point[1]

    mouse_vector = MoveVector(vx=x_difference, vy=y_difference)
    compare_vector = MoveVector(speed=100, direction=math.pi / 8)

    dot_produt = mouse_vector.get_dot_product_normalized(compare_vector)
    angle_radians = mouse_vector.get_direction()
    distance = mouse_vector.get_speed()

    halfway_point = (center_point[0] + x_difference // 2, center_point[1] + y_difference // 2)

    angle_degrees = np.rad2deg(angle_radians)

    vx = int(50 * math.cos(angle_radians))
    vy = int(50 * math.sin(angle_radians))
    # print(vx, vy)
    win.fill(0)
    pygame.draw.circle(win, (0, 0, 255),
                       (center_point[0] + vx,
                        center_point[1] + vy),
                       5)



    show_text((10,10), str(center_point) + " - " + str(mouse_position))
    show_text((10,30), str(angle_degrees))
    show_text((10,50), "Dot product: "+str(dot_produt))
    pygame.draw.circle(win, yellow, center_point, 5)
    pygame.draw.circle(win, yellow, mouse_position, 5)
    pygame.draw.line(win, yellow, center_point, mouse_position)
    pygame.draw.line(win, red, center_point, (compare_vector.get_vx()+center_point[0], compare_vector.get_vy()+center_point[1]))
    # pygame.draw.line(win, RED, center_point, (mouse_position[0], center_point[1]))
    # pygame.draw.line(win, RED, mouse_position, (mouse_position[0], center_point[1]))
    # show_text(halfway_point, str(round(distance, 2)))
    # show_text((halfway_point[0], center_point[1]), str(round(x_difference, 2)))
    # show_text((mouse_position[0], halfway_point[1]), str(round(y_difference, 2)))
    pygame.display.flip()
    time.sleep(0.01)

pygame.exit()