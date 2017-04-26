import pygame, vector, math

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)


class GameObject(pygame.sprite.Sprite):
    """ Classi joka perii pygamen Spriten ja lisää yleisiä peliobjektin käyttäytymiseen liittyviä juttuja """
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
        self.mass = 1.0
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
        self.move_vector.set_speed(0)
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
        """ Pitää objektin pelialueen sisällä, palauttaa 1 jos on ulkopuolella """
        return_value = 0

        x_before = self.x
        y_before = self.y

        self.x = max(0, self.x)
        self.x = min(self.level.size_x - 1, self.x)
        self.y = max(0, self.y)
        self.y = min(self.level.size_y - 1, self.y)

        # Jos koordinaatteja muutettiin (eli oli out of bounds) niin muutetaan liikemäärää
        if self.x != x_before:
            self.move_vector.set_vx(0)
            return_value = 1
        elif self.y != y_before:
            self.move_vector.set_vy(0)
            return_value = 1

        return return_value

    def check_collision_with_wall_and_goal(self):
        """ Tarkastaa törkmäyksen seiniin  ja mahdollisesti maaliin - eli juttuihin level-taustassa """
        # Katotaan mikä väri on levelissä tässä pisteessä - skipataan alfa
        current_point = self.level.image.get_at((self.x, self.y))[:3]

        # Jos väri on muuta kuin musta/vihreä/punainen niin on törmäys ja vauhti menee nollaan
        if current_point not in (black, red, green):
            if self.is_bullet:
                # Tuhoaa seinää törmätessä jos on bullet
                pygame.draw.circle(self.level.image, black, (self.x, self.y), self.size - 1)
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
            # self.move_vector.add_vector(collide_list[0].move_vector)
            # dotproduct = self.move_vector.get_dot_product(collide_list[0].move_vector)
            self.collide_circle(collide_list[0])

    def collide_circle(self, other_sprite):
        """ 
        Törmäyttää kaksi ympyrän muotoista GameObjectia ja laskee niiden suunnat ja liikemäärät uusiksi.
        Jopa ottaa massat huomioon! 
        """
        angle_to_other = get_angle_in_radians(other_sprite.rect.center, self.rect.center)
        self.move_vector.set_direction(angle_to_other - math.pi)
        other_sprite.move_vector.set_direction(angle_to_other)

        speed1 = self.move_vector.get_speed()
        speed2 = other_sprite.move_vector.get_speed()
        mass1 = self.mass
        mass2 = other_sprite.mass
        speed1_new = (mass2 / mass1) * speed2
        speed2_new = (mass1 / mass2) * speed1
        self.move_vector.set_speed(speed1_new)
        other_sprite.move_vector.set_speed(speed2_new)


def get_angle_difference(angle1, angle2):
    """ Palauttaa kahden kulman välisen eron radiaaneissa. Väli -PI...0...PI """
    angle_difference = angle1 - angle2
    if angle_difference > math.pi: angle_difference -= 2 * math.pi
    return angle_difference

def get_angle_in_radians(point1, point2):
    x_difference = point1[0] - point2[0]
    y_difference = point1[1] - point2[1]
    return math.atan2(y_difference, x_difference)
