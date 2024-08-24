import pygame
import time
import random
import math
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption('High Noon')

WIDTH, HEIGHT = 1600, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

BG = pygame.transform.scale(pygame.image.load('High Noon/Cowboy-BG.jpg'), (WIDTH, WIDTH))
PLAYER = pygame.transform.scale(pygame.image.load('High Noon/Cowboy1/idle.png'), (HEIGHT/3, HEIGHT/3))
COMPUTER = pygame.transform.scale(pygame.image.load('High Noon/Cowboy2/idle.png'), (HEIGHT/3, HEIGHT/3))

TITLE_FONT_HEIGHT = int(HEIGHT/4)
TITLE_FONT = pygame.font.Font('High Noon/RioGrande.ttf', TITLE_FONT_HEIGHT)
START_FONT_HEIGHT = int(TITLE_FONT_HEIGHT/4)
START_FONT = pygame.font.Font('High Noon/RioGrande.ttf', START_FONT_HEIGHT)

HELP_FONT_HEIGHT = int(HEIGHT/30)
HELP_FONT = pygame.font.Font('High Noon/Dust-West.otf', HELP_FONT_HEIGHT)

BUTTON_WIDTH = WIDTH/8
BUTTON_HEIGHT = BUTTON_WIDTH/4

HOLSTER = pygame.transform.scale(pygame.image.load('High Noon/holster.png'), (HEIGHT/5, HEIGHT/5))
HOLSTER_POS = (WIDTH/2 - HOLSTER.get_width()/2, HEIGHT - (1.3*HOLSTER.get_height()))
HOLSTER_TEXT = pygame.transform.scale(pygame.image.load('High Noon/holster_text.png'), (HEIGHT/2, HEIGHT/8))

TARGET_SIZE = int(HEIGHT/8)
TARGET_RADIUS = TARGET_SIZE*0.4

TIMER_FONT = pygame.font.Font('High Noon/DS-DIGIB.ttf', int(TITLE_FONT_HEIGHT/2))
TIMER_BOX_SIZE = TIMER_FONT.render('00.00', 1, 'green')

END_SCREEN_SIZE = WIDTH/2
END_SCREEN = pygame.transform.scale(pygame.image.load('High Noon/sign.png'), (END_SCREEN_SIZE, END_SCREEN_SIZE))

WIN_FONT_HEIGHT = int(HEIGHT/8)
WIN_FONT = pygame.font.Font('High Noon/RioGrande.ttf', WIN_FONT_HEIGHT)

STATS_FONT_HEIGHT = int(HEIGHT/12)
STATS_FONT = pygame.font.Font('High Noon/Dust-West.otf', STATS_FONT_HEIGHT)

TRANSPARENCY = pygame.transform.scale(pygame.image.load('High Noon/transparency.png'), (WIDTH, HEIGHT))

SPEED_TARGETS = 15
ACCURACY_TARGETS = 12
ACCURACY_TIME = 30

gunshot_sound = pygame.mixer.Sound('High Noon/Audio/gunshot.mp3')
bird_sound = pygame.mixer.Sound('High Noon/Audio/bird.mp3')
target_break_1 = pygame.mixer.Sound('High Noon/Audio/target-break-1.wav')
target_break_2 = pygame.mixer.Sound('High Noon/Audio/target-break-2.ogg')
whip_sound = pygame.mixer.Sound('High Noon/Audio/whip.wav')
pygame.mixer.Sound.set_volume(gunshot_sound, 0.3)
pygame.mixer.Sound.set_volume(target_break_1, 0.8)
pygame.mixer.Sound.set_volume(target_break_2, 0.8)

pygame.mixer.music.load('High Noon/Audio/High-Noon-Theme.wav')
pygame.mixer.music.set_volume(0.3)

def load_sprite_sheets(dir1, width, height):
    path = join('High Noon', dir1)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            if dir1 != 'Target':
                sprites.append(pygame.transform.scale(surface, (HEIGHT/3, HEIGHT/3)))
            else:
                sprites.append(pygame.transform.scale(surface, (TARGET_SIZE, TARGET_SIZE)))

        all_sprites[image.replace('.png', '')] = sprites
    
    return all_sprites

