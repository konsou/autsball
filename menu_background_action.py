# -*- coding: utf8 -*-
import game_object
import AUTSball
import pygame
import math
import random

""" IHAN HIRVEÄ SOTKU MUTTA TOIMII PÄÄOSIN """
# TODO: MAJOR CLEANUP

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)

background_group = pygame.sprite.GroupSingle()


class DemoPlayer(AUTSball.PlayerSprite):
    def __init__(self, team=None, level=None, parent=None, pos=None):
        if team == 'red':
            image = pygame.image.load('gfx/ship1_red_20px.png').convert_alpha()
        else:
            image = pygame.image.load('gfx/ship1_green_20px.png').convert_alpha()

        # Lisätään PlayerGroup-ryhmään
        game_object.GameObject.__init__(self, group=AUTSball.PlayerGroup, level=level, parent=parent,
                                        image=image)

        # Graffat
        self.motor_flame_image = pygame.image.load('gfx/motor_flame_10.png').convert_alpha()
        self.thrust_gfx = AUTSball.EffectSprite(attached_player=self, image=self.motor_flame_image,
                                                effect_type='motorflame', visible=0)
        self.viewscreen_rect = (0, 0, 800, 600)

        # Koordinaatit

        # Heading ja thrust
        self.heading = 0
        self.thrust = 0

        # Pallo
        self.attached_ball = None

        # Shipin ominaisuudet
        self.handling = int(5)  # kuinka monta astetta kääntyy per frame
        self.max_thrust = 0.35  # kun FPS 60, gravity 0.1 ja mass 1 niin 0.35 on aika hyvä
        self.max_speed = 10
        self.mass = 1.0
        self.cooldown_basic_shot = 5  # framea
        self.cooldown_after_ball_shot = 60  # cooldown sen jälkeen kun pallo on ammuttu
        self.cooldown_counter = 0  # cooldown-counter1

        self.gravity_affects = 1
        self.team = team

        if pos is not None:
            self.start_position = pos
        else:
            if self.team == 'red':
                self.start_position = (700, 300)
            else:
                self.start_position = (100, 300)

        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.x, self.y

        self.goal_green_pos = 50, 300
        self.goal_red_pos = 750, 300
        self.goal = 0,0

    def update(self):
        if self.attached_ball is None:
            self.goal = self.parent.ball_pos

        else:
            if self.team == 'red':
                self.goal = self.goal_green_pos
            else:
                self.goal = self.goal_red_pos
        # print("Team, goal point:", self.team, goal)
        # print("Ball attached:", self.attached_ball)
        # pygame.draw.line(window, game_object.blue, goal, (self.x, self.y))

        new_heading = 270 - math.degrees(game_object.get_angle_in_radians(self.goal, (self.x, self.y)))
        self.heading = new_heading
        self.rot_self_image_keep_size(self.heading)

        # heading_difference = game_object.get_angle_difference(self.heading, new_heading, degrees=1)
        # print("Heading old, goal, difference:", self.heading, new_heading, heading_difference)
        # if heading_difference > 0:
            # print("Rotating right...")
            # self.rotate_right()
        # else:
            # print("Rotating left...")
            # self.rotate_left()
        # print("New heading:", self.heading)
        # print("---")
        self.accelerate()
        if self.attached_ball is None:
            if random.randint(1, 20) == 1:
                self.shoot()

        AUTSball.PlayerSprite.update(self)

    def shoot(self):
        """ Pitää overrideta kun randomisyystä vakioarvot ei toimi """
        if self.cooldown_counter == 0:
            bullet_x = int(20 * math.sin(math.radians(self.heading)) * -1 + self.x)
            bullet_y = int(20 * math.cos(math.radians(self.heading)) * -1 + self.y)
            AUTSball.BulletSprite(level=self.level, parent=self.parent, x=bullet_x, y=bullet_y, direction=self.heading,
                         speed=20)
            self.cooldown_counter = self.cooldown_basic_shot


