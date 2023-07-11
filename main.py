import math
from machine import Pin, I2C, PWM
from ssd1306 import SSD1306_I2C
from utime import sleep_ms
import random

WIDTH = 128
HEIGHT = 64
PLAYER_WIDTH = 3
PLAYER_HEIGHT = 13
PLAYER_SPEED = 1
BALL_RADIO = 3
BALL_SPEED = 2
BALL_VERTICAL_INCLINATION = 0
UP, DOWN, LEFT, RIGHT = "UP", "DOWN", "LEFT", "RIGHT"
DEFAULT_FREQ = 500

AT_MENU = True
IS_PAUSED = False

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
down_button = Pin(27, Pin.IN, Pin.PULL_UP)
up_button = Pin(28, Pin.IN, Pin.PULL_UP)

display = SSD1306_I2C(WIDTH, HEIGHT, i2c)

buzzer = PWM(Pin(26))
buzzer.freq(DEFAULT_FREQ)
beeping = 0

class Entity:
    def __init__(self, x: int, y: int, h: int, w: int):
        self.x = x
        self.y = y
        self.h = h
        self.w = w

    def draw(self):
        display.fill_rect(self.x, self.y, self.w, self.h, 1)


class Player(Entity):
    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y, PLAYER_HEIGHT, PLAYER_WIDTH)

    def move_down(self):
        if self.y + self.h < HEIGHT:
            self.y += PLAYER_SPEED

    def move_up(self):
        if self.y > 0:
            self.y -= PLAYER_SPEED


class Ball(Entity):
    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y, BALL_RADIO, BALL_RADIO)
        self.horizontal_direction = RIGHT

    def center_back(self):
        self.x = math.floor(WIDTH / 2 - BALL_RADIO / 2)
        self.y = math.floor(HEIGHT / 2 - BALL_RADIO / 2)

    def check_collition(self, entity: Entity) -> bool:
        if (
                self.x < entity.x + entity.w and
                self.x + self.w > entity.x and
                self.y < entity.y + entity.h and
                self.h + self.y > entity.y
        ):
            return True
        return False

    def move(self):
        self.y += BALL_VERTICAL_INCLINATION

        if self.horizontal_direction == RIGHT:
            self.x += BALL_SPEED
        else:
            self.x -= BALL_SPEED


player = Player(0, 0)
player_score = 0

bot = Player(WIDTH - 5, 0)
bot_score = 0

ball = Ball()
ball.center_back()


def blinking():
    global IS_PAUSED
    global display

    IS_PAUSED = True
    buzzer.freq(1000)
    buzzer.duty_u16(1000)
    display.invert(1)
    sleep_ms(100)
    display.invert(0)
    buzzer.freq(1500)
    sleep_ms(100)
    display.invert(1)
    sleep_ms(100)
    display.invert(0)
    buzzer.freq(1000)
    sleep_ms(100)
    buzzer.duty_u16(0)
    buzzer.freq(DEFAULT_FREQ)
    IS_PAUSED = False


while True:
    if beeping > 0:
        buzzer.duty_u16(1000)
        beeping -= 1
    else:
        buzzer.duty_u16(0)

    display.fill(0)

    if AT_MENU:
        display.text("Pong!", math.floor(WIDTH / 2) - 15, math.floor(HEIGHT / 2) - 10)
        display.text("Press to start", math.floor(WIDTH / 2) - 55, math.floor(HEIGHT / 2) + 10)
        display.invert(1)

        if down_button.value() == 0 or up_button.value() == 0:
            AT_MENU = False
            display.invert(0)
    else:

        display.line(math.floor(WIDTH / 2) + 2, 0, math.floor(WIDTH / 2) + 2, HEIGHT, 1)

        # Ball collisions with margins
        if ball.x + BALL_RADIO >= WIDTH:
            blinking()
            BALL_VERTICAL_INCLINATION = random.randint(-4, 0)
            player_score += 1
            ball.horizontal_direction = LEFT
        elif ball.x <= 0:
            blinking()
            BALL_VERTICAL_INCLINATION = random.randint(-4, 0)
            bot_score += 1
            ball.horizontal_direction = RIGHT
        if ball.y + BALL_RADIO >= HEIGHT:
            ball.y = HEIGHT - BALL_RADIO
            BALL_VERTICAL_INCLINATION *= -1
        elif ball.y <= 0:
            ball.y = 1
            BALL_VERTICAL_INCLINATION *= -1

        # Ball collisions with entities
        if ball.check_collition(player):
            BALL_VERTICAL_INCLINATION = random.randint(-4, 0)
            ball.horizontal_direction = RIGHT
            beeping = 5

        if ball.check_collition(bot):
            BALL_VERTICAL_INCLINATION = random.randint(-4, 0)
            ball.horizontal_direction = LEFT
            beeping = 5

        if not IS_PAUSED:
            ball.move()

            if ball.y > bot.y + PLAYER_HEIGHT / 2:
                bot.move_down()
            else:
                bot.move_up()

            if down_button.value() == 0:
                player.move_up()

            if up_button.value() == 0:
                player.move_down()

        player.draw()
        bot.draw()
        ball.draw()

        display.text(str(player_score), math.floor(WIDTH / 2) - 20, 5)
        display.text(str(bot_score), math.floor(WIDTH / 2) + 20, 5)

    display.show()