class Button():    
    def __init__(self, x, y, name):
        self.image = pygame.transform.scale(pygame.image.load(f'High Noon/Buttons/{name}.png'), (BUTTON_WIDTH, BUTTON_HEIGHT))
        self.border = pygame.transform.scale(pygame.image.load(f'High Noon/Buttons/{name}_bordered.png'), (BUTTON_WIDTH, BUTTON_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.x = x
        self.y = y
        self.clicked = False

    def draw(self):
        is_clicked = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            WIN.blit(self.border, (self.rect.x, self.rect.y))
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                is_clicked = True
        else:
            WIN.blit(self.image, (self.rect.x, self.rect.y))

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return is_clicked     

class Target(pygame.sprite.Sprite):
    SPRITES = load_sprite_sheets('Target', 40, 40)
    ANIMATION_DELAY = int(FPS/30)

    def __init__(self, x, y):
        self.breaking = False
        self.animation_count = 0
        self.x = x
        self.y = y
        self.center = (self.x + TARGET_SIZE/2, self.y + TARGET_SIZE/2)

    def update_sprite(self):
        sprite_sheet = 'idle'
        if self.breaking:
            sprite_sheet = 'breaking'
        
        self.sprites = self.SPRITES[sprite_sheet]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.sprite = self.sprites[sprite_index]
        self.animation_count += 1

    def draw(self, win):
        win.blit(self.sprite, (self.x, self.y))

    def collide(self, mouse_x, mouse_y):
        dis = math.sqrt((mouse_x - self.center[0])**2 + (mouse_y - self.center[1])**2)
        return dis <= TARGET_RADIUS

class Player(pygame.sprite.Sprite):
    SPRITES = load_sprite_sheets('Cowboy1', 128, 128)
    ANIMATION_DELAY = int(FPS/12)

    def __init__(self, x, y, width, height):
        super().__init__()
        self.animation_count = 0
        self.x = x
        self.y = y
        self.shoot = False
        self.spin = False    

    def update_sprite(self):
        sprite_sheet = 'idle'
        if self.shoot:
            sprite_sheet = 'shoot'
        if self.spin:
            sprite_sheet = 'spin'
        
        self.sprites = self.SPRITES[sprite_sheet]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.sprite = self.sprites[sprite_index]
        self.animation_count += 1

    def draw(self, win):
        win.blit(self.sprite, (self.x, self.y))

class Computer(pygame.sprite.Sprite):
    SPRITES = load_sprite_sheets('Cowboy2', 128, 128)
    ANIMATION_DELAY = int(FPS/12)

    def __init__(self, x, y, width, height):
        super().__init__()
        self.animation_count = 0
        self.x = x
        self.y = y        
        self.shoot = False
        self.spin = False

    def update_sprite(self):
        sprite_sheet = 'idle'
        if self.shoot:
            sprite_sheet = 'shoot'
        if self.spin:
            sprite_sheet = 'spin'
        
        self.sprites = self.SPRITES[sprite_sheet]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(self.sprites)
        self.sprite = self.sprites[sprite_index]
        self.animation_count += 1

    def draw(self, win):
        win.blit(self.sprite, (self.x, self.y))

def check_holster():
    pos = pygame.mouse.get_pos()
    holster_rect = HOLSTER.get_rect(topleft=(HOLSTER_POS))
    
    if holster_rect.collidepoint(pos):
        return True

def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))

    return f'{seconds:02d}.{milli:02d}'

def reset_animations(player, computer):
    player.shoot = False
    player.spin = False
    player.animation_count = 0
    computer.shoot = False
    computer.spin = False
    computer.anitmation_count = 0

def create_targets(targets, x_bounds, y_bounds):
    collision = False
    target = Target(random.uniform(*x_bounds), random.uniform(*y_bounds))
    
    for check in targets:
        for i in range(0, TARGET_SIZE, 20):
            for j in range(0, TARGET_SIZE, 20):
                if check.collide(target.x + i, target.y + j):
                    collision = True

    if collision == False:
        targets.append(target)

    return targets

