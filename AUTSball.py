# -*- coding: utf8 -*-
import pygame, math, sys, game_object, vector

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)


class AUTSBallGame:
    def __init__(self):
        # Vakioita
        self.gravity = 0.1
        self.screen_size_x = 800
        self.screen_size_y = 600
        self.screen_center_point = self.screen_size_x // 2, self.screen_size_y // 2

        # Pygamen inittejä
        pygame.init()
        self.win = pygame.display.set_mode((self.screen_size_x, self.screen_size_y))
        pygame.display.set_caption("AUTSball")
        self.clock = pygame.time.Clock()

        # Latauskuva koska levelin latauksessa voi kestää jonkin aikaa
        self.loading_image = pygame.image.load('gfx/loading.png').convert_alpha()
        self.win.blit(self.loading_image, self.loading_image.get_rect())
        pygame.display.update()

        # TODO: tähän assettien esilataus
        # Instansioidaan leveli, tämä lataa myös level-kuvan joka voi olla iiisooo
        self.current_level = Level()
        # Instansioidaan pelaaja ja pallo
        self.player = { 0: PlayerSprite(level=self.current_level, parent=self) }
        self.ball = BallSprite(level=self.current_level, parent=self)

        self.viewscreen_rect = None
        self.background_view_rect = None

        self.score_green = 0
        self.score_red = 0

        self.quit_game = False
        self.frame_counter = 0

    def update(self):
        # Tämä estää errorin quitattaessa
        if self.quit_game is False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game = True

            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_UP]:
                self.player[0].accelerate()
            else:
                self.player[0].stop_acceleration()
            if pressed_keys[pygame.K_RIGHT]:
                self.player[0].rotate_right()
            if pressed_keys[pygame.K_LEFT]:
                self.player[0].rotate_left()
            if pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
                self.player[0].shoot()

            # Viewscreen rect: viewscreen absoluuttisissa koordinaateissa
            self.viewscreen_rect = (self.player[0].x - self.screen_size_x // 2,
                                    self.player[0].y - self.screen_size_y // 2,
                                    self.screen_size_x,
                                    self.screen_size_y)

            # Background view rect: näytetään levelistä oikea kohta
            self.background_view_rect = (self.screen_size_x // 2 - self.player[0].x,
                                         self.screen_size_y // 2 - self.player[0].y,
                                         self.screen_size_x,
                                         self.screen_size_y)

            # Spritejen päivitykset tässä
            BulletGroup.update(self.viewscreen_rect)
            BallGroup.update(self.viewscreen_rect)
            PlayerGroup.update()
            EffectGroup.update()
            TextGroup.update()

            # Päivitetään graffat vaan joka toisessa framessa
            if self.frame_counter % 2 == 0:
                self.update_graphics()

            # Pelilogiikan FPS target 60, eli graffoilla siis 30
            self.clock.tick(60)

        if self.quit_game:
            self.exit()

    def update_graphics(self):
        """ Grafiikoiden päivitysmetodi """

        # Ruutu tyhjäksi
        self.win.fill((0, 0, 0))
        # Piirretään levelistä vain viewscreenin kokoinen alue, pelaaja keskellä
        self.win.blit(self.current_level.image, self.background_view_rect)

        # Bullettien, pelaajan, pallon piirrot
        BulletGroup.draw(self.win)
        BallGroup.draw(self.win)
        PlayerGroup.draw(self.win)
        EffectGroup.draw(self.win)
        TextGroup.draw(self.win)

        # HUD
        # self.show_text((10, 10), "Speed: " + str(math.hypot(self.player[0].vx, self.player[0].vy)))
        self.show_text((10, 50), "FPS: " + str(self.clock.get_fps()))
        self.show_text((10, 10), str(self.score_green), color=green, font_size=40)
        self.show_text((750, 10), str(self.score_red), color=red, font_size=40)

        # Näytetään pallonsuuntamarkkeri
        # TODO: muuta pallon sijaan nuoli joka osoittaa oikeaan suuntaan
        # TODO: tee niin että jos pallo on lähempänä kuin 100 pikseliä niin markkeri on pallon päällä
        if self.player[0].attached_ball is None:
            ball_angle = self.get_ball_angle_in_radians(self.ball)
            vx = int(100 * math.cos(ball_angle))
            vy = int(100 * math.sin(ball_angle))
            pygame.draw.circle(self.win, (0, 0, 255),
                               (self.screen_size_x // 2 + vx, self.screen_size_y // 2 + vy), 5)

        # Displayn update
        pygame.display.update()

    def score(self, scoring_team):
        """ Tätä kutsutaan kun tulee maali """
        if scoring_team == 'red':
            self.score_red += 1
            goal_text_color = red
        elif scoring_team == 'green':
            self.score_green += 1
            goal_text_color = green
        DisappearingText(pos=self.screen_center_point, text="GOAL!!!", frames_visible=120,
                         color=goal_text_color, font_size=120, flashes=1)

    def get_ball_angle_in_radians(self, ball):
        """ Tämä auttaa pallon suuntamarkkerin piirrossa """
        point2 = (self.screen_size_x // 2, self.screen_size_y // 2)
        point1 = ball.rect.center
        x_difference = point1[0] - point2[0]
        y_difference = point1[1] - point2[1]
        return math.atan2(y_difference, x_difference)

    def show_text(self, pos, text, color=(255, 255, 255), bgcolor=(0, 0, 0), font_size=24):
        """ Utility-metodi tekstin näyttämiseen ruudulla """
        font = pygame.font.Font(None, font_size)
        textimg = font.render(text, 1, color, bgcolor)
        self.win.blit(textimg, pos)

    def exit(self):
        """ Tähän voi laittaa jotain mitä tulee ennen poistumista """
        pygame.quit()
        # Jostain syystä vaatii myös tämän, muuten jää infinite looppi taustalle vaikka pygame-ikkuna katoaakin
        sys.exit()

# Sprite-ryhmät
PlayerGroup = pygame.sprite.Group()
LevelGroup = pygame.sprite.Group()
BulletGroup = pygame.sprite.Group()
BallGroup = pygame.sprite.Group()
EffectGroup = pygame.sprite.Group()
TextGroup = pygame.sprite.Group()


class Level(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, LevelGroup)
        # self.image = pygame.image.load('gfx/test_arena_2400x1200.png').convert_alpha()
        self.image = pygame.image.load('gfx/test_arena_vertical_challenge.png').convert_alpha()
        self.size_x = self.image.get_width()
        self.size_y = self.image.get_height()
        self.rect = self.image.get_rect()
        self.center_point = self.size_x // 2, self.size_y // 2


class EffectSprite(game_object.GameObject):
    """ Yleinen efektisprite, tällä hetkellä tosin vain moottorin liekit """
    def __init__(self, image=None, attached_player=None, attached_ball=None, effect_type=None, visible=1, parent=None):
        game_object.GameObject.__init__(self, group=EffectGroup, image=image)
        self.attached_player = attached_player
        self.attached_ball = attached_ball
        self.effect_type = effect_type
        self.visible = visible

    def update(self):
        if self.visible:
            player_dir_radians = math.radians(self.attached_player.heading)
            dx = int(12 * math.sin(player_dir_radians))
            dy = int(12 * math.cos(player_dir_radians))
            self.rect.center = self.attached_player.rect.center[0] + dx, self.attached_player.rect.center[1] + dy
            self.rot_self_image_keep_size(self.attached_player.heading)

        else:
            # jos ei visible niin heitetään vaan jonnekin kuuseen
            self.rect.center = -100, -100

    def destroy(self):
        self.attached_player = None
        self.kill()


class BallSprite(game_object.GameObject):
    """ Pallo. Osaa liittää itsensä pelaajaan ja poistaa liitoksen. """
    def __init__(self, level=None, parent=None):
        game_object.GameObject.__init__(self, group=BallGroup, image_file='gfx/ball_50_red.png', level=level, parent=parent)
        self.start_position = self.level.center_point
        self.x, self.y = self.start_position

        # Player attachment
        self.attached_player = None
        self.attached_player_max_distance = 50  # "tetherin" pituus
        self.attached_player_max_distance_squared = self.attached_player_max_distance**2  # distance-laskelmia varten

        self.mass = 1.0
        self.max_speed = 10

        # Tämä tekee sen että tarkistetaan törmäys maaliin
        self.is_ball = 1

    def update(self, viewscreen_rect):
        """ Päivittää palloa. Vaatii viewscreen_rect:in että osaa laskea näyttämisen oikein. """
        self.viewscreen_rect = viewscreen_rect

        # Jos törmää pelaajaan niin liitetään siihen
        collide_list = pygame.sprite.spritecollide(self, PlayerGroup, dokill=False, collided=pygame.sprite.collide_circle)
        if len(collide_list) > 0:
            self.attach_to_player(collide_list[0])

        # Jos on liitetty pelaajaan ja jos on liian kaukana niin vetävät toisiaan puoleensa
        # Suht hyvä, voi viilata jos saa vielä paremmaksi
        # TODO: weightit ei tunnu vaikuttavan?
        # TODO: graffat tetherille
        if self.attached_player is not None:
            distance_to_player = self.distance(self.attached_player)
            if distance_to_player >= self.attached_player_max_distance:
                player_angle = game_object.get_angle_in_radians((self.attached_player.x, self.attached_player.y),
                                                                 (self.x, self.y))

                pull_vector_speed = (distance_to_player - self.attached_player_max_distance) * 0.02

                ball_pull_vector = vector.MoveVector(speed=pull_vector_speed, direction=player_angle)
                # Tässä rikotaan voiman ja vastavoiman lakia mutta who cares! (Newton pyörii haudassaan)
                player_pull_vector = vector.MoveVector(speed=pull_vector_speed * -1 * 0.4, direction=player_angle)

                self.move_vector.add_vector(ball_pull_vector)
                self.attached_player.move_vector.add_vector(player_pull_vector)

        self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_bullets(BulletGroup)

    def collide_tether(self, other_object):
        """ 
        Eksperimentaalinen tetherin törmäysmetodi. Ei toimi niin kuin haluaisin.
        Ideana tässä että tether-collide on oletettavasti ekvivalentti normaalille törmäykselle niin että
        objektien paikat vaihdetaan
        Ei tällä hetkellä käytössä
        """
        new_self = other_object
        new_other = self
        angle_to_other = game_object.get_angle_in_radians(new_other.rect.center, new_self.rect.center)
        new_self.move_vector.set_direction(angle_to_other - math.pi)
        new_other.move_vector.set_direction(angle_to_other)

        speed1 = new_self.move_vector.get_speed()
        speed2 = new_other.move_vector.get_speed()
        mass1 = new_self.mass
        mass2 = new_other.mass
        speed1_new = (mass2 / mass1) * speed2
        speed2_new = (mass1 / mass2) * speed1
        self.move_vector.set_speed(speed2_new * -1)
        other_object.move_vector.set_speed(speed1_new * -1)

    def reset(self):
        """ 
        HUOM! Tämä metodi overrideaa GameObjectin reset-metodin että osaa detachata pallon pelaajasta.
        Siksi kutsuu GameObjectin resetin näin käsin.
        """
        game_object.GameObject.reset(self)
        self.detach()

    def shoot(self, direction=0, speed=0, x=0, y=0):
        """ 
        Ampuu itsensä määritettyyn suuntaan, määritetyllä nopeudella, alkaen määritetyistä koordinaateista.
        Tätä kutsuu PlayerSpriten shoot-metodi, joka hoitaa detachauksen ja antaa tarvittavat tiedot
        """
        # Jostain syystä vaatii direktion korjauksen tässä
        self.move_vector.set_speed_direction(speed, math.radians(270 - direction))
        self.x = int(x)
        self.y = int(y)
        self.update_rect()

    def attach_to_player(self, player):
        """ 
        Tämä metodi liittää pallon pelaajaan. Olisi tarkoitus myös lisätä painoa mutta paino ei toimi
        oikein vielä.
        """
        self.attached_player = player
        player.attach_ball(self)
        # self.tether = EffectSprite(image=pygame.Surface((0,0)), effect_type='tether',
        #                            attached_ball=self, attached_player=player, parent=self.parent)
        # TODO: korjaa weight että tämä voidaan enabloida
        # self.attached_player.weight += self.weight

    def detach(self):
        """ Tämä metodi poistaa liitoksen pelaajaan. """
        # self.attached_player.weight -= self.weight
        if self.attached_player is not None:
            self.attached_player.detach_ball()
            self.attached_player = None
            # self.tether.kill()
            # self.tether = None



class BulletSprite(game_object.GameObject):
    """ direction asteina, tulee PlayerSpriten headingista """
    def __init__(self, parent=None, level=None, x=0, y=0, direction=0, parent_speed=0, speed=5, type='basic'):
        game_object.GameObject.__init__(self, group=BulletGroup, image_file='gfx/bullet_5.png', start_position=(x, y),
                                        level=level, parent=parent)
        self.rect.center = (x, y)
        self.move_vector.set_speed_direction(speed, math.radians(270 - direction))
        self.max_speed = 20
        # self.explosion_force = 1
        self.mass = 0.1

        self.is_bullet = 1

    def update(self, viewscreen_rect):
        self.viewscreen_rect = viewscreen_rect
        self.update_movement()
        self.check_out_of_bounds()

        # Tehdään nämä vain jos on olemassa
        if self in BulletGroup:
            self.check_collision_with_wall_and_goal()
            self.update_rect()

    def check_out_of_bounds(self):
        """ Overrideaa GameObjectin metodin koska pitää tuhota bulletti jos on out of bounds """
        if self.x < 0 or self.y < 0 or self.x >= self.level.size_x or self.y >= self.level.size_y:
            self.x = 0
            self.y = 0
            self.kill()


class PlayerSprite(game_object.GameObject):
    def __init__(self, level=None, parent=None):
        # Lisätään PlayerGroup-ryhmään
        game_object.GameObject.__init__(self, group=PlayerGroup, level=level, parent=parent, image_file='gfx/ship1_20px.png')

        # Graffat
        self.motor_flame_image = pygame.image.load('gfx/motor_flame_10.png').convert_alpha()
        self.thrust_gfx = EffectSprite(attached_player=self, image=self.motor_flame_image,
                                       effect_type='motorflame', visible=0, parent=parent)
        self.rect.center = self.parent.screen_center_point
        self.is_centered_on_screen = 1

        # Koordinaatit
        self.start_position = (700, 1200)
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.x, self.y

        # Heading ja thrust
        self.heading = 0  # HUOM! Heading asteina koska Pygame käyttää niitä rotaatioissa
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

    def update(self):
        # Lisätään liikemäärään thrust-vektori
        # Tässä jopa ottaa jo massan huomioon!
        self.move_vector.add_to_vx((self.thrust / self.mass * math.sin(math.radians(self.heading)) * -1))
        self.move_vector.add_to_vy((self.thrust / self.mass * math.cos(math.radians(self.heading)) * -1))

        self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_bullets(BulletGroup)

        # Lasketaan cooldownia
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

        # Jos on pallo kytkettynä niin lisätään paljon cooldownia
        if self.attached_ball is not None:
            self.cooldown_counter = self.cooldown_after_ball_shot

    def attach_ball(self, ball):
        self.attached_ball = ball

    def detach_ball(self):
        self.attached_ball = None

    def accelerate(self):
        self.thrust = self.max_thrust
        self.thrust_gfx.visible = 1

    def stop_acceleration(self):
        self.thrust = 0
        self.thrust_gfx.visible = 0

    def rotate_right(self):
        self.heading -= self.handling
        if self.heading < 0:
            self.heading += 360
        # TODO: laske rotaatiot latausvaiheessa valmiiksi
        self.rot_self_image_keep_size(self.heading)

    def rotate_left(self):
        self.heading += self.handling
        if self.heading > 360:
            self.heading -= 360
        self.rot_self_image_keep_size(self.heading)

    def shoot(self, bullet_list=None):
        # Ammutaan perusammus
        # Pelaajan nopeus vaikuttaa ammuksen vauhtiin
        # TODO: pelaajan nopeus lisää aina ammuksen nopeutta saman verran riippumatta siitä mihin suuntaan se ammutaan!
        # Asetetaan ammuksen alkupiste riittävän kauas pelaajasta ettei törmää saman tien siihen
        if self.cooldown_counter == 0:
            bullet_x = int(10 * math.sin(math.radians(self.heading)) * -1 + self.x)
            bullet_y = int(10 * math.cos(math.radians(self.heading)) * -1 + self.y)
            BulletSprite(level=self.level, parent=self.parent, x=bullet_x, y=bullet_y, direction=self.heading,
                         speed=10 + self.move_vector.get_speed())
            self.cooldown_counter = self.cooldown_basic_shot

        # Jos pallo on liitettynä niin ammutaan se
        if self.attached_ball is not None:
            ball_x = self.attached_ball.image.get_width() * math.sin(math.radians(self.heading)) * -1 + self.x
            ball_y = self.attached_ball.image.get_height() * math.cos(math.radians(self.heading)) * -1 + self.y

            self.attached_ball.shoot(x=ball_x, y=ball_y, direction=self.heading, speed=10)
            self.attached_ball.detach()


class DisappearingText(pygame.sprite.Sprite):
    """ Näyttää ruudulla tekstin x framen ajan """
    # TODO: tausta läpinäkyväksi
    def __init__(self, pos=(0,0), text="", frames_visible=60,
                 color=white, bgcolor=black, font_size=24, flashes=0, flash_interval=10):
        pygame.sprite.Sprite.__init__(self, TextGroup)

        self.frame_counter = 0
        self.frames_visible = frames_visible

        font = pygame.font.Font(None, font_size)
        self.image = font.render(text, 1, color, bgcolor)
        self.original_position = pos
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.flashes = flashes
        self.flash_interval = flash_interval
        self.visible = 1

    def update(self):
        self.frame_counter += 1
        if self.frame_counter > self.frames_visible:
            self.kill()

        if self.flashes and self.frame_counter % self.flash_interval == 0:
            self.toggle_image()

    def toggle_image(self):
        if self.visible:
            self.visible = 0
            self.rect.center = -100, -100
        else:
            self.visible = 1
            self.rect.center = self.original_position


if __name__ == '__main__':
    game = AUTSBallGame()
    while True:
        game.update()