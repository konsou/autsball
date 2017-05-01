# -*- coding: utf-8 -*-
import pygame
import vector
import math
import copy
from colors import *

class GameObject(pygame.sprite.Sprite):
    """ Classi joka perii pygamen Spriten ja lisää yleisiä peliobjektin käyttäytymiseen liittyviä juttuja """
    # TODO: muuta nämä niin että vakioarvot ei tule tässä argumentteina vaan selkeämmin alempana asetetaan arvoihinsa
    # ja sitten instansioinnissa voi tarvittaessa overrideta
    def __init__(self, level=None, parent=None, group=None, image_file=None, image=None, start_position=None):
        # Pygame-Spriten init
        pygame.sprite.Sprite.__init__(self, group)
        
        # Tämä laskee myös rectin, sizen ja radiuksen
        self.load_image(image=image, image_file=image_file)

        # parent on itse peliobjekti
        self.parent = parent

        # level-objekti
        self.level = level

        # SFX
        self.wall_collide_sound = None
        self.bullet_collide_sound = None

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

        # Liikkumisvektori - sisältää sekä vx/vy että speed/direction (radiaaneina)
        self.move_vector = vector.MoveVector()

        # Peliobjektin ominaisuuksia - oletusarvot
        self.mass = 1
        self.max_speed = 30
        self.gravity_affects = 1
        self.is_ball = 0
        self.is_bullet = 0
        self.is_centered_on_screen = 0

        # Attachit
        self.attached_player = None
        self.attached_ball = None

        # Tämä päivitetään myöhemmin, initoidaan kuitenkin ettei PyCharm herjaa
        self.viewscreen_rect = None

    def load_image(self, image=None, image_file=None):
        """ Lataa kuvan spritelle. Asettaa rect, radius, size."""
        # Jos image on valmiiksi kuvaobjekti niin käytetään sitä
        if image is not None:
            self.image = image
        # Jos on annettu kuvatiedosto niin luetaan se
        elif image_file is not None:
            self.image = pygame.image.load(image_file).convert_alpha()
        # Tämä tarvitaan rotaatioita varten
        self.original_image = self.image
        # Size on tämmöinen yhden luvun approksimaatio objektin koosta - neliöllä sivun pituus, ympyrällä halkaisija
        # Suorakulmiolla sivujen pituuksien keskiarvo
        self.size = (self.image.get_width() + self.image.get_height()) // 2
        # Radiusta tarvii collision detectionissa
        self.rect = self.image.get_rect()
        self.radius = (self.size + 1) // 2
        self.original_radius = self.radius

    def reset(self):
        """ Resetoi position ja asettaa nopeuden nollaan. Päivittää rectin. """
        self.x, self.y = self.start_position
        self.move_vector.set_speed(0)
        self.update_rect()
        if self.attached_player is not None:
            self.attached_player.detach()
            self.detach()
        if self.attached_ball is not None:
            self.attached_ball.detach()
            self.detach()



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
        self.move_vector.set_speed(min(self.move_vector.get_speed(), self.max_speed))

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
        if current_point not in (BLACK, RED, GREEN):
            # Soitetaan seinääntörmäysääni seuraavin ehdoin:
            #  -nopeus yli 3 (ettei ihan pienistä tule jatkuvaa pärinää)
            #  -jos on liikuttu
            #  -ääni on olemassa
            if self.move_vector.get_speed() > 3:
                if self.wall_collide_sound and self.x != self.x_previous and self.y != self.y_previous:
                    # print("Playing thump")
                    self.force_play_sound(self.wall_collide_sound)
            if self.is_bullet:
                # Tuhoaa seinää törmätessä ja myös itsensä jos on bullet
                pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
                self.kill()
            else:
                # Vauhti loppuu kuin seinään
                self.move_vector.set_speed(0)
                # Vähän estetään seinän sisään menemistä tällä
                self.x = self.x_previous
                self.y = self.y_previous

        # Jos objekti on pallo niin katsotaan onko maalissa
        if self.is_ball:
            # Punainen maali - piste vihreälle
            if current_point == RED:
                self.parent.score('GREEN')
                self.reset()
            # Vihreä maali - piste punaiselle
            elif current_point == GREEN:
                self.parent.score('RED')
                self.reset()

    def speculate_collision_with_wall(self):
        """ Spekuloi mahdollista törmäystä walliin - onpahan taas huonosti toteutettu (duplikoi koodia) mutta toimii """
        move_vector_copy = copy.copy(self.move_vector)

        # Gravityn vaikutus
        if self.gravity_affects:
            move_vector_copy.add_to_vy(self.parent.gravity)

        # Max speed rajoittaa
        move_vector_copy.set_speed(min(move_vector_copy.get_speed(), self.max_speed))

        # Muutetaan koordinaatteja liikemäärän mukaan
        x = int(move_vector_copy.get_vx() + self.x)
        y = int(move_vector_copy.get_vy() + self.y)

        # Out of bounds-check
        x = max(0, x)
        x = min(self.level.size_x - 1, x)
        y = max(0, y)
        y = min(self.level.size_y - 1, y)

        # Katotaan mikä väri on levelissä tässä pisteessä - skipataan alfa
        current_point = self.level.image.get_at((x, y))[:3]
        # print("Current point (copy):", current_point)
        if current_point not in (BLACK, RED, GREEN):
            #print("Speculative collision detected")
            return 1
        else:
            return 0


    def check_collision_with_bullets(self, BulletGroup):
        collide_list = pygame.sprite.spritecollide(self, BulletGroup, dokill=True, collided=pygame.sprite.collide_circle)
        if len(collide_list) > 0:
            self.collide_circle(collide_list[0])
            if self.bullet_collide_sound is not None:
                self.force_play_sound(self.bullet_collide_sound)

    def check_collision_with_players(self, playergroup):
        collide_list = pygame.sprite.spritecollide(self, playergroup, dokill=False,
                                                   collided=pygame.sprite.collide_circle)
        for colliding_player in collide_list:
            if colliding_player != self:
                self.collide_circle(collide_list[0])
        
    def collide_circle(self, other_object):
        """ 
        Törmäyttää kaksi ympyrän muotoista GameObjectia ja laskee niiden suunnat ja liikemäärät uusiksi.
        Jopa ottaa massat huomioon!
        Vähän luulen että tässä on vielä viilaamisen varaa, ei tunnu aivan oikealta kaikissa tilanteissa...
        """
        angle_to_other = get_angle_in_radians(other_object.rect.center, self.rect.center)
        self.move_vector.set_direction(angle_to_other - math.pi)
        other_object.move_vector.set_direction(angle_to_other)

        speed1 = self.move_vector.get_speed()
        speed2 = other_object.move_vector.get_speed()
        mass1 = self.mass
        mass2 = other_object.mass
        speed1_new = (mass2 / mass1) * speed2
        speed2_new = (mass1 / mass2) * speed1
        self.move_vector.set_speed(speed1_new)
        other_object.move_vector.set_speed(speed2_new)

    def distance_squared(self, other_object):
        """ Laskee etäisyyden neliön toiseen GameObjectiin. Näin vältetään neliöjuuren laskeminen joka on kallista. """
        return (self.x - other_object.x)**2 + (self.y - other_object.y)**2

    def distance(self, other_object):
        """ Laskee etäisyyden toiseen GameObjectiin. Käyttää neliöjuurta eli oletettavasti hitaampi kuin yllä. """
        return math.hypot(self.x - other_object.x, self.y - other_object.y)

    def force_play_sound(self, sound, duration=0):
        # Soitetaan ääni, pakotetaan sille kanava auki
        # if sound.get_num_channels() == 0:
        # print("Playing sound", sound)
        if sound is not None:
            pygame.mixer.find_channel(True).play(sound, duration)
        # else:
        #     print("Not playing sound", sound)


class DummyObject(GameObject):
    """ 
    Luo kopion alkuperäisestä GameObjectista soveltuvin osin seinän collision detektiota varten 
    Ei taida olla enää käytössä
    """
    def __init__(self, original):
        self.x = original.x
        self.y = original.y
        self.move_vector = original.move_vector
        self.gravity_affects = original.gravity_affects
        self.parent = original.parent
        self.level = original.level
        self.max_speed = original.max_speed
        self.is_centered_on_screen = original.is_centered_on_screen
        self.viewscreen_rect = original.viewscreen_rect
        self.rect = original.rect


def get_angle_difference(angle1, angle2, degrees=0):
    """ Palauttaa kahden kulman välisen eron radiaaneissa. Väli -PI...0...PI """
    angle_difference = angle1 - angle2
    if degrees:
        if angle_difference > 180: angle_difference -= 360
    else:
        if angle_difference > math.pi: angle_difference -= 2 * math.pi
    return angle_difference


def get_angle_in_radians(point1, point2):
    """ Palauttaa kahden pisteen välisen kulman radiaaneina """
    x_difference = point1[0] - point2[0]
    y_difference = point1[1] - point2[1]
    return math.atan2(y_difference, x_difference)