def play_speed(win, player, computer, BG, mode, diff=None):    
    clock = pygame.time.Clock()

    x_bounds = (WIDTH/2, WIDTH - TARGET_SIZE)
    y_bounds = (TITLE_FONT_HEIGHT/2, HEIGHT - PLAYER.get_height())

    if mode[0] == 'vs':
        x_bounds = (WIDTH/4, 3*WIDTH/4)

    targets = []

    while len(targets) < SPEED_TARGETS:
        targets = create_targets(targets, x_bounds, y_bounds)
    
    
    clicks = 0
    player_hits = 0
    computer_increment = 0
    computer_counter = 0
    computer_hits = 0
    
    if diff == 'easy':
        computer_increment = 1
    elif diff == 'medium':
        computer_increment = 3
    elif diff == 'hard':
        computer_increment = 5

    pygame.mixer.Sound.play(whip_sound)
    start_time = time.time()    
    run = True
    while run:
        clock.tick(FPS)
        click = False
        pos = pygame.mouse.get_pos()
        elapsed_time = round(time.time() - start_time, 2)
        elapsed_time = format_time(elapsed_time)
        computer_counter += computer_increment

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1
                player.shoot = True
                player.animation_count = 0
                pygame.mixer.Sound.play(gunshot_sound)

        for target in targets:
            if click and target.collide(*pos) and target.breaking == False:
                target.breaking = True
                target.animation_count = 0
                player_hits += 1
                pygame.mixer.Sound.play(random.choice([target_break_1, target_break_2]))
        
        if mode[0] == 'vs':
            for target in targets:
                if target.breaking == False and computer_counter >= 120:
                    target.breaking = True
                    target.animation_count = 0
                    computer_hits += 1
                    computer_counter = 0
                    computer.shoot = True
                    computer.animation_count = 0
                    pygame.mixer.Sound.play(gunshot_sound)
                    pygame.mixer.Sound.play(random.choice([target_break_1, target_break_2]))


        if player_hits + computer_hits >= SPEED_TARGETS:
            break
        
        for target in targets:
            target.update_sprite()
            if target.breaking and target.animation_count > target.ANIMATION_DELAY * len(target.sprites):
                targets.remove(target)
        
        if player.shoot and player.animation_count > player.ANIMATION_DELAY * len(player.sprites):
            player.shoot = False
        
        if computer.shoot and computer.animation_count > computer.ANIMATION_DELAY * len(computer.sprites):
            computer.shoot = False

        player.update_sprite()
        computer.update_sprite()
        draw(WIN, player, computer, BG, mode, targets, True, elapsed_time)

    return((elapsed_time, clicks, player_hits, computer_hits))

def play_accuracy(win, player, computer, BG, mode, diff=None):
    clock = pygame.time.Clock()

    x_bounds = (WIDTH/2, WIDTH - TARGET_SIZE)
    y_bounds = (TITLE_FONT_HEIGHT/2, HEIGHT - PLAYER.get_height())

    if mode[0] == 'vs':
        x_bounds = (WIDTH/4, 3*WIDTH/4)

    targets = []

    while len(targets) < ACCURACY_TARGETS:
        targets = create_targets(targets, x_bounds, y_bounds)

    clicks = 0
    player_hits = 0
    computer_increment = 0
    computer_counter = 0
    computer_hits = 0
    
    if diff == 'easy':
        computer_increment = 1
    elif diff == 'medium':
        computer_increment = 3
    elif diff == 'hard':
        computer_increment = 5
    
    pygame.mixer.Sound.play(whip_sound)
    start_time = time.time()
    run = True
    while run:
        clock.tick(FPS)
        click = False
        pos = pygame.mouse.get_pos()
        elapsed_time = round(time.time() - start_time, 2)
        time_left = ACCURACY_TIME - elapsed_time
        elapsed_time = format_time(elapsed_time)
        time_left = format_time(time_left)
        computer_counter += computer_increment

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1
                player.shoot = True
                player.animation_count = 0
                pygame.mixer.Sound.play(gunshot_sound)

        for target in targets:
            if click and target.collide(*pos) and target.breaking == False:
                target.breaking = True
                target.animation_count = 0
                player_hits += 1
                pygame.mixer.Sound.play(random.choice([target_break_1, target_break_2]))
        
        if mode[0] == 'vs':
            for target in targets:
                if target.breaking == False and computer_counter >= 120:
                    target.breaking = True
                    target.animation_count = 0
                    computer_hits += 1
                    computer_counter = 0
                    computer.shoot = True
                    computer.animation_count = 0
                    pygame.mixer.Sound.play(gunshot_sound)
                    pygame.mixer.Sound.play(random.choice([target_break_1, target_break_2]))


        if time.time() >= start_time + 30:
            break
        
        if len(targets) < ACCURACY_TARGETS:
            create_targets(targets, x_bounds, y_bounds)

        for target in targets:
            target.update_sprite()
            if target.breaking and target.animation_count > target.ANIMATION_DELAY * len(target.sprites):
                targets.remove(target)
        
        if player.shoot and player.animation_count > player.ANIMATION_DELAY * len(player.sprites):
            player.shoot = False
        
        if computer.shoot and computer.animation_count > computer.ANIMATION_DELAY * len(computer.sprites):
            computer.shoot = False

        player.update_sprite()
        computer.update_sprite()
        draw(WIN, player, computer, BG, mode, targets, True, time_left)

    return((elapsed_time, clicks, player_hits, computer_hits))
    

