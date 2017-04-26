# -*- coding: utf8 -*-
from math import acos
from math import sqrt
from math import pi
import pygame, math, time
import numpy as np

""" TOIMII! """

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
    # direction = angle_between(center_point, mouse_position)

    x_difference = mouse_position[0] - center_point[0]
    y_difference = mouse_position[1] - center_point[1]


    halfway_point = (center_point[0] + x_difference // 2, center_point[1] + y_difference // 2)

    distance = math.hypot(x_difference, y_difference)
    #direction = np.rad2deg(math.asin(y_difference / distance))
    # angle_radians = math.atan2(y_difference, x_difference)
    angle_radians = get_angle_in_radians(mouse_position, center_point)
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
    pygame.draw.circle(win, yellow, center_point, 5)
    pygame.draw.circle(win, yellow, mouse_position, 5)
    pygame.draw.line(win, yellow, center_point, mouse_position)
    pygame.draw.line(win, red, center_point, (mouse_position[0], center_point[1]))
    pygame.draw.line(win, red, mouse_position, (mouse_position[0], center_point[1]))
    show_text(halfway_point, str(round(distance, 2)))
    show_text((halfway_point[0], center_point[1]), str(round(x_difference, 2)))
    show_text((mouse_position[0], halfway_point[1]), str(round(y_difference, 2)))
    pygame.display.flip()
    time.sleep(0.01)

pygame.exit()