import pygame, math, time, sys, vector, game_object
import numpy as np # onko loppujen lopuksi tarpeen?

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)


class AUTSBallGame:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("AUTSball")
        self.clock = pygame.time.Clock()

        # Latauskuva koska levelin latauksessa kestää jonkin aikaa
        self.loading_image = pygame.image.load('loading.png').convert_alpha()
        self.win.blit(self.loading_image, self.loading_image.get_rect())
        pygame.display.update()

        # Instansioidaan leveli, tämä lataa myös level-kuvan joka voi olla iiisooo
        self.current_level = Level()
        # Instansioidaan pelaaja ja pallo
        self.player = { 0: PlayerSprite(level=self.current_level, parent=self) }
        self.ball = BallSprite(level=self.current_level, parent=self)
        # print(dir(self.ball))

        self.viewscreen_rect = None
        self.background_view_rect = None

        self.score_green = 0
        self.score_red = 0

        self.quit_game = False
        self.frame_counter = 0

    class Constants:
        """ Sisältää vakioita kuten voi nimestä päätellä """
        gravity = 0.1
        screen_size_x = 800
        screen_size_y = 600
        screen_center_point = screen_size_x // 2, screen_size_y // 2
        # gravity_vector = np.array([math.pi, gravity])

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
            self.viewscreen_rect = (self.player[0].x - self.Constants.screen_size_x // 2,
                                    self.player[0].y - self.Constants.screen_size_y // 2,
                                    self.Constants.screen_size_x,
                                    self.Constants.screen_size_y)

            # Background view rect: näytetään levelistä oikea kohta
            self.background_view_rect = (self.Constants.screen_size_x // 2 - self.player[0].x,
                                         self.Constants.screen_size_y // 2 - self.player[0].y,
                                         self.Constants.screen_size_x,
                                         self.Constants.screen_size_y)

            # print("Viewscreen rect:", viewscreen_rect_1)
            # print("Player coordinates:", player[0].x, player[0].y)

            # Spritejen päivitykset tässä
            BulletGroup.update(self.viewscreen_rect)
            BallGroup.update(self.viewscreen_rect)
            PlayerGroup.update()
            EffectGroup.update()

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

        # HUD
        # self.show_text((10, 10), "Speed: " + str(math.hypot(self.player[0].vx, self.player[0].vy)))
        self.show_text((10, 30), "FPS: " + str(self.clock.get_fps()))
        self.show_text((10, 10), str(self.score_green), color=green, font_size=40)
        self.show_text((750, 10), str(self.score_red), color=red, font_size=40)

        # Näytetään pallonsuuntamarkkeri
        if self.player[0].attached_ball is None:
            ball_angle = self.get_ball_angle_in_radians(self.ball)
            vx = int(100 * math.cos(ball_angle))
            vy = int(100 * math.sin(ball_angle))
            pygame.draw.circle(self.win, (0, 0, 255),
                               (self.Constants.screen_size_x // 2 + vx, self.Constants.screen_size_y // 2 + vy), 5)

        # Displayn update
        pygame.display.update()

    def score(self, scoring_team):
        if scoring_team == 'red':
            self.score_red += 1
        elif scoring_team == 'green':
            self.score_green += 1

    def get_ball_angle_in_radians(self, ball):
        point2 = (self.Constants.screen_size_x // 2, self.Constants.screen_size_y // 2)
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


class Level(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, LevelGroup)
        self.image = pygame.image.load('test_arena_2400x1200.png').convert_alpha()
        self.size_x = self.image.get_width()
        self.size_y = self.image.get_height()
        self.rect = self.image.get_rect()
        self.center_point = self.size_x // 2, self.size_y // 2


class EffectSprite(game_object.GameObject):
    """ Yleinen efektisprite, tällä hetkellä tosin vain moottorin liekit """
    def __init__(self, image=None, attached_player=None, effect_type=None, visible=1):
        game_object.GameObject.__init__(self, group=EffectGroup, image=image)
        self.attached_player = attached_player
        self.type = effect_type
        self.visible = visible

    def update(self):
        if self.visible:
            player_dir_radians = math.radians(self.attached_player.heading)
            vx = int(12 * math.sin(player_dir_radians))
            vy = int(12 * math.cos(player_dir_radians))
            self.rect.center = self.attached_player.rect.center[0] + vx, self.attached_player.rect.center[1] + vy
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
        game_object.GameObject.__init__(self, group=BallGroup, image_file='ball_50.png', level=level, parent=parent)
        # self.image = pygame.image.load('ball_50.png').convert_alpha()
        # self.rect = self.image.get_rect()
        self.start_position = self.level.center_point
        self.x, self.y = self.start_position
        self.attached_player = None
        self.mass = 1
        self.max_speed = 10
        # Tämä tekee sen että tarkistetaan törmäys maaliin
        self.is_ball = 1

    def update(self, viewscreen_rect):
        """ Päivittää palloa. Vaatii viewscreen_rect:in että osaa laskea näyttämisen oikein. """
        self.viewscreen_rect = viewscreen_rect

        # Jos törmää pelaajaan niin liitetään siihen
        collide_list = pygame.sprite.spritecollide(self, PlayerGroup, False)
        if len(collide_list) > 0:
            self.attach_to_player(collide_list[0])

        # Jos on liitetty pelaajaan niin koordinaatit ja rect on samat kuin pelaajalla
        if self.attached_player is not None:
            # print("Ball update. Attached to player. Player x,y:", self.attached_player.x, self.attached_player.y)
            self.x = self.attached_player.x
            self.y = self.attached_player.y
            self.rect.center = self.attached_player.rect.center
        # Jos ei ole liitetty pelaajaan niin lasketaan liike
        else:
            self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_bullets()

    def reset(self):
        """ 
        HUOM! Tämä metodi overrideaa GameObjectin reset-metodin että osaa detachata pallon pelaajasta.
        Siksi kutsuu GameObjectin resetin näin käsin.
        """
        game_object.GameObject.reset(self)
        self.detach()

    def shoot(self, direction=0, speed=0, x=0, y=0):
        # print("Ball shoot - direction, speed:", direction, speed)
        # Jostain syystä vaatii direktion korjauksen tässä
        self.move_vector.set_magnitude_angle(speed, math.radians(270 - direction))
        self.x = int(x)
        self.y = int(y)
        self.update_rect()
        # print("ball.shoot - magnitude, angle:", self.move_vector.get_magnitude_angle())

    def check_collision_with_bullets(self):
        collide_list = pygame.sprite.spritecollide(self, BulletGroup, True)
        if len(collide_list) > 0:
            # print("Ball collision with bullet")
            # print("vx, vy:",self.vx, self.vy)
            # Törmäyksessä lisätään bulletin liikemäärä palloon
            # TODO: ota huomioon suhteelliset kulmat, ota huomioon objektien massat
            self.move_vector.set_vx(self.move_vector.get_vx() + collide_list[0].move_vector.get_vx() * collide_list[0].explosion_force)
            self.move_vector.set_vy(self.move_vector.get_vy() + collide_list[0].move_vector.get_vy() * collide_list[0].explosion_force)
            # print("vx, vy:", self.vx, self.vy)

    def attach_to_player(self, player):
        """ 
        Tämä metodi liittää pallon pelaajaan. Olisi tarkoitus myös lisätä painoa mutta paino ei toimi
        oikein vielä.
        """
        self.attached_player = player
        player.attach_ball(self)
        # TODO: korjaa weight että tämä voidaan enabloida
        # self.attached_player.weight += self.weight

    def detach(self):
        """ Tämä metodi poistaa liitoksen pelaajaan. """
        # self.attached_player.weight -= self.weight
        if self.attached_player is not None:
            self.attached_player.detach_ball()
            self.attached_player = None


class BulletSprite(game_object.GameObject):
    """ direction asteina, tulee PlayerSpriten headingista """
    def __init__(self, parent=None, level=None, x=0, y=0, direction=0, parent_speed=0, speed=5, type='basic'):
        game_object.GameObject.__init__(self, group=BulletGroup, image_file='bullet_5.png', start_position=(x, y),
                                        level=level, parent=parent)
        self.rect.center = (x, y)
        self.move_vector.set_magnitude_angle(speed, math.radians(270 - direction))
        self.max_speed = 20
        self.explosion_force = 1

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
        game_object.GameObject.__init__(self, group=PlayerGroup, level=level, parent=parent, image_file='ship1_20px.png')

        # Parent
        # self.parent = parent

        # Graffat
        # self.original_image = pygame.image.load('ship1_20px.png').convert_alpha()
        self.motor_flame_image = pygame.image.load('motor_flame_10.png').convert_alpha()
        self.thrust_gfx = EffectSprite(attached_player=self, image=self.motor_flame_image,
                                       effect_type='motorflame', visible=0)
        # self.level = level # level-objekti
        # self.image = self.original_image
        # self.rect = self.image.get_rect()
        self.rect.center = self.parent.Constants.screen_center_point
        self.is_centered_on_screen = 1

        # Koordinaatit
        self.x = 800
        self.y = 600
        self.x_previous = 800
        self.y_previous = 600

        # Liikevektori
        # TODO: ota käyttöön myös muissa kuin PlayerSpritessä
        # self.move_vector = vector.MoveVector()
        self.heading = 0
        self.thrust = 0

        # Pallo
        self.attached_ball = None

        # Shipin ominaisuudet
        self.handling = int(5) # kuinka monta astetta kääntyy per frame
        self.max_thrust = 0.35 # kun FPS 60 ja ei weightiä niin 0.5 on tässä aika hyvä
        self.max_speed = 10
        self.mass = 1
        self.cooldown_basic_shot = 5 # framea
        self.cooldown_ball_attached = 60 # cooldown sen jälkeen kun pallo on ammuttu
        self.cooldown_counter = 0 # cooldown-counter1

    def update(self):
        # Lisätään liikemäärään thrust-vektori
        # Tässä jopa ottaa jo massan huomioon!
        self.move_vector.set_vx(self.move_vector.get_vx() + (self.thrust / self.mass * math.sin(math.radians(self.heading)) * -1))
        self.move_vector.set_vy(self.move_vector.get_vy() + (self.thrust / self.mass * math.cos(math.radians(self.heading)) * -1))

        self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_bullets(BulletGroup)

        # Lasketaan cooldownia
        if self.cooldown_counter != 0:
            self.cooldown_counter -= 1

        # Jos on pallo kytkettynä niin lisätään paljon cooldownia
        if self.attached_ball is not None:
            self.cooldown_counter = self.cooldown_ball_attached

        # print("Player x,y:", self.x, self.y)

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
        if self.heading < -360:
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
            bullet_x = int(10 * math.sin(np.deg2rad(self.heading)) * -1 + self.x)
            bullet_y = int(10 * math.cos(np.deg2rad(self.heading)) * -1 + self.y)
            bullet = BulletSprite(level=self.level, parent=self.parent, x=bullet_x, y=bullet_y, direction=self.heading,
                                  speed=10 + self.move_vector.get_magnitude())
            self.cooldown_counter = self.cooldown_basic_shot

        # Jos pallo on liitettynä niin ammutaan se
        if self.attached_ball is not None:
            ball_x = self.attached_ball.image.get_width() * math.sin(np.deg2rad(self.heading)) * -1 + self.x
            ball_y = self.attached_ball.image.get_height() * math.cos(np.deg2rad(self.heading)) * -1 + self.y

            self.attached_ball.shoot(x=ball_x, y=ball_y, direction=self.heading, speed=10)
            self.attached_ball.detach()

if __name__ == '__main__':
    game = AUTSBallGame()
    while True:
        game.update()