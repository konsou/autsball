# -*- coding: utf8 -*-
import pygame, math, vector, game_object, AUTSball


center_point = (400,300)

yellow = (255, 255, 0)
red = (255, 0, 0)
green = (0, 255, 0)

pygame.init()
win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Angle finding test")

class TestBall(AUTSball.BallSprite):
    def __init__(self, level):
        AUTSball.BallSprite.__init__(self, level=level, parent=DummyParent())
        self.gravity_affects = 1
        self.start_position = 400, 300
        self.rect.center = self.start_position
        self.attached_player_max_distance = 100  # "tetherin" pituus
        self.attached_player_max_distance_squared = self.attached_player_max_distance**2  # distance-laskelmia varten


    def update(self, viewscreen_rect):
        AUTSball.BallSprite.update(self, viewscreen_rect)
        distance_squared_to_player = self.distance_squared(self.attached_player)
        if distance_squared_to_player > self.attached_player_max_distance_squared:
            player_angle = game_object.get_angle_in_radians((self.attached_player.x, self.attached_player.y),
                                                             (self.x, self.y))
            pull_vector_speed = (distance_squared_to_player - self.attached_player_max_distance_squared) / 10000
            pull_vector_normalized = vector.MoveVector(speed=1, direction=player_angle)
            self.dotproduct = self.move_vector.get_dot_product_normalized(vector.MoveVector(speed=1, direction=player_angle + math.pi))
            # print(self.dotproduct)
            self.move_vector.add_vector(vector.MoveVector(speed=pull_vector_speed, direction=player_angle))
            self.attached_player.move_vector.add_vector(vector.MoveVector(speed=pull_vector_speed * -1, direction=player_angle))
            # self.move_vector.set_speed(self.move_vector.get_speed() * 0.95)


class TestPlayer(AUTSball.PlayerSprite):
    def __init__(self, level):
        AUTSball.PlayerSprite.__init__(self, level=level, parent=DummyParent())
        self.gravity_affects = 0
        self.is_centered_on_screen = 0
        self.viewscreen_rect = 0, 0, 800, 600

class DummyParent():
    screen_center_point = 400,300
    gravity = 0.1

class EmptyLevel(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, AUTSball.LevelGroup)
        # self.image = pygame.image.load('gfx/test_arena_2400x1200.png').convert_alpha()
        self.image = pygame.Surface((800, 600))
        self.size_x = self.image.get_width()
        self.size_y = self.image.get_height()
        self.rect = self.image.get_rect()
        self.center_point = self.size_x // 2, self.size_y // 2

def show_text(pos, text, color=(255, 255, 255), bgcolor=(0, 0, 0), fontSize=24):
    """ Utility-metodi tekstin näyttämiseen ruudulla """
    global win
    font = pygame.font.Font(None, fontSize)
    textimg = font.render(text, 1, color, bgcolor)
    win.blit(textimg, pos)


level = EmptyLevel()
ball = TestBall(level=level)
player = TestPlayer(level=level)

ball.attached_player = player
player.attached_ball = ball

clock = pygame.time.Clock()

viewscreen_rect = 0, 0, 800, 600

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_position = pygame.mouse.get_pos()
    player.x, player.y = mouse_position
    player.update_rect()
    distance_squared = ball.distance_squared(player)
    distance = ball.distance(player)

    if distance_squared >= 10000:
        line_color = yellow
    else:
        line_color = green

    win.fill(0)
    AUTSball.BallGroup.update(viewscreen_rect)
    AUTSball.PlayerGroup.update()

    AUTSball.LevelGroup.draw(win)
    AUTSball.BallGroup.draw(win)
    AUTSball.PlayerGroup.draw(win)

    pygame.draw.line(win, line_color, (ball.x, ball.y), (player.x, player.y), 2)

    show_text((10,10), str(center_point) + " - " + str(mouse_position))
    show_text((10, 30), "Dist squared: " + str(distance_squared))
    show_text((10, 50), "Dist: " + str(distance))

    pygame.display.flip()
    clock.tick(30)

pygame.exit()