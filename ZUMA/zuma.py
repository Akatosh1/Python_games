import pygame
import sys
import random
import os
import math
import time
import random


width = 1050
height = 500
speed = 5
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Zuma')
clock = pygame.time.Clock()

game_folder = os.path.dirname(__file__)
image_folder = os.path.join(game_folder, 'images')
back_image = pygame.image.load(os.path.join(image_folder, 'Back.png'))
player_image = pygame.image.load(os.path.join(image_folder, 'Player.png'))
red_image = pygame.image.load(os.path.join(image_folder, 'Red.png'))
blue_image = pygame.image.load(os.path.join(image_folder, 'DarkBlue.png'))
gray_image = pygame.image.load(os.path.join(image_folder, 'Gray.png'))
violet_image = pygame.image.load(os.path.join(image_folder, 'Violet.png'))
yellow_image = pygame.image.load(os.path.join(image_folder, 'Yellow.png'))
skull_image = pygame.image.load(os.path.join(image_folder, 'Skull.png'))
bomb_image = pygame.image.load(os.path.join(image_folder, 'Bomb.png'))
balls_images = [red_image, blue_image, gray_image,
                violet_image, yellow_image]
current_bullet = random.choice(balls_images)

sounds_folder = os.path.join(game_folder, 'sounds')
shoot_sound = pygame.mixer.Sound(os.path.join(sounds_folder, 'shoot.wav'))
explode_sound = pygame.mixer.Sound(os.path.join(sounds_folder, 'expl.wav'))
game_over_sound = pygame.mixer.Sound(os.path.join(sounds_folder, 'end.wav'))
pygame.mixer.music.load(os.path.join(sounds_folder, 'nirvana.mp3'))
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play()