def end_screen(win, bg, stats, mode, player, computer):
    reset_animations(player, computer)
    pygame.mixer.music.play()
    sign_y = HEIGHT
    sign_vel = HEIGHT/350
    scroll = 0
    clock = pygame.time.Clock()
    elapsed_time, clicks, player_hits, computer_hits = stats[0], stats[1], stats[2], stats[3]
    if clicks != 0:
        accuracy = round((player_hits/clicks)*100, 2)
    else:
        accuracy = 0    
    play_again_button = Button(WIDTH/4 - BUTTON_WIDTH/2, 3*HEIGHT/4, 'button_play_again')
    change_mode_button = Button(WIDTH/2 - BUTTON_WIDTH/2, 3*HEIGHT/4, 'button_change_mode')
    quit_button = Button(3*WIDTH/4 - BUTTON_WIDTH/2, 3*HEIGHT/4, 'button_quit')


    end_texts_left = []
    end_texts_right = []
    end_texts_left.append(STATS_FONT.render('Time: ', 1, 'black'))
    end_texts_right.append(STATS_FONT.render(f'{elapsed_time}s', 1, 'black'))
    end_texts_left.append(STATS_FONT.render('Clicks: ', 1, 'black'))
    end_texts_right.append(STATS_FONT.render(f'{clicks}', 1, 'black'))
    end_texts_left.append(STATS_FONT.render('Hits: ', 1, 'black'))
    end_texts_right.append(STATS_FONT.render(f'{player_hits}', 1, 'black'))
    end_texts_left.append(STATS_FONT.render('Acc: ', 1, 'black'))
    end_texts_right.append(STATS_FONT.render(f'{accuracy}%', 1, 'black'))
    if mode[0] == 'vs':
        end_texts_left.append(STATS_FONT.render('CPU Hits: ', 1, 'black'))
        end_texts_right.append(STATS_FONT.render(f'{computer_hits}', 1, 'black'))
    
    winner_text = WIN_FONT.render('YOU WIN!', 1, 'red')
    loser_text = WIN_FONT.render('YOU LOSE!', 1, 'red')
    tied_text = WIN_FONT.render('YOU TIED!', 1, 'red')

    while True:
        clock.tick(FPS)
        win.blit(bg, (0, HEIGHT - WIDTH))
        player.draw(win)
        if mode[0] == 'vs':
            computer.draw(win)
        win.blit(END_SCREEN, (WIDTH/2 - END_SCREEN.get_width()/2, HEIGHT-(scroll*sign_vel)))
        for i, text in enumerate(end_texts_left):
            win.blit(text, (WIDTH/2 - text.get_width() + END_SCREEN_SIZE/32, HEIGHT + 35 + (i*(STATS_FONT_HEIGHT-12)) - (scroll*sign_vel)))
        for i, text in enumerate(end_texts_right):
            win.blit(text, (WIDTH/2 + END_SCREEN_SIZE/32, HEIGHT + 35 + (i*(STATS_FONT_HEIGHT-12)) - (scroll*sign_vel)))
        if player_hits > computer_hits:
            win.blit(winner_text, (WIDTH/2 - winner_text.get_width()/2 + END_SCREEN_SIZE/32, 35))
            player.spin = True
        elif player_hits < computer_hits and mode[0] == 'vs':
            win.blit(loser_text, (WIDTH/2 - winner_text.get_width()/2 + END_SCREEN_SIZE/32, 35))
            computer.spin = True
        elif player_hits == computer_hits and mode[0] == 'vs':
            win.blit(tied_text, (WIDTH/2 - winner_text.get_width()/2 + END_SCREEN_SIZE/32, 35))

        player.update_sprite()
        computer.update_sprite()

        if sign_y > HEIGHT - END_SCREEN_SIZE:
            sign_y -= sign_vel
            scroll += 1

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            if play_again_button.draw():
                return False
            if change_mode_button.draw():
                return True
            if quit_button.draw():
                pygame.quit()

        pygame.display.update()    

