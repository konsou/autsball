# -*- coding: utf8 -*-
import game_object
import AUTSball
import pygame
""" TOTAALISEN KESKEN """

background_group = pygame.sprite.GroupSingle()


class DemoPlayer(AUTSball.PlayerSprite):
    def __init__(self, team, level):
        # Lisätään PlayerGroup-ryhmään
        game_object.GameObject.__init__(self, group=AUTSball.PlayerGroup, level=level, image_file='gfx/ship1_red_20px.png')

        # Graffat
        self.motor_flame_image = pygame.image.load('gfx/motor_flame_10.png').convert_alpha()
        self.thrust_gfx = AUTSball.EffectSprite(attached_player=self, image=self.motor_flame_image,
                                       effect_type='motorflame', visible=0)
        self.viewscreen_rect = (0,0,800,600)

        # Koordinaatit
        self.start_position = (100, 100)
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.x, self.y

        # Heading ja thrust
        self.heading = 0
        self.thrust = 0

        # Pallo
        self.attached_ball = None

        # Shipin ominaisuudet
        self.handling = int(5) # kuinka monta astetta kääntyy per frame
        self.max_thrust = 0.35 # kun FPS 60, gravity 0.1 ja mass 1 niin 0.35 on aika hyvä
        self.max_speed = 10
        self.mass = 1.0
        self.cooldown_basic_shot = 5 # framea
        self.cooldown_after_ball_shot = 60 # cooldown sen jälkeen kun pallo on ammuttu
        self.cooldown_counter = 0 # cooldown-counter1

        self.gravity_affects = 0
        self.team = team
        if team == 'red':
            self.image = pygame.image.load('gfx/ship1_red_20px.png').convert_alpha()
        else:
            self.image = pygame.image.load('gfx/ship1_green_20px.png').convert_alpha()


class DemoBall(AUTSball.BallSprite):
    def __init__(self, level):
        AUTSball.BallSprite.__init__(self, level=level)
        self.gravity_affects = 0
        self.image = pygame.image.load('gfx/ball_50_red.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (300, 300)


class BackgroundAction(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, background_group)
        level = AUTSball.Level(image=pygame.Surface((800, 600)))
        ship1 = DemoPlayer(team='green', level=level)
        ship2 = DemoPlayer(team='red', level=level)
        ball1 = DemoBall(level=level)
        self.image = pygame.Surface((800, 600))
        self.rect = self.image.get_rect()

    def update(self):
        AUTSball.PlayerGroup.update()
        AUTSball.BallGroup.update()

        AUTSball.PlayerGroup.draw(self.image)
        AUTSball.BallGroup.draw(self.image)

def debug_run():
    pygame.init()
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

