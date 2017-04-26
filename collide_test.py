import pygame, math, time, vector, game_object

YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

pygame.init()
win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Physics test")

def pause_and_wait_for_any_key():
    paused = True
    while paused:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                paused = False
            elif e.type == pygame.QUIT:
                paused = False
                global running
                running = False

        time.sleep(0.01) #estää 100% cpu usen

    return None


def show_text(pos, text, color=(255, 255, 255), bgcolor=(0, 0, 0), fontSize=24):
    """ Utility-metodi tekstin näyttämiseen ruudulla """
    global win
    font = pygame.font.Font(None, fontSize)
    textimg = font.render(text, 1, color, bgcolor)
    win.blit(textimg, pos)


def get_angle_in_radians(point1, point2):
    x_difference = point1[0] - point2[0]
    y_difference = point1[1] - point2[1]
    return math.atan2(y_difference, x_difference)


def mouse_clicked(button=None, pos=None):
    if button == 1:
        CollidingBall(pos, direction=math.pi, speed=2)


SpawnedBallGroup = pygame.sprite.Group()
CenterBallGroup = pygame.sprite.Group()


class CollidingBall(game_object.GameObject):
    def __init__(self, pos=None, direction=None, speed=None, group=SpawnedBallGroup):
        game_object.GameObject.__init__(self, group=group, image_file='gfx/ball_50_red.png')
        self.x, self.y = pos
        self.radius = 25
        self.rect.center = pos
        self.move_vector = vector.MoveVector()
        if direction is not None:
            self.move_vector.set_direction(direction)
        if speed is not None:
            self.move_vector.set_speed(speed)
        self.gravity_affects = 0
        self.viewscreen_rect = (0,0,800,600)

    def update(self):
        self.update_movement()
        if self.check_out_of_bounds():
            self.kill()
        else:
            self.check_collision()

    def check_collision(self):
        if self in SpawnedBallGroup:
            collide_list = pygame.sprite.spritecollide(self, CenterBallGroup, dokill=False,
                                                       collided=pygame.sprite.collide_circle)
            if len(collide_list) > 0:
                print("COLLISION")
                print(self.move_vector.get_all())
                print(self.move_vector.normalize().get_all())
                angle_to_center = get_angle_in_radians(collide_list[0].rect.center, self.rect.center)
                angle_difference1 = self.move_vector.get_direction() - angle_to_center
                angle_difference2 = angle_difference1 - 2 * math.pi
                angle_difference = min(angle_difference1, angle_difference2)

                print("Angle:", angle_to_center)
                print("Direction:", self.move_vector.get_direction())
                print("Angle difference:", angle_difference)


                pause_and_wait_for_any_key()
                self.kill()

    def check_out_of_bounds(self):
        """ Pitää objektin pelialueen sisällä, palauttaa 1 jos on ulkopuolella """
        return_value = 0

        x_before = self.x
        y_before = self.y

        self.x = max(0, self.x)
        self.x = min(800 - 1, self.x)
        self.y = max(0, self.y)
        self.y = min(600 - 1, self.y)

        # Jos koordinaatteja muutettiin (eli oli out of bounds) niin muutetaan liikemäärää
        if self.x != x_before or self.y != y_before:
            return_value = 1

        return return_value

center_point = (400,300)

center_ball = CollidingBall(pos=center_point, group=CenterBallGroup)

ball2_direction = 180

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_clicked(button=event.button, pos=event.pos)

    SpawnedBallGroup.update()
    CenterBallGroup.update()

    win.fill(BLACK)

    CenterBallGroup.draw(win)
    SpawnedBallGroup.draw(win)



    pygame.display.flip()
    time.sleep(0.01)

pygame.quit()