class DemoBall(AUTSball.BallSprite):
    def __init__(self, level, parent):
        AUTSball.BallSprite.__init__(self, level=level, parent=parent)
        self.gravity_affects = 1
        self.image = pygame.image.load('gfx/ball_50_red.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.start_position = (400, 300)
        self.rect.center = self.start_position
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.start_position


class BackgroundAction(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, background_group)

        # Vakioita
        self.gravity = 0.1
        self.screen_size_x = 800
        self.screen_size_y = 600
        self.screen_center_point = self.screen_size_x // 2, self.screen_size_y // 2

        self.level = AUTSball.Level(image_file='gfx/menu_background_level.png')
        self.ship1 = DemoPlayer(team='green', level=self.level, parent=self, pos=(700, 200))
        self.ship2 = DemoPlayer(team='green', level=self.level, parent=self, pos=(700, 300))
        self.ship3 = DemoPlayer(team='green', level=self.level, parent=self, pos=(700, 400))
        self.ship4 = DemoPlayer(team='red', level=self.level, parent=self, pos=(100, 200))
        self.ship5 = DemoPlayer(team='red', level=self.level, parent=self, pos=(100, 300))
        self.ship6 = DemoPlayer(team='red', level=self.level, parent=self, pos=(100, 400))
        self.ball = DemoBall(level=self.level, parent=self)

        coders = ['Konso', 'Muumi', 'Tursa']
        random.shuffle(coders)
        coders_string = ', '.join(coders)
        credits_text = "Idea: Konso"+30*" "+"Code: "+coders_string+30*" "+"Music: Pera"+30*" "+"Your name can be here!"
        AUTSball.ScrollingText(y_pos=590, screen_size_x=800, text=credits_text, scroll_speed=3)

        self.image = pygame.Surface((800, 600))
        self.rect = self.image.get_rect()
        self.viewscreen_rect = (0, 0, 800, 600)

        self.ball_pos = (self.ball.x, self.ball.y)

        self.score_green = 0
        self.score_red = 0



    def update(self):
        self.ball_pos = (self.ball.x, self.ball.y)

        AUTSball.BulletGroup.update(self.viewscreen_rect)
        AUTSball.BallGroup.update(self.viewscreen_rect)
        AUTSball.PlayerGroup.update()
        AUTSball.EffectGroup.update()
        AUTSball.TextGroup.update()

        AUTSball.LevelGroup.draw(self.image)
        AUTSball.BallGroup.draw(self.image)
        AUTSball.PlayerGroup.draw(self.image)
        AUTSball.BulletGroup.draw(self.image)
        AUTSball.EffectGroup.draw(self.image)
        AUTSball.TextGroup.draw(self.image)

        self.show_text((10, 10), str(self.score_green), color=green, font_size=40)
        self.show_text((750, 10), str(self.score_red), color=red, font_size=40)

    def show_text(self, pos, text, color=(255, 255, 255), bgcolor=(0, 0, 0), font_size=24):
        """ Utility-metodi tekstin näyttämiseen ruudulla """
        font = pygame.font.Font(None, font_size)
        textimg = font.render(text, 1, color, bgcolor)
        self.image.blit(textimg, pos)

    def score(self, scoring_team=None):
        self.ship1.detach_ball()
        self.ship2.detach_ball()
        self.ship3.detach_ball()
        self.ship4.detach_ball()
        self.ship5.detach_ball()
        self.ship6.detach_ball()
        """ Tätä kutsutaan kun tulee maali """
        if scoring_team == 'red':
            self.score_red += 1
            goal_text_color = AUTSball.red
        elif scoring_team == 'green':
            self.score_green += 1
            goal_text_color = AUTSball.green
        AUTSball.DisappearingText(pos=(400,525), text="GOAL!!!", frames_visible=60,
                                  color=goal_text_color, font_size=120, flashes=1)

    def kill_me(self):
        AUTSball.LevelGroup.empty()
        AUTSball.BallGroup.empty()
        AUTSball.PlayerGroup.empty()
        AUTSball.BulletGroup.empty()
        AUTSball.EffectGroup.empty()
        AUTSball.TextGroup.empty()
        background_group.empty()
        self.kill()


def debug_run():
    pygame.init()
    global window
    window = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Menu test")
    clock = pygame.time.Clock()

    background_action = BackgroundAction()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window.fill((0, 0, 0))
        background_group.update()
        background_group.draw(window)

        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == '__main__':
    debug_run()

