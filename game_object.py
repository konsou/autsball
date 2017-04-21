import pygame, vector

class GameObject(pygame.sprite.Sprite):
    """ Classi joka perii pygamen Spriten ja lisää yleisiä peliobjektin käyttäytymiseen liittyviä juttuja """
    def __init__(self, level=None, parent=None, group=None, image_file=None, start_position=None):
        # Spriten init
        pygame.sprite.Sprite.__init__(self, group)
        # parent on itse peliobjekti
        self.parent = parent
        # level-objekti
        self.level = level
        if image_file is not None:
            self.image = pygame.image.load(image_file).convert_alpha()
            self.rect = self.image.get_rect()
        if start_position is None:
            self.start_position = self.level.size_x // 2, self.level.size_y // 2
        else:
            self.start_position = start_position
        self.x, self.y = self.start_position
        self.mass = 1
        self.move_vector = vector.MoveVector()
        self.viewscreen_rect = None
