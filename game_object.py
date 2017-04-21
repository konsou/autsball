import pygame, vector

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)


class GameObject(pygame.sprite.Sprite):
    """ Classi joka perii pygamen Spriten ja lisää yleisiä peliobjektin käyttäytymiseen liittyviä juttuja """
    def __init__(self, level=None, parent=None, group=None, image_file=None, image=None, start_position=None,
                 gravity_affects=1, is_ball=0):
        # Spriten init
        pygame.sprite.Sprite.__init__(self, group)
        # parent on itse peliobjekti
        self.parent = parent
        # level-objekti
        self.level = level
        if image is not None:
            self.image = image
            self.rect = self.image.get_rect()
        elif image_file is not None:
            self.image = pygame.image.load(image_file).convert_alpha()
            self.rect = self.image.get_rect()
        self.original_image = image

        if start_position is None:
            if level is not None:
                self.start_position = self.level.center_point
            else:
                self.start_position = 0, 0
        else:
            self.start_position = start_position
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.start_position
        self.mass = 1
        self.move_vector = vector.MoveVector()

        self.gravity_affects = gravity_affects
        self.is_ball = is_ball

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
        self.rect.center = (self.x - self.viewscreen_rect[0],
                            self.y - self.viewscreen_rect[1])

    def update_movement(self):
        """
        Päivittää spriten koordinaatit move_vectorin ja gravityn pohjalta 
        """
        # Gravityn vaikutus
        self.move_vector.set_vy(self.move_vector.get_vy() + self.parent.Constants.gravity)

        # Max speed rajoittaa
        self.move_vector.set_magnitude(min(self.move_vector.get_magnitude(), self.max_speed))

        # Muutetaan koordinaatteja liikemäärän mukaan
        self.x_previous = int(self.x)
        self.y_previous = int(self.y)
        self.x = int(self.move_vector.get_vx() + self.x)
        self.y = int(self.move_vector.get_vy() + self.y)
        self.update_rect()

    def rot_self_image_keep_size(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self.rect
        rot_image = pygame.transform.rotate(self.original_image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        self.image = rot_image

    def check_out_of_bounds(self):
        """ Pitää objektin pelialueen sisällä """
        self.x = max(0, self.x)
        self.x = min(self.level.size_x - 1, self.x)
        self.y = max(0, self.y)
        self.y = min(self.level.size_y - 1, self.y)

    def check_collision_with_wall_and_goal(self):
        """ Tarkastaa törkmäyksen seiniin  ja mahdollisesti maaliin - eli juttuihin level-taustassa """
        # Katotaan mikä väri on levelissä tässä pisteessä - skipataan alfa
        try:
            current_point = self.level.image.get_at((self.x, self.y))[:3]
        except IndexError as e:
            print("IndexError wall-collision-metodissa:", e)
            print("x ja y:", self.x, self.y)

        # Jos väri on muuta kuin musta/vihreä/punainen niin on törmäys
        if current_point != black and current_point != green and current_point != red:
            self.move_vector.set_magnitude(0)

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



