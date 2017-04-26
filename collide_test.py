import pygame, math, time, vector, game_object, random

YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

pygame.init()
win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Physics test")

def pause_and_wait_for_any_key():
    paused = True
    show_text((10,10), "PAUSED", fontSize=48)
    SpawnedBallGroup.draw(win)
    CenterBallGroup.draw(win)
    pygame.display.update()
    while paused:
        for e in pygame.event.get():
            if e.type == pygame.KEYUP or e.type == pygame.MOUSEBUTTONUP:
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

def get_angle_difference(angle1, angle2):
    """ Palauttaa kahden kulman välisen eron radiaaneissa. Väli -PI...0...PI """
    angle_difference = angle1 - angle2
    if angle_difference > math.pi: angle_difference -= 2 * math.pi
    return angle_difference


def get_angle_in_radians(point1, point2):
    x_difference = point1[0] - point2[0]
    y_difference = point1[1] - point2[1]
    return math.atan2(y_difference, x_difference)


def mouse_clicked(button=None, pos=None):
    if button == 1:
        CollidingBall(pos, direction=random.uniform(0, 2* math.pi), speed=5, mass=random.uniform(0.1, 5))


SpawnedBallGroup = pygame.sprite.Group()
# CenterBallGroup = pygame.sprite.GroupSingle()


class CollidingBall(game_object.GameObject):
    def __init__(self, pos=None, direction=None, speed=None, group=SpawnedBallGroup, mass=1):
        game_object.GameObject.__init__(self, group=group, image=pygame.Surface((10,10)))
        self.x, self.y = pos
        self.radius = int(mass * 30)
        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        pygame.draw.circle(self.image, RED, (self.radius, self.radius), self.radius)
        self.rect.center = pos
        self.move_vector = vector.MoveVector()
        if direction is not None:
            self.move_vector.set_direction(direction)
        if speed is not None:
            self.move_vector.set_speed(speed)
        self.gravity_affects = 0
        self.viewscreen_rect = (0,0,800,600)
        self.already_checked_collisions = []
        self.mass = mass


    def update(self):
        self.update_movement()
        self.check_out_of_bounds()
        # if self in SpawnedBallGroup:
            # self.x, self.y = pygame.mouse.get_pos()
            # self.update_rect()
            # pygame.draw.line(win, YELLOW, (self.x, self.y), (center_ball.x, center_ball.y))
            # pygame.draw.line(win, YELLOW, (self.x, self.y),
            #                  (self.x + 50 * self.move_vector.get_vx(), self.y + 50 * self.move_vector.get_vy()))
            # show_text((10,50), "Angle to center: " + str(math.degrees(get_angle_in_radians(center_ball.rect.center, self.rect.center))))
            # show_text((10,70), "Angle of move vector:" + str(math.degrees(self.move_vector.get_direction())))
            # angle_difference = get_angle_difference(self.move_vector.get_direction(), get_angle_in_radians(center_ball.rect.center, self.rect.center))

            # show_text((10,90), "Angle difference: " + str(math.degrees(angle_difference)))
            # show_text((600, 10), "move_vector info:")
            # show_text((600, 30), "vx: "+str(self.move_vector.get_vx()))
            # show_text((600, 50), "vy: "+str(self.move_vector.get_vy()))
            # show_text((600, 70), "speed: "+str(self.move_vector.get_speed()))
            # show_text((600, 90), "direction: "+str(self.move_vector.get_direction()))

        self.check_collision()

    def check_collision(self):
        collide_list = pygame.sprite.spritecollide(self, SpawnedBallGroup, dokill=False,
                                                   collided=pygame.sprite.collide_circle)

        if len(collide_list) > 0:
            for colliding_sprite in collide_list:
                if colliding_sprite != self:
                    # print(colliding_sprite)
                    self.collide_circle(collide_list[0])

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
        if self.x != x_before:
            return_value = 1
            self.move_vector.set_vx(self.move_vector.get_vx() * -1)
        if self.y != y_before:
            # print("top or bottom collision")
            return_value = 1
            self.move_vector.set_vy(self.move_vector.get_vy() * -1)

        return return_value

center_point = (400,300)

# center_ball = CollidingBall(pos=center_point, group=CenterBallGroup)

ball2_direction = 180

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_clicked(button=event.button, pos=event.pos)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                pause_and_wait_for_any_key()

    win.fill(BLACK)

    SpawnedBallGroup.update()
    #CenterBallGroup.update()


    #CenterBallGroup.draw(win)
    SpawnedBallGroup.draw(win)



    pygame.display.flip()
    time.sleep(0.01)

pygame.quit()