def draw(win, player, computer, bg, mode, targets=[], start=False, elapsed_time=0):
    
    win.blit(bg, (0, HEIGHT - WIDTH))
    player.draw(win)
    if mode[0] == 'vs':
        computer.draw(win)
    if mode[1] != None and start == False:
        win.blit(HOLSTER, HOLSTER_POS)
    if check_holster() and start == False:
        win.blit(HOLSTER_TEXT, (WIDTH/2 - HOLSTER_TEXT.get_width()/2, HEIGHT/3 - HOLSTER_TEXT.get_height()/2))
    for target in targets:        
        target.draw(win)
    if start:
        timer_text = START_FONT.render(f'Time: {elapsed_time}', 1, 'black')
        win.blit(timer_text, (WIDTH/2 - timer_text.get_width()/2, 0))



    pygame.display.update()


def BG_scroll_solo(win, title):
    bg_y = 0
    bg_vel = HEIGHT/500
    i = 1
    clock = pygame.time.Clock()
    pygame.mixer.Sound.play(bird_sound)
    pygame.mixer.music.fadeout(5000)

    while bg_y > HEIGHT - WIDTH:
        clock.tick(FPS)
        win.blit(BG, (0, 0-(i*bg_vel)))
        win.blit(title, (WIDTH/2 - title.get_width()/2, 50-(i*bg_vel)))
        win.blit(PLAYER, (0, BG.get_height()-PLAYER.get_height()-50-(i*bg_vel)))
        pygame.display.update()
        bg_y -= bg_vel
        player_y = BG.get_height()-PLAYER.get_height()-50-(i*bg_vel)
        i += 1

    return True, player_y

def BG_scroll_vs(win, title):
    bg_y = 0
    bg_vel = HEIGHT/500
    i = 1
    clock = pygame.time.Clock()
    pygame.mixer.Sound.play(bird_sound)
    pygame.mixer.music.fadeout(5000)

    while bg_y > HEIGHT - WIDTH:
        clock.tick(FPS)
        win.blit(BG, (0, 0-(i*bg_vel)))
        win.blit(title, (WIDTH/2 - title.get_width()/2, 50-(i*bg_vel)))
        win.blit(PLAYER, (0, BG.get_height()-PLAYER.get_height()-50-(i*bg_vel)))
        win.blit(COMPUTER, (WIDTH-COMPUTER.get_height(), BG.get_height()-PLAYER.get_height()-50-(i*bg_vel)))
        pygame.display.update()
        bg_y -= bg_vel
        player_y = BG.get_height()-PLAYER.get_height()-50-(i*bg_vel)
        i += 1

    return True, player_y

def select_diff(mode=None):
    easy_button = Button(WIDTH/4 - BUTTON_WIDTH/2, 3*HEIGHT/4, 'button_easy')
    medium_button = Button(WIDTH/2 - BUTTON_WIDTH/2, 3*HEIGHT/4, 'button_medium')
    hard_button = Button(3*WIDTH/4 - BUTTON_WIDTH/2, 3*HEIGHT/4, 'button_hard')

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        if mode == 'vs':

            if easy_button.draw():
                diff = 'easy'
                break
            if medium_button.draw():
                diff = 'medium'
                break
            if hard_button.draw():
                diff = 'hard'
                break
        else:
            diff = None
            break

        pygame.display.update()

    return diff