class Game():

    def __init__(self, player, all_sprites, ball_sprites, bullet_sprites,
                 skull_spites, balls, current_bullet_sprite, typ, level,
                 score, timing):
        self.bomb_timer = 0
        self.bullet_speed = 5
        self.score = score
        self.level = level
        self.type = typ
        self.player = player
        self.lives = 5
        self.bomb_time_left = -1
        self.time = timing
        self.time_left = timing
        self.all_sprites = all_sprites
        self.ball_sprites = ball_sprites
        self.bullet_sprites = bullet_sprites
        self.skull_spites = skull_spites
        self.balls = balls
        self.current_bullet_sprite = current_bullet_sprite
        self.copy_group = pygame.sprite.Group()
        self.begin_time = time.time()
        self.duplicate_delay = time.time()

    def get_events(self):
        global FPS
        global current_bullet
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.shooting = True
                if event.key == pygame.K_1:
                    if self.score >= 100:
                        FPS = 30
                        self.score -= 100
                if event.key == pygame.K_2:
                    FPS = 60
                if event.key == pygame.K_3:
                    if self.score >= 300:
                        for ball in self.balls:
                            ball.type = "reverse"
                        self.type = "reverse"
                        self.score -= 300
                if event.key == pygame.K_4:
                    for ball in self.balls:
                        ball.type = "common"
                    self.type = "common"
                if event.key == pygame.K_5:
                    if self.score >= 500:
                        self.bullet_speed = 10
                        self.score -= 500
                if event.key == pygame.K_6:
                    self.bullet_speed = 5
                if event.key == pygame.K_7:
                    if self.score >= 1000:
                        self.player.nextBullet("bomb")
                        self.score -= 1000
                if event.key == pygame.K_8:
                    self.player.nextBullet("normal")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.shooting = False
                    self.player.nextBullet("normal")

    def check_hits(self):
        skull_hits = pygame.sprite.groupcollide(self.skull_spites,
                                                self.ball_sprites,
                                                False, True,
                                                pygame.sprite.collide_circle)
        hits = pygame.sprite.groupcollide(self.bullet_sprites,
                                          self.ball_sprites,
                                          True, False,
                                          pygame.sprite.collide_circle)
        if skull_hits:
            if self.lives > 1:
                self.lives -= 1
            else:
                game.game_over()
        if hits:
            hit_balls = list(hits.values())
            bullet_ball = list(hits.keys())
            hit_ball = hit_balls[0][0]
            shift_angle, x, y = hit_ball.return_new_ball_pos()
            shift_number = hit_ball.number
            shift_image = bullet_ball[0].image
            if shift_image == bomb_image:
                self.bomb_timer = 3
                self.bomb_begin_time = time.time()
            for ball in list(self.ball_sprites):
                if ball.number >= shift_number:
                    ball.number += 1
                else:
                    ball.correct_sprites_trajectory()
            ball = Ball(shift_angle, self.type,
                        shift_number, shift_image, self.level, x, y)
            self.ball_sprites.add(ball)
            self.all_sprites.add(ball)
            self.balls.insert(len(self.balls) - shift_number + 1, ball)
            self.count_duplicates()

    def count_duplicates(self):
        duplicate_balls = 1
        if (time.time() - self.duplicate_delay) > 1:
            for i in range(len(self.balls)):
                if i == (len(self.balls) - 1):
                    if self.check_duplicates(i, duplicate_balls):
                        break
                    duplicate_balls = 1
                elif self.balls[i].image == self.balls[i+1].image:
                    duplicate_balls += 1
                else:
                    if self.check_duplicates(i, duplicate_balls):
                        break
                    duplicate_balls = 1
            self.duplicate_delay = time.time()

    def check_duplicates(self, i, duplicate_balls):
        if duplicate_balls > 2:
            self.score += duplicate_balls * 100
            for j in range(duplicate_balls, 0, -1):
                current_ball = i - duplicate_balls + 1
                super_number = self.balls[current_ball].number
                self.balls[current_ball].kill()
                self.balls.pop(current_ball)
            for j in self.balls:
                if j.number > len(self.balls) - i + duplicate_balls:
                    j.number -= duplicate_balls
            self.bring_balls_together()
            return True
        else:
            return False

    def bring_balls_together(self):
        for i in range(len(self.balls) - 1):
            x = (self.balls[i+1].rect.center[0] -
                 self.balls[i].rect.center[0])**2
            y = (self.balls[i+1].rect.center[1] -
                 self.balls[i].rect.center[1])**2
            sqrt = int(math.sqrt(x+y))
            while sqrt > 33:
                self.balls[i+1].reduce_distance()
                x = (self.balls[i+1].rect.center[0] -
                     self.balls[i].rect.center[0])**2
                y = (self.balls[i+1].rect.center[1] -
                     self.balls[i].rect.center[1])**2
                sqrt = math.sqrt(x+y)

    def bomb_explode(self):
        explode_sound.play()
        for ball in self.balls:
            if ball.image == bomb_image:
                number = ball.number + 2
                kill_number = len(self.balls) - number
                for i in range(5):
                    try:
                        self.balls[kill_number].kill()
                        self.balls.pop(kill_number)
                    except LookupError:
                        break
                counter = len(self.balls)
                for j in self.balls:
                    j.number = counter
                    counter -= 1

    def show_score_and_level(self):
        self.time_left = int(self.time + self.begin_time - time.time())
        font = pygame.font.SysFont('monaco', 30)
        bonus = font.render("Бонусы", True, RED)
        score = font.render('Счет: {}'.format(self.score), True, WHITE)
        level = font.render('Уровень: {}'.format(self.level), True, WHITE)
        lives = font.render('Жизни: {}'.format(self.lives), True, WHITE)
        timer = font.render('Время: {}'.format(self.time_left), True, WHITE)
        if self.bomb_timer > 0:
            self.bomb_time_left = int(self.bomb_timer +
                                      self.bomb_begin_time - time.time())
            bomb_timer = font.render('Взрыв: {}'.format(self.bomb_time_left),
                                     True, WHITE)
            screen.blit(bomb_timer, (50, 250))
        else:
            self.bomb_time_left = -1
        if self.score >= 1000:
            bomb_av = "Доступно"
        else:
            bomb_av = "Недоступно"
        if self.score >= 500:
            boost_av = "Доступно"
        else:
            boost_av = "Недоступно"
        if self.score >= 300:
            reverse_av = "Доступно"
        else:
            reverse_av = "Недоступно"
        if self.score >= 100:
            freeze_av = "Доступно"
        else:
            freeze_av = "Недоступно"
        font2 = pygame.font.SysFont('monaco', 22)
        bomb = font2.render('7  Бомба: 1000 ({})'.format(bomb_av),
                            True, WHITE)
        boost = font2.render('5  Быстрые выстрелы: 500 ({})'.format(boost_av),
                             True, WHITE)
        reverse = font2.render('3  Обратный ход: 300 ({})'.format(reverse_av),
                               True, WHITE)
        freeze = font2.render('1  Замедление: 100 ({})'.format(freeze_av),
                              True, WHITE)
        screen.blit(bonus, (750, 10))
        screen.blit(freeze, (750, 30))
        screen.blit(reverse, (750, 50))
        screen.blit(boost, (750, 70))
        screen.blit(bomb, (750, 90))
        screen.blit(timer, (50, 300))
        screen.blit(lives, (50, 350))
        screen.blit(score, (50, 400))
        screen.blit(level, (50, 450))

    def game_over(self):
        pygame.mixer.music.stop()
        game_over_sound.play()
        font = pygame.font.SysFont('monaco', 80)
        game_over = font.render('Игра окончена', True, WHITE)
        screen.blit(game_over, (500, 200))
        pygame.display.flip()
        time.sleep(3)
        pygame.quit()
        sys.exit()


