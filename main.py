import pygame
from pygame.locals import *
import os
import random
pygame.init()

width = 800
height = 700

win = pygame.display.set_mode((width, height))
pygame.display.set_caption('Flappy Bird')

# LOAD IMAGES
background = pygame.transform.scale(pygame.image.load(os.path.join("images","bg.png")), (width, height))
ground = pygame.transform.scale(pygame.image.load(os.path.join("images", "ground.png")), (800, 200))
ground_width = width
ground_height = int(ground.get_height() * (ground_width / ground.get_width()))  
ground = pygame.transform.scale(ground, (ground_width, ground_height))
button_img = pygame.image.load(os.path.join("images", "restart.png"))

# Ground
ground_x = 0
ground_y = height - ground_height 
# Font and Text
font = pygame.font.SysFont('Bauhaus 93', 40)
text_col = (255, 255, 255)
# Game Variables
FPS = 60
clock = pygame.time.Clock()
flying = False
game_over = False
scroll_speed = 4
pipe_gap = 150
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency 
score = 0
pass_pipe = False

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(height / 2)
    score = 0
    return score


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1,4):
            img = pygame.image.load(os.path.join('images', f'bird{num}.png'))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vel = 0
        self.clicked = False

    def update(self):
        # Gravity
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < ground_y:
               self.rect.y += int(self.vel)
        if game_over == False:
        # Jump
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.clicked == False:
                self.clicked = True
                self.vel = -10

            if not keys[pygame.K_SPACE]:
                self.clicked = False

            # Animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotating the Bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
            
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("images", "pipe.png")), (100, 220))
        self.rect = self.image.get_rect()
        # Position of Pipe
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
            self.rect.midbottom = (x, y)

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw_button(self):
        clicked = False
        pos = pygame.mouse.get_pos()

        # Check mouse click and hover
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                clicked = True
        # Draw Button
        win.blit(self.image, (self.rect.x, self.rect.y))

        return clicked

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(height/2))
bird_group.add(flappy)
button = Button(width // 2 - 100, height // 2 - 50, button_img)

def draw():
    win.blit(background, (0,0))
    pipe_group.draw(win)
    win.blit(ground, (ground_x, ground_y))
    bird_group.draw(win)
    draw_text(str(score), font, text_col, 400, 20)

    if game_over:  
        button.draw_button()

    pygame.display.update()

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    win.blit(img, (x,y))


# Main Loop
run = True
while run:
    clock.tick(FPS)
    # Check The Score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
        and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    
    # Collision With pipe
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    #Check if bird hits ground
    if flappy.rect.bottom >= ground_y:
        game_over = True
        flying = False
    
    if game_over == False and flying == True:
        pipe_height = random.randint(-80, 80)
        #Generate New Pipe
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe > pipe_frequency:
            # Pipe spawning points
            btm_pipe_y = ground_y  
            top_pipe_y = ground_y - pipe_gap - 150 + pipe_height

            btm_pipe = Pipe(width, btm_pipe_y , -1)
            top_pipe = Pipe(width, top_pipe_y, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = current_time
        pipe_group.update()

    # Game Over and Reset
    if game_over == True:
        if button.draw_button() == True:
            game_over = False
            score = reset_game()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True


    if not game_over and flying:
        pipe_group.update()

    draw()
    bird_group.draw(win)
    bird_group.update()


pygame.quit()          