def start_game():
    start = False
    help = False
    pygame.mixer.music.play()
    title = TITLE_FONT.render('High Noon', 1, 'red')
    start_text = START_FONT.render('SELECT GAME MODE', 1, 'red')
    solo_text = START_FONT.render('SOLO', 1, 'red')
    vs_text = START_FONT.render('VS COMPUTER', 1, 'red')
    how_to_text = []
    how_to_text.append(HELP_FONT.render(f'Speed Mode: Shoot the {SPEED_TARGETS} targets as quickly as possible', 1, 'black'))
    how_to_text.append(HELP_FONT.render(f'Accuracy Mode: Shoot as many targets as you can in {ACCURACY_TIME} seconds', 1, 'black'))
    how_to_text.append(HELP_FONT.render(' ', 1, 'black'))
    how_to_text.append(HELP_FONT.render('HOW TO PLAY', 1, 'black'))
    how_to_text.append(HELP_FONT.render('Hover your cursor over the holster', 1, 'black'))
    how_to_text.append(HELP_FONT.render('After a random amount of time, the game will begin', 1, 'black'))
    how_to_text.append(HELP_FONT.render('Click on the targets to shoot them', 1, 'black'))
    speed_solo_button = Button(WIDTH/4 - (1.1*BUTTON_WIDTH), HEIGHT/2 + (2*BUTTON_HEIGHT), 'button_speed')
    accuracy_solo_button = Button(WIDTH/4 + (0.1*BUTTON_WIDTH), HEIGHT/2 + (2*BUTTON_HEIGHT), 'button_accuracy')
    speed_vs_button = Button(3*WIDTH/4 - (1.1*BUTTON_WIDTH), HEIGHT/2 + (2*BUTTON_HEIGHT), 'button_speed')
    accuracy_vs_button = Button(3*WIDTH/4 + (0.1*BUTTON_WIDTH), HEIGHT/2 + (2*BUTTON_HEIGHT), 'button_accuracy')
    how_to_play_button = Button(WIDTH/2 - BUTTON_WIDTH/2, 4*HEIGHT/5, 'button_how-to-play')

    pygame.display.update()

    while start == False:

        WIN.blit(BG, (0, 0))
        WIN.blit(title, (WIDTH/2 - title.get_width()/2, 50))
        WIN.blit(start_text, (WIDTH/2 - start_text.get_width()/2, HEIGHT/3 + start_text.get_height()/2))
        WIN.blit(solo_text, (WIDTH/4 - solo_text.get_width()/2, HEIGHT/2 - solo_text.get_height()/2))
        WIN.blit(vs_text, ((3*WIDTH/4) - vs_text.get_width()/2, HEIGHT/2 - vs_text.get_height()/2))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if speed_vs_button.draw() and not help:
            diff = select_diff('vs')
            start, player_y = BG_scroll_vs(WIN, title)
            mode = ('vs', 'speed')
            break
        if accuracy_vs_button.draw() and not help:
            diff = select_diff('vs')
            start, player_y = BG_scroll_vs(WIN, title)
            mode = ('vs', 'accuracy')
            break
        if speed_solo_button.draw() and not help:
            diff = select_diff()
            start, player_y = BG_scroll_solo(WIN, title)
            mode = ('solo', 'speed')
            break
        if accuracy_solo_button.draw() and not help:
            diff = select_diff()
            start, player_y = BG_scroll_solo(WIN, title)
            mode = ('solo', 'accuracy')
            break
        if help:
            WIN.blit(TRANSPARENCY, (0, 0))
            WIN.blit(END_SCREEN, (WIDTH/2 - END_SCREEN.get_width()/2, HEIGHT - END_SCREEN_SIZE))
            for i, text in enumerate(how_to_text):
                WIN.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT - END_SCREEN_SIZE + ((2+i)*HELP_FONT_HEIGHT)))
        
        if how_to_play_button.draw():
            if help:
                help = False
            else:
                help = True
        
        
        pygame.display.update()

    return player_y, mode, diff

def main():
    run = True
    while run:
        player_y, mode, diff = start_game()
        clock = pygame.time.Clock()
        start_time = 0
        start_delay = 0
        targets = []
        stats = None
        reset = False

        player = Player(0, player_y, HEIGHT/3, HEIGHT/3)
        computer = Computer(WIDTH-(HEIGHT/3), player_y, HEIGHT/3, HEIGHT/3)

        while reset == False:
            clock.tick(FPS) 


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    reset = True
                    break
            
            if mode[1] == 'speed':
                if check_holster():
                    if start_time == 0:
                        start_time = time.time()
                        start_delay = random.uniform(2, 6)
                    if time.time() - start_time >= start_delay:
                        stats = play_speed(WIN, player, computer, BG, mode, diff)
                else:
                    start_time = 0
                    start_delay = 0
            
            elif mode [1] == 'accuracy':
                if check_holster():
                    if start_time == 0:
                        start_time = time.time()
                        start_delay = random.uniform(2, 6)
                    if time.time() - start_time >= start_delay:
                        stats = play_accuracy(WIN, player, computer, BG, mode, diff)
                else:
                    start_time = 0
                    start_delay = 0


            if stats != None:
                reset = end_screen(WIN, BG, stats, mode, player, computer)
                stats = None
                reset_animations(player, computer)
                if reset == False:
                    pygame.mixer.music.fadeout(3000)

            player.update_sprite()
            computer.update_sprite()
            draw(WIN, player, computer, BG, mode, targets)

if __name__ == '__main__':
    main()        