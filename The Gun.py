import math
import time
from random import choice
from random import randint
import sys
import pygame


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
Ball_Colors = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600

tank = pygame.image.load('tank.png')
tank.set_colorkey(WHITE)


class Ball:
    def __init__(self, screen: pygame.Surface, x = WIDTH * 0.5, y = 450):
        """ The ball class constructor
        Args:
        x, y - initial coords
        vx, vy - the x- and y-axis speeds (default zero)
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(Ball_Colors)
        self.live = 30
        self.time = 0
        self.hit = 0
        self.is_moving = True

    def move(self, dt = 1):
        """Function moves the ball per time unit (updates position and velocities considering gravity) """
        if self.y <= 550:
            self.vy -= 1.2 * dt
            self.y -= self.vy * dt
            self.x += self.vx * dt
            self.vx *= 0.99
        else:
            if self.vx ** 2 + self.vy ** 2 > 10:
                self.vy = -self.vy / 2
                self.vx = self.vx / 2
                self.y = 549
            else:
                self.is_moving = False

        if self.x > 780:
            self.vx = -self.vx / 2
            self.x = 778

    def draw(self):
        """Draws the ball with """
        if self.is_moving == False:
            self.hit += 1
        if self.hit >= 30:
            self.color = WHITE
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def check_hit(self, obj):
        """Function checks the hit with object obj.
        Args:
            obj: object.
        Returns:
            True in case of hitting and False else.
        """

        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 <= (self.r + obj.r + 30) ** 2:
            return True
        return False


class Gun:
    def __init__(self, screen):
        self.screen = screen #the screen initialization
        self.x = WIDTH/2
        self.y = 450
        self.an = 1 #initial angle value
        self.f2_power = 30 #the shot power
        self.f2_on = 0 #aiming mode
        self.color = GREEN #the gun color before aiming
        self.speed = 2

    def fire2_start(self, event):
        """The gun "gets ready" for shot"""
        self.f2_on = 1

    def fire2_end(self, event_):
        """Function for shootting: the gun shoots after releasing the mouse
        Initial values depends on the mouse position.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, self.x, self.y)
        new_ball.r += 5
        self.an = math.atan2((event_.pos[1]-self.y), (event_.pos[0]-self.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 30

    def targeting(self, event_target):
        """Function for targeting"""
        if event_target:
            if event_target.pos[0]-self.x != 0:
                self.an = math.atan((event_target.pos[1]-self.y) / (event_target.pos[0]-self.x))
            else:
                self.an = math.atan((event_target.pos[1] - self.y) / 0.0001)
        if self.f2_on:
            self.color = RED
        else:
            self.color = YELLOW

    def draw(self):
        gun_w = 10
        gun_l = self.f2_power
        x0, y0 = pygame.mouse.get_pos()

        sin_an = math.sin(self.an)
        cos_an = math.cos(self.an)
        if self.x > x0:
            sin_an = -sin_an
            cos_an = -cos_an

        coords = [(self.x + gun_w * 0.5 * sin_an, self.y - gun_w * 0.5 * cos_an),
                  (self.x + gun_w * 0.5 * sin_an + gun_l * cos_an, self.y - gun_w * 0.5 * cos_an + gun_l * sin_an),
                  (self.x - gun_w * 0.5 * sin_an + gun_l * cos_an, self.y + gun_w * 0.5 * cos_an + gun_l * sin_an),
                  (self.x - gun_w * 0.5 * sin_an, self.y + gun_w * 0.5 * cos_an)]

        pygame.draw.polygon(screen, self.color, coords)
        pygame.draw.rect(screen, BLUE, (self.x - 40, self.y + 5, 80, 20))
        pygame.draw.polygon(screen, BLACK, [(self.x - 10, self.y + 5), (self.x + 10, self.y + 5),
                                            (self.x + 10, self.y + 20), (self.x - 10, self.y + 20)], 15)
        #screen.blit(tank, tank.get_rect(center=(self.x, self.y + 10)))
        #pygame.display.update()

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = YELLOW

    def gun_move(self, event):
        if (pygame.key.get_pressed()[pygame.K_d]) and (self.x <= WIDTH -30):
            self.x += 10
        elif (pygame.key.get_pressed()[pygame.K_a]) and (self.x >= 30):
            self.x -= 10


class Target:

    def __init__(self, a = 0):
        self.points = 0
        self.cnt = 0
        self.exist = 1
        self.make_new_target(a)

    def make_new_target(self, v, clr = RED):
        """ New target initialization"""
        self.x = randint(20, 780)
        self.y = randint(50, 200)
        self.r = randint(7, 20)
        self.v = v
        self.exist = 1
        self.color = clr

    def move(self):
        """Moving and reflecting object"""
        if (self.x > 750 and self.v > 0) or (self.x < 50 and self.v < 0):
            print(self.x - self.v, self.v)
            self.v = -self.v
        self.x += self.v

    def drop(self):
        """Drops the bombs"""
        global bombs
        b_o_m_b = Bomb(self.x, self.y)
        bombs.append(b_o_m_b)

    def hit(self, points=1):
        """Adds points after hitting the target"""
        self.points += points

    def draw(self):
        """Draws a ball"""
        self.cnt += 1
        pygame.draw.ellipse(screen, self.color, (self.x - 40, self.y + 20, 80, 40))

class Bomb:
    def __init__(self, x_targ, y_targ):
        self.exist = 1
        self.color = GREY
        self.x = x_targ
        self.y = y_targ
        self.r = 7

    def move(self):
        self.y += 1

    def hit(self, obj):
        if (self.x - obj.x) ** 2 + (self.y - obj.y) ** 2 <= (self.r + obj.r + 30) ** 2:
            return True
        return False

    def destroy(self):
        self.color = BLACK
        self.y += 500

    def draw(self):
        pygame.draw.ellipse(screen, self.color, (self.x - 10, self.y + 20, 20, 40))

    def BOOM(self, obj):
        if (obj.x - self.x) ** 2 + (obj.y - self.y) ** 2 <= 400:
            return True
        return False


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []
bombs = []

clock = pygame.time.Clock()
gun = Gun(screen)
target = Target()
additional_target = Target()
finished = False
a = 0
flag = 0


while not finished:
    if flag == 1:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        bullet = 0
        balls = []
        bombs = []

        clock = pygame.time.Clock()
        gun = Gun(screen)
        target = Target()
        additional_target = Target()
        finished = False
        a = 0
        flag = 0
    screen.fill(WHITE)
    gun.draw()
    target.draw()
    additional_target.draw()
    for bmb in bombs:
        bmb.draw()
    for b_o_m_b in balls:
        b_o_m_b.draw()
    pygame.display.update()

    clock.tick(FPS)
    if (pygame.key.get_pressed()[pygame.K_d]) or (pygame.key.get_pressed()[pygame.K_a]):
        gun.gun_move(event)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targeting(event)

    for b_o_m_b in balls:
        for bmb in bombs:
            bmb.move()
            if b_o_m_b.check_hit(bmb):
                bmb.exist = 0
                bmb.destroy()
            if bmb.BOOM(gun):
                flag = 1
        b_o_m_b.move()
        if b_o_m_b.check_hit(target) and target.exist:
            target.exist = 0
            target.hit()
            target.make_new_target(0)
        if b_o_m_b.check_hit(additional_target) and additional_target.exist:
            additional_target.exist = 0
            additional_target.hit()
            additional_target.make_new_target(randint(7, 13), GREY)

    additional_target.move()

    if randint(0, 100) > 98:
        additional_target.drop()
    gun.power_up()

pygame.quit()