# -*- coding: utf-8 -*-
import pygame
import vector
import math
import copy
import types
import sound
import assets
from colors import *
# from assets import assets, assets_rot, assets_mask, assets_rot_mask


class GameObject(pygame.sprite.Sprite):
    """ 
    Classi joka perii pygamen Spriten ja lisää yleisiä peliobjektin käyttäytymiseen liittyviä juttuja.
    
    __init__:issä ottaa seuraavia argumentteja:
        level: level-objekti
        parent: itse peliobjekti
        group: sprite-ryhmä, johon tämä objekti lisätään
        image_file: objektin kuvan tiedostonimi TAI lista tiedostonimistä (animointia varten)
        image: objektin kuva (kuvaobjekti)
        start_position: objektin aloituspositio
        frames_per_image: jos kuva halutaan animoida niin tässä voi määritellä animointinopeuden
    """
    def __init__(self, level=None, parent=None, group=None, image_file=None, start_position=None,
                 frames_per_image=5):
        # Pygame-Spriten init, lisäys ryhmään
        pygame.sprite.Sprite.__init__(self, group)
        
        # Kuvan lataus - tämä laskee myös rectin, sizen ja radiuksen
        # Hoitaa myös animointikuvien latauksen
        self.load_image(image_file=image_file, frames_per_image=frames_per_image)

        # parent on itse peliobjekti
        self.parent = parent

        # level-objekti
        self.level = level

        # SFX placeholderit - overrideaa perivissä classeissa jos haluat ääntä
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

        # Attachit - käytetään pallon liittämiseen pelaajaan
        self.attached_player = None
        self.attached_ball = None

        # Tämä päivitetään myöhemmin, initoidaan kuitenkin ettei PyCharm herjaa
        self.viewscreen_rect = None

    def __repr__(self):
        return "<GAME OBJECT>"

    def load_image(self, image_file=None, frames_per_image=5):
        """ 
        Lataa kuvan/kuvat spritelle. Asettaa rect, radius, size.
        Onko size tarpeeton ja redundantti?
        HUOM! Assettien esilatauksen myötä ei tue enää kuvaobjektien syöttämistä suoraan vaan AINA pitää olla
        tiedostonimi!
        """
        # Ensin katsotaan onko image_file muuta kuin yksittäinen stringi.
        # Jos on muuta niin oletetaan sen olevan lista/tuple/dict joka sitältää tiedostonimiä
        # ja ladataan sieltä kuvat animaatiota varten.
        if image_file is not None and type(image_file) not in types.StringTypes:
            self._animation_images = []
            self._animation_image_filenames = []
            for current_image in image_file:
                self._animation_images.append(assets.assets[current_image])
                self._animation_image_filenames.append(current_image)
            self.image = self._animation_images[0]
            self.image_filename = self._animation_image_filenames[0]

            self.animation_frames_per_image = frames_per_image
            self._animation_frame_counter = 0
            self._animation_current_image_counter = 0
            self._animation_enabled = 1
        # Jos animaatio ei enabloitu niin jatketaan normaalisti
        else:
            # Jos on annettu kuvatiedosto niin luetaan se
            self.image = assets.assets[image_file]
            self.image_filename = image_file
            self._animation_enabled = 0

        # bitmask collision detectionia varten
        self.mask = assets.assets_mask[self.image_filename]

        # Tämä tarvitaan rotaatioita varten
        self.original_image = self.image
        # Size on tämmöinen yhden luvun approksimaatio objektin koosta - neliöllä sivun pituus, ympyrällä halkaisija
        # Suorakulmiolla sivujen pituuksien keskiarvo
        # Tarpeeton? Taidetaan käyttää vain bulletin maastoon tekemän reiän koon laskennassa, radius kelpaisi yhtä hyvin
        self.size = (self.image.get_width() + self.image.get_height()) // 2
        # Radiusta tarvii collision detectionissa
        self.rect = self.image.get_rect()
        self.radius = (self.size + 1) // 2
        # original_radius oli käytössä vähän aikaa kun pallo liitettiin pelaajaan suoraan mutta ei enää ole
        # self.original_radius = self.radius

    def reset(self):
        """ 
        -resetoi position (eli muuttaa start_position:iksi)
        -asettaa nopeuden nollaan
        -päivittää rectin
        -poistaa palloliitoksen
        
        Tätä kutsutaan esim. pelaajan recoveryssä ja pallolle kun tulee maali.
        """
        self.x, self.y = self.start_position
        self.move_vector.set_speed(0)
        self.update_rect()
        if self.attached_player is not None:
            self.attached_player.detach()
            self.detach()
        if self.attached_ball is not None:
            self.attached_ball.detach()
            self.detach()

    def update_rect(self, viewscreen_rect=None):
        """ 
        Päivittää objektin rectin ottamaan huomioon viewscreenin 
        Tämä metodi on tärkeää muistaa kutsua kun liikuttelee objektia! Muuten sekoaa. 
        """
        if not self.is_centered_on_screen:
            if self.viewscreen_rect is None:
                self.viewscreen_rect = viewscreen_rect

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

    def animate(self):
        """ 
        Tätä kun kutsuu update():ssa niin animoi objektin kuvan
        
        Tarkastaa onko aika päivittää animaatioon seuraava image ja tekee sen tarvittaessa
        """
        if self._animation_enabled:
            self._animation_frame_counter += 1
            if self._animation_frame_counter % self.animation_frames_per_image == 0:
                self.animate_next_frame()

    def animate_next_frame(self):
        """ Muuttaa image:ksi ja original_image:ksi seuraavan kuvan animaatiossa """
        # TODO: tämän olisi hyvä vaikuttaa myös maskiin siltä varalta jos eri frameissa on eri koko
        self._animation_current_image_counter += 1
        try:
            self.image = self._animation_images[self._animation_current_image_counter]
        except IndexError:
            # Jos on menty animaatiokuvissa yli kuvamäärän niin mennään takaisin kuvaan nro 0
            self.image = self._animation_images[0]
            self._animation_current_image_counter = 0
        self.original_image = self.image
        self.rect.size = self.image.get_rect().size  # pidä positio samana, muuten siirtyy hetkeksi yläkulmaan

    def rot_self_image_keep_size(self, angle):
        """ Muuttaa kuvaksi oikean esiladatun ja -rotatoidun kuvan """
        angle = int(angle)  # tällä sallitaan floatit handlingiin
        self.image = assets.assets_rot[self.image_filename][angle]
        self.mask = assets.assets_rot_mask[self.image_filename][angle]

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

    def check_collision_with_wall_and_goal(self, speculate=0):
        """ 
        Tarkastaa törmäyksen seiniin  ja mahdollisesti maaliin - eli juttuihin level-taustassa 
        Palauttaa 1 jös tärmäsi seinään, muuten 0
        Jos speculate on 1 niin laskee seinätörmäyksen ikään kuin oltaisiin jo seuraavassa framessa
        """
        wall_collision = 0

        if speculate:
            # Nykyiset arvot talteen
            orig_x, orig_y = self.x, self.y
            orig_x_previous, orig_y_previous = self.x_previous, self.y_previous
            orig_move_vector = copy.copy(self.move_vector)

            # Päivitetään liikettä ikään kuin oltaisiin jo seuraavassa framessa
            self.update_movement()
            self.check_out_of_bounds()

        # Katotaan mikä väri on levelissä tässä pisteessä - skipataan alfa
        current_point = self.level.image.get_at((self.x, self.y))[:3]

        # Jos väri on muuta kuin musta/vihreä/punainen niin on törmäys ja kutsutaan tärmäysmetodia
        if current_point not in (BLACK, RED, GREEN):
            if not speculate:
                self.collided_with_wall()
            wall_collision = 1
        elif current_point in (RED, GREEN):
            if not speculate:
                self.is_in_goal(current_point)

        if speculate:
            # Palautetaan alkuperäiset arvot
            self.x, self.y = orig_x, orig_y
            self.x_previous, self.y_previous = orig_x_previous, orig_y_previous
            self.move_vector = orig_move_vector

        return wall_collision

    def check_collision_with_group(self, group, collided=pygame.sprite.collide_mask):
        """ Tarkastaa törmääkö objekti ryhmässä oleviin toisiin objekteihin. """
        collide_list = pygame.sprite.spritecollide(self, group, dokill=False, collided=collided)
        for colliding_object in collide_list:
            # Emme halua törmätä itseemme
            # Skippaamme myös jo käsitellyt kollisiot
            if colliding_object != self: #  and (self, colliding_object) not in self.parent.checked_collisions:
                # Kutsutaan objektin collided_with-metodia, se hoitaa törmäyskäyttäytymisen
                self.collided_with(colliding_object)
                # Lisätään käsitelty törmäys settiin ettei sitä toisteta tässä framessa enää
                # self.parent.checked_collisions.add((self, colliding_object))
                # colliding_object.collided_with(self)

    def collided_with(self, other_object):
        """ Tämä on tarkoitus overwritettaa jos haluaa kustomia törmäyskäyttäytymistä """
        # Lasketaan törmäyksen liikemäärät
        self.apply_collision_to_move_vector(other_object)

    def collided_with_wall(self):
        """ Tämä on tarkoitus overwritettaa jos haluaa kustomia törmäyskäyttäytymistä """
        # Soitetaan seinääntörmäysääni jos nopeus yli 3 ja on liikkunut viime kerrasta
        if self.move_vector.get_speed() > 3 and self.x != self.x_previous and self.y != self.y_previous:
            sound.force_play_sound(self.wall_collide_sound)

        # Vauhti loppuu kuin seinään
        self.move_vector.set_speed(0)
        # Estetään seinän sisään menemistä tällä - eli jos olisi seinän sisällä niin vaihdetaan
        # koordinaateiksi edelliset lukemat (jolloin oletettavasti ei ollut seinän sisällä)
        self.x = self.x_previous
        self.y = self.y_previous

    def is_in_goal(self, point_color):
        """ Tämä on tarkoitus overwritettaa jos haluaa kustomia törmäyskäyttäytymistä """
        pass

    def apply_collision_to_move_vector(self, other_object):
        """ 
        Törmäyttää itsensä toiseen GameObjectiin.
        Oletetaan molemmat ympyrän muotoisiksi.
        --> Laskee VAIN SELF:IN suunnat ja liikemäärät uusiksi. <--
        Jopa ottaa massat huomioon!
        Vähän luulen että tässä on vielä viilaamisen varaa, ei tunnu aivan oikealta kaikissa tilanteissa...
        """
        angle_to_other = get_angle_in_radians(other_object.rect.center, self.rect.center)
        self.move_vector.set_direction(angle_to_other - math.pi)
        # other_object.move_vector.set_direction(angle_to_other)

        speed1 = self.move_vector.get_speed()
        # speed2 = other_object.move_vector.get_speed()
        mass1 = self.mass
        mass2 = other_object.mass
        # speed1_new = (mass2 / mass1) * speed2
        speed2_new = (mass1 / mass2) * speed1
        self.move_vector.set_speed(speed2_new)
        # Yritetään estää toisen sisään menemistä
        self.x, self.y = self.x_previous, self.y_previous
        # other_object.move_vector.set_speed(speed2_new)

    def distance_squared(self, other_object):
        """ Laskee etäisyyden neliön toiseen GameObjectiin. Näin vältetään neliöjuuren laskeminen joka on kallista. """
        return (self.x - other_object.x)**2 + (self.y - other_object.y)**2

    def distance(self, other_object):
        """ Laskee etäisyyden toiseen GameObjectiin. Käyttää neliöjuurta eli oletettavasti hitaampi kuin yllä. """
        return math.hypot(self.x - other_object.x, self.y - other_object.y)


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


def rad2deg_custom(rad):
    """ Muuttaa annetun kulman asteiksi, ottaen huomioon omituisuudet. Palauttaa INT-arvon välilä 0...359. """
    degrees = 270 - math.degrees(rad)
    while degrees < 0:
        degrees += 360
    while degrees > 359:
        degrees -= 360
    return int(degrees)

