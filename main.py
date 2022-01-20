import os
import pygame
from random import randint

pygame.init()

sound_button = pygame.mixer.Sound('data/sounds/button.mp3')
jump_sound = pygame.mixer.Sound('data/sounds/jump.mp3')
run_sound = pygame.mixer.Sound('data/sounds/run.mp3')

FPS = 30
WIDTH = 1280
HEIGHT = 720
level = 0
health = 3
counter = 25
level_person = 0
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


all_sprites = pygame.sprite.Group()
fruit = pygame.sprite.Group()


def print_text(message, x, y, font_color=(21, 36, 102), font_type='data/font/F77 Minecraft.ttf', font_size=30):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))


class AnimatedPlayer(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))


class AnimatedFruit(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(fruit)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))


class Player(AnimatedPlayer):
    right = True

    def __init__(self):
        self.names, self.columns, self.rows = self.AnimatePlayer('idle')
        super().__init__(load_image(self.names), self.columns, self.rows, 200, 500)
        self.level = None
        self.count = 0
        self.rect = self.image.get_rect()
        self.rect.move(self.rect.x, self.rect.y)
        self.change_x = 0
        self.change_y = 0
        self.idlecheck = True

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if not self.right:
            self.flip()
        self.calc_grav()
        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            self.change_y = 0

    def AnimatePlayer(self, do):
        if do == 'idle':
            self.names = 'Free/Main Characters/Virtual Guy/idle.png'
            self.columns = 11
            self.rows = 1
            return self.names, self.columns, self.rows

        elif do == 'jump':
            self.names = 'Free/Main Characters/Virtual Guy/jump.png'
            self.columns = 1
            self.rows = 1
            return self.names, self.columns, self.rows

        elif do == 'run':
            self.names = 'Free/Main Characters/Virtual Guy/Run.png'
            self.columns = 12
            self.rows = 1
            return self.names, self.columns, self.rows

        elif do == 'hit':
            self.names = "Free/Main Characters/Virtual Guy/Hit.png"
            self.columns = 7
            self.rows = 1
            return self.names, self.columns, self.rows

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 1
        if self.rect.y >= HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = HEIGHT - self.rect.height

    def jump_anim(self):
        self.names, self.columns, self.rows = self.AnimatePlayer('jump')
        super().__init__(load_image(self.names), self.columns, self.rows, self.rect.x, self.rect.y)

    def idle_anim(self):
        self.names, self.columns, self.rows = self.AnimatePlayer('idle')
        super().__init__(load_image(self.names), self.columns, self.rows, self.rect.x, self.rect.y)

    def run_anim(self):
        self.names, self.columns, self.rows = self.AnimatePlayer('run')
        super().__init__(load_image(self.names), self.columns, self.rows, self.rect.x, self.rect.y)

    def run_anim_left(self):
        self.names, self.columns, self.rows = self.AnimatePlayer('run')
        super().__init__(load_image(self.names), self.columns, self.rows, self.rect.x, self.rect.y)

    def hit_anim(self):
        self.names, self.columns, self.rows = self.AnimatePlayer('hit')
        super().__init__(load_image(self.names), self.columns, self.rows, self.rect.x, self.rect.y)

    def jump(self):
        pygame.mixer.stop()
        self.jump_anim()
        self.rect.y += 5
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 5
        if len(platform_hit_list) > 0 or self.rect.bottom >= HEIGHT:
            self.change_y = -15

    def go_left(self):
        pygame.mixer.Sound.play(run_sound)

        self.run_anim_left()
        self.change_x = -9
        if self.right:
            self.flip()
            self.right = False

    def go_right(self):
        pygame.mixer.Sound.play(run_sound)
        self.run_anim()
        self.change_x = 9
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):
        self.change_x = 0

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)


class Saw(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load("data\Free\Traps\Saw\On.png"), (1280, 720))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 720)


class Level(object):
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.player = player

    def update(self):
        self.platform_list.update()

    def draw(self):
        background = load_image("gackdround.png")
        background = pygame.transform.scale(background, (1280, 720))
        screen.blit(background, (0, 0))

        self.platform_list.draw(screen)