class Skull(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = skull_image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.radius = 15

    def update(self):
        screen.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.shooting = False
        self.timing = 0.25
        self.timer = 0
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = (width / 2, height / 2)
        self.x = width / 2
        self.y = height / 2
        self.angle = 0

    def rotate(self, x, y):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
        self.angle = ((180 / math.pi) * -math.atan2(rel_y, rel_x))
        angle = ((180 / math.pi) * -math.atan2(rel_y, rel_x)) + 90
        rotated_image = pygame.transform.rotate(self.image, int(angle))

        w, h = self.image.get_size()
        box = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0),
               (w, -h), (0, -h)]]
        box_rotate = [p.rotate(self.angle) for p in box]
        min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate,
                   key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate,
                   key=lambda p: p[1])[1])

        pivot = pygame.math.Vector2(-w/2, -h/2)
        pivot_rotate = pivot.rotate(angle)
        pivot_move = pivot_rotate - pivot
        pos = (600, 250)

        origin = (pos[0] - w/2 + min_box[0] - pivot_move[0],
                  pos[1] - h/2 - max_box[1] + pivot_move[1])

        screen.blit(rotated_image, origin)

    def update(self):
        if self.shooting:
            tim = self.timing + self.timer - time.time()
            if tim <= 0:
                self.timer = 0
                self.shoot()
            if self.timer == 0:
                self.timer = time.time()
        self.rotate(self.x, self.y)

    def nextBullet(self, typ):
        global current_bullet
        global game
        if typ == "normal":
            current_bullet = random.choice(balls_images)
        if typ == "bomb":
            current_bullet = bomb_image
        list(game.current_bullet_sprite)[0].image = current_bullet

    def shoot(self):
        global current_bullet
        shoot_sound.play()
        bullet = Ball(self.angle, "bullet", 0, current_bullet, "unknown", 0, 0)
        game.bullet_sprites.add(bullet)
        game.all_sprites.add(bullet)


