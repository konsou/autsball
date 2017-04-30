# -*- coding: utf-8 -*-
import pygame, vector

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)


class GameObject(pygame.sprite.Sprite):
    """ Classi joka perii pygamen Spriten ja lisää yleisiä peliobjektin käyttäytymiseen liittyviä juttuja """
    # TODO: muuta nämä niin että vakioarvot ei tule tässä argumentteina vaan selkeämmin alempana asetetaan arvoihinsa
    # ja sitten instansioinnissa voi tarvittaessa overrideta
    def __init__(self, level=None, parent=None, group=None, image_file=None, image=None, start_position=None):
        # Pygame-Spriten init
        pygame.sprite.Sprite.__init__(self, group)

        # parent on itse peliobjekti
        self.parent = parent

        # level-objekti
        self.level = level

        # Jos image on valmiiksi kuvaobjekti niin käytetään sitä
        if image is not None:
            self.image = image
            self.rect = self.image.get_rect()
        # Jos on annettu kuvatiedosto niin luetaan se
        elif image_file is not None:
            self.image = pygame.image.load(image_file).convert_alpha()
            self.rect = self.image.get_rect()
        # Tämä tarvitaan rotaatioita varten
        self.original_image = self.image
        self.size = (self.image.get_width() + self.image.get_height()) // 2

        # SFX
        self.wall_collide_sound = None

        # Start positio on levelin keskellä jos muuta ei ole määritetty
        if start_position is None:
            if level is not None:
                self.start_position = self.level.center_point
            else:
                self.start_position = 0, 0
        else:
            self.start_position = start_position

        # Koordinaattien määritys
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.start_position

        # Liikkumisvektori - sisältää sekä vx/vy että magnitude/angle (radiaaneina)
        self.move_vector = vector.MoveVector()

        # Peliobjektin ominaisuuksia - oletusarvot
        self.mass = 1
        self.max_speed = 30
        self.gravity_affects = 1
        self.is_ball = 0
        self.is_bullet = 0
        self.is_centered_on_screen = 0

        # Tämä päivitetään myöhemmin, initoidaan kuitenkin ettei PyCharm herjaa
        self.viewscreen_rect = None

    def reset(self):
        """ Resetoi position ja asettaa nopeuden nollaan. Päivittää rectin. """
        self.x, self.y = self.start_position
        self.move_vector.set_magnitude(0)
        self.update_rect()

    def update_rect(self):
        """ 
        Päivittää objektin rectin ottamaan huomioon viewscreenin 
        Tämä metodi on tärkeää muistaa kutsua kun liikuttelee objektia! Muuten sekoaa. 
        """
        if not self.is_centered_on_screen:
            self.rect.center = (self.x - self.viewscreen_rect[0],
                                self.y - self.viewscreen_rect[1])

    def update_movement(self):
        """
        Päivittää spriten koordinaatit move_vectorin ja gravityn pohjalta 
        """
        # Gravityn vaikutus
        if self.gravity_affects:
            self.move_vector.add_to_vy(self.parent.gravity)

        # Max speed rajoittaa
        self.move_vector.set_magnitude(min(self.move_vector.get_magnitude(), self.max_speed))

        # Muutetaan koordinaatteja liikemäärän mukaan
        self.x_previous = int(self.x)
        self.y_previous = int(self.y)
        self.x = int(self.move_vector.get_vx() + self.x)
        self.y = int(self.move_vector.get_vy() + self.y)

        # Päivitetään rect että ottaa viewscreenin huomioon
        self.update_rect()

    def rot_self_image_keep_size(self, angle):
        """rotate an image while keeping its center and size"""
        # Tämä copypastettu jostain netistä. Loppujen lopuksi en ole varma onko tarpeen vai ei.
        orig_rect = self.rect
        rot_image = pygame.transform.rotate(self.original_image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.image = rot_image

    def check_out_of_bounds(self):
        """ Pitää objektin pelialueen sisällä """
        x_before = self.x
        y_before = self.y
        self.x = max(0, self.x)
        self.x = min(self.level.size_x - 1, self.x)
        self.y = max(0, self.y)
        self.y = min(self.level.size_y - 1, self.y)
        # Jos koordinaatteja muutettiin (eli oli out of bounds) niin muutetaan liikemäärää
        if self.x != x_before:
            self.move_vector.set_vx(0)
        elif self.y != y_before:
            self.move_vector.set_vy(0)

    def check_collision_with_wall_and_goal(self):
        """ Tarkastaa törkmäyksen seiniin  ja mahdollisesti maaliin - eli juttuihin level-taustassa """
        # Katotaan mikä väri on levelissä tässä pisteessä - skipataan alfa
        current_point = self.level.image.get_at((self.x, self.y))[:3]

        # Jos väri on muuta kuin musta/vihreä/punainen niin on törmäys ja vauhti menee nollaan
        if current_point not in (black, red, green):
            # Soitetaan seinääntörmäysääni seuraavin ehdoin:
            #  -nopeus yli 5 (ettei ihan pienistä tule jatkuvaa pärinää)
            #  -jos on liikuttu
            #  -ääni on olemassa
            if self.move_vector.get_magnitude() > 5:
                if self.wall_collide_sound and self.x != self.x_previous and self.y != self.y_previous:
                    # print("Playing thump")
                    self.force_play_sound(self.wall_collide_sound)
            if self.is_bullet:
                # Tuhoaa seinää törmätessä ja myös itsensä jos on bullet
                pygame.draw.circle(self.level.image, black, (self.x, self.y), self.size - 1)
                self.kill()
            else:
                # Vauhti loppuu kuin seinään
                self.move_vector.set_magnitude(0)
                # Vähän estetään seinän sisään menemistä tällä
                self.x = self.x_previous
                self.y = self.y_previous

        # Jos objekti on pallo niin katsotaan onko maalissa
        if self.is_ball:
            # Punainen maali - piste vihreälle
            if current_point == red:
                self.parent.score('green')
                self.reset()
            # Vihreä maali - piste punaiselle
            elif current_point == green:
                self.parent.score('red')
                self.reset()

    def check_collision_with_bullets(self, BulletGroup):
        collide_list = pygame.sprite.spritecollide(self, BulletGroup, True)
        if len(collide_list) > 0:
            # TODO: laske massojen vaikutukset törmäyksessä
            # TODO: laske vektorit oikein objektien suhteellisten kulmien mukaan
            self.move_vector.add_vector(collide_list[0].move_vector)

    def force_play_sound(self, sound, duration=0):
        # Soitetaan ääni, pakotetaan sille kanava auki
        # if sound.get_num_channels() == 0:
        # print("Playing sound", sound)
        pygame.mixer.find_channel(True).play(sound, duration)
        # else:
        #     print("Not playing sound", sound)