class Heart(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("data/Heart/Heart.png")
        self.image = pygame.transform.scale(self.image, (45, 45))
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = randint(5, 20)
        self.rect = self.rect.move(randint(35, 1250), 0)

    def update(self):
        platform_list = pygame.sprite.Group()
        platform_list.update()
        if self.rect.bottom > 720:
            self.change_y = 0
        self.rect.y += self.change_y


class Button:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inactive_color = (100, 120, 205)
        self.active_color = (110, 129, 212)

    def draw(self, x, y, message, font_size, do=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.active_color, (x, y, self.width, self.height), 5)
            if click[0] == 1:
                pygame.mixer.Sound.play(sound_button)
                pygame.time.delay(300)
                if do is not None:
                    if do == quit:
                        pygame.quit()
                        quit()
                    do()
        else:
            pygame.draw.rect(screen, self.inactive_color, (x, y, self.width, self.height), 100)

        print_text(message=message, x=x + 10, y=y + 10, font_size=font_size)


def draw_health():
    health_picture = pygame.transform.scale(load_image('Heart/Heart.png'), (50, 50))
    for i in range(health):
        screen.blit(health_picture, (60 * i, 25))


class Button_Image:
    def __init__(self, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self, x, y, do=None):
        global level
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            screen.blit(self.image, (x, y))
            if click[0] == 1:
                pygame.mixer.Sound.play(sound_button)
                pygame.time.delay(200)
                level = do
        else:
            screen.blit(self.image, (x, y))


class Apple(AnimatedPlayer):
    def __init__(self, x, y):
        super().__init__(pygame.transform.scale2x(load_image("Free/Items/Fruits/Apple.png")), 17, 1, x, y)

        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


def show_menu(gameover):
    global level
    menu_background = load_image('image/menu.jpg')
    show = True

    button_start = Button(430, 70)
    button_quit = Button(430, 70)
    button_levels = Button(430, 70)

    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        screen.blit(menu_background, (0, 0))
        button_quit.draw(424.5, 400.5, 'Quit', 50, quit)
        button_start.draw(424.5, 317.5, 'Play', 50, game)
        if level == 0:
            level = 1
        if gameover == 1:
            print_text('You Lose', 530, 230)
        pygame.display.update()
        clock.tick(60)


def choice_level():
    show = True

    while show:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    show = False


class Arrow1(pygame.sprite.Sprite):
    def __init__(self, x=1280, y=720):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.image.load("data/arrow1.png"), 270)
        self.image = pygame.transform.scale(self.image, (20, 68))
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.dobav = 15
        self.change_y = randint(5, self.dobav)
        self.level = 0
        self.rect = self.rect.move(x, y)

    def update(self):
        platform_list = pygame.sprite.Group()
        platform_list.update()
        self.rect.y += self.change_y


def game_over():
    pygame.mixer.stop()
    show_menu(1)


def draw_level(groupsprite, sprite):
    for i in range(5):
        groupsprite.add(sprite)


class Level_difficulty:
    level_person = 0

    def __init__(self, lvl_person):
        self.amount_apple = 5
        self.amount_arrow = lvl_person + 1
        self.amount_heart = 1
        self.finish = False


def print_count(count):
    print_text(('Ваш счет: ' + str(count)), 1000, 30)


def main():
    global health
    pygame.display.set_caption("Pixel Adventure")
    show_menu(0)
    while game():
        health = 3


class Block(pygame.sprite.Sprite):
    def __init__(self, xy):
        super().__init__()
        self.image = pygame.image.load("data/Free/Traps/Blocks/Idle.png")
        self.image = pygame.transform.scale(self.image, (60, 68))
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(xy)


def game():
    global health, counter

    pygame.display.set_icon(load_image('icon.png'))
    player = Player()
    apple = Apple(randint(30, 1250), 680)
    saw = Saw(0, 0)
    arrow1 = Arrow1(randint(10, 1270), 0)

    heart = Heart()
    saw_group = pygame.sprite.Group()
    arrow_group = pygame.sprite.Group()
    heart_group = pygame.sprite.Group()
    saw_group.add(saw)
    level_list = [Level(player)]

    current_level_no = level - 1
    current_level = level_list[current_level_no]
    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    fruit = pygame.sprite.Group()

    ld = Level_difficulty(1)

    def level_draw():
        Arrow1(randint(0, 1280), 0).dobav += 1
        arrow1 = Arrow1(randint(0, 1280), 10)
        if len(arrow_group) < counter / 7:
            arrow_group.add(arrow1)

        apple = Apple(randint(50, 1200), 670)
        if len(fruit) < 3:
            fruit.add(apple)

        heart = Heart()
        if len(heart_group) < 1:
            heart_group.add(heart)

    player.rect.x = 340
    player.rect.y = HEIGHT - player.rect.height
    active_sprite_list.add(player)

    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.jump_anim()
                    player.jump()
                    pygame.mixer.Sound.play(jump_sound)

                elif event.key == pygame.K_LEFT:
                    player.go_left()

                elif event.key == pygame.K_RIGHT:
                    player.go_right()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                    player.idle_anim()
                    pygame.mixer.stop()

                elif event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
                    player.idle_anim()
                    pygame.mixer.stop()
                elif event.key == pygame.K_ESCAPE:
                    show_menu(0)

        active_sprite_list.update()
        current_level.update()
        arrow_group.update()
        if player.rect.right > WIDTH:
            player.rect.right = WIDTH

        if player.rect.left < 0:
            player.rect.left = 0

        fruit.update()
        heart_group.update()

        current_level.draw()
        fruit.draw(screen)
        heart_group.draw(screen)

        active_sprite_list.draw(screen)
        arrow_group.draw(screen)
        saw_group.draw(screen)
        hits = pygame.sprite.spritecollide(player, arrow_group, True)
        hits_with_fruit = pygame.sprite.spritecollide(player, fruit, True)
        hits_with_heart = pygame.sprite.spritecollide(player, heart_group, True)
        hits_arrow_with_saw = pygame.sprite.spritecollide(saw, arrow_group, True)

        draw_health()
        print_count(player.count)

        level_draw()
        if hits_with_heart:
            health += 1

        if hits_arrow_with_saw:
            counter += 1
            arrow1.kill()

        if hits_with_fruit:
            player.count += 1
            apple.kill()

        if hits:
            health -= 1
            player.hit_anim()
            arrow1.kill()
            if health < 1:
                game_over()
        clock.tick(30)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