class Ball(pygame.sprite.Sprite):

    def __init__(self, angle, typ, number, image, level, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 1
        self.number = number
        self.type = typ
        self.level = level
        self.image = image
        self.angle = angle
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        if self.level == "Первый":
            self.rect.x = x
            self.rect.y = y
        if self.type == "bullet":
            self.rect.center = (width / 2, height / 2)
        self.shoot_angle = self.angle + 90
        self.radius = 10

    def update(self):
        if self.level == "Нулевой":
            if self.type == "common":
                self.circle(525, 250, 125)
            if self.type == "reverse":
                self.reverse_circle(525, 250, 125)
        if self.level == "Первый":
            if self.type == "common":
                self.maze()
            if self.type == "reverse":
                self.reverse_maze()
        if self.type == "bullet":
            self.bullet()
        if self.type == "current_bullet":
            self.current_bullet()

    def maze(self):
        speed = (1 * self.speed)
        if self.rect.x < 900 and self.rect.y == 100:
            self.rect.x += speed
        elif self.rect.x == 900 and self.rect.y < 400:
            self.rect.y += speed
        elif self.rect.x > 100 and self.rect.y == 400:
            self.rect.x -= speed
        elif self.rect.x == 100 and self.rect.y > 150:
            self.rect.y -= speed
        elif self.rect.x < 850 and self.rect.y == 150:
            self.rect.x += speed
        elif self.rect.x == 850 and self.rect.y < 350:
            self.rect.y += speed
        elif self.rect.x > 150 and self.rect.y == 350:
            self.rect.x -= speed
        elif self.rect.x == 150 and self.rect.y > 200:
            self.rect.y -= speed

    def reverse_maze(self):
        speed = (1 * self.speed)
        if self.rect.x > 100 and self.rect.y == 100:
            self.rect.x -= speed
        elif self.rect.x == 900 and self.rect.y > 100:
            self.rect.y -= speed
        elif self.rect.x < 900 and self.rect.y == 400:
            self.rect.x += speed
        elif self.rect.x == 100 and self.rect.y < 400:
            self.rect.y += speed
        elif self.rect.x > 100 and self.rect.y == 150:
            self.rect.x -= speed
        elif self.rect.x == 850 and self.rect.y > 150:
            self.rect.y -= speed
        elif self.rect.x < 850 and self.rect.y == 350:
            self.rect.x += speed
        elif self.rect.x == 150 and self.rect.y < 350:
            self.rect.y += speed

    def reduce_distance(self):
        if self.level == "Нулевой":
            self.reverse_circle(525, 250, 125)
        if self.level == "Первый":
            self.reverse_maze()

    def current_bullet(self):
        self.rect.x = 50
        self.rect.y = 50

    def return_new_ball_pos(self):
        if self.level == "Нулевой":
            for i in range(50):
                self.circle(525, 250, 125)
            angle = self.angle
            x = self.rect.x
            y = self.rect.y
            for i in range(50):
                self.reverse_circle(525, 250, 125)
            return angle, x, y
        if self.level == "Первый":
            for i in range(30):
                self.maze()
            angle = self.angle
            x = self.rect.x
            y = self.rect.y
            for i in range(30):
                self.reverse_maze()
            return angle, x, y

    def correct_sprites_trajectory(self):
        if self.level == "Нулевой":
            for i in range(50):
                self.circle(525, 250, 125)
        if self.level == "Первый":
            for i in range(50):
                self.update()

    def circle(self, x, y, radius):
        self.angle += 0.005 * self.speed
        self.rect.x = x + radius * math.cos(self.angle)
        self.rect.y = y + radius * math.sin(self.angle)

    def reverse_circle(self, x, y, radius):
        self.angle -= 0.005 * self.speed
        self.rect.x = x + radius * math.cos(self.angle)
        self.rect.y = y + radius * math.sin(self.angle)

    def bullet(self):
        global game
        self.rect.y += (math.cos(math.pi * self.shoot_angle / 180) *
                        game.bullet_speed)
        self.rect.x += (math.sin(math.pi * self.shoot_angle / 180) *
                        game.bullet_speed)
        if (self.rect.x < 0 or self.rect.x > width
           or self.rect.y < 0 or self.rect.y > height):
            self.kill()


def make_Sprites(first, last, amount, typ, level, score, time):
    global game
    all_sprites = pygame.sprite.Group()
    ball_sprites = pygame.sprite.Group()
    bullet_sprites = pygame.sprite.Group()
    skull_spites = pygame.sprite.Group()
    current_bullet_sprite = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    if level == "Первый":
        skull = Skull(135, 185)
        all_sprites.add(skull)
        skull_spites.add(skull)
    counter = 0
    for i in range(first, last):
        angle = 0.25*i
        image = random.choice(balls_images)
        number = amount - counter
        x = 180 + (angle * 120)
        y = 100
        ball = Ball(angle, typ, number, image, level, x, y)
        counter += 1
        ball_sprites.add(ball)
        all_sprites.add(ball)

    current_ball = Ball(0, "current_bullet", 0, current_bullet, level, 0, 0)
    current_bullet_sprite.add(current_ball)
    angle = 0
    balls = list(ball_sprites)
    game = Game(player, all_sprites, ball_sprites, bullet_sprites,
                skull_spites, balls, current_bullet_sprite,
                typ, level, score, time)


make_Sprites(0, 10, 10, "common", "Нулевой", 0, 45)

while True:

    clock.tick(FPS)
    game.bring_balls_together()
    game.get_events()
    game.check_hits()
    game.count_duplicates()

    screen.blit(back_image, [0, 0])
    game.current_bullet_sprite.update()
    game.current_bullet_sprite.draw(screen)
    game.all_sprites.update()
    game.ball_sprites.update()
    game.bullet_sprites.update()
    game.ball_sprites.draw(screen)
    game.bullet_sprites.draw(screen)
    game.show_score_and_level()
    pygame.display.flip()

    if game.bomb_time_left == 0:
        game.bomb_explode()
        game.bomb_timer = 0
    if game.time_left == 0:
        game.game_over()
    if len(game.ball_sprites) == 0 and game.level == "Нулевой":
        make_Sprites(0, 10, 10, "common", "Первый", game.score, 90)
        game.level = 'Первый'
    if len(game.ball_sprites) == 0 and game.level == "Первый":
        game.game_over()

pygame.quit()
