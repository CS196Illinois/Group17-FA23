import pygame
import time
import sys
from sys import exit
import math
import random
from NewSettings import *

pygame.init()

# Screen dimensions and setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background_image = pygame.transform.scale(pygame.image.load('Sprites/Maps/blue.png').convert(), (1280,720))
boundary = pygame.Rect(42, 53, 1148, 578)
pygame.display.set_caption("Top Down Shooter")

# Load Player
player_image = pygame.transform.scale(pygame.image.load('Sprites/Characters/character_main.png'), (50,40))
player_size = player_image.get_size()
player_health = 100
bullet_damage = 1

# Handle music
pygame.mixer.init()
pygame.mixer.set_num_channels(3)  # default is 8s
pygame.mixer.music.load("Sound/Music/surreal_sippin.mp3")
pygame.mixer.music.play(-1) # Loop indefinitely
laser_sound = pygame.mixer.Sound('Sound/SFX/blaster.mp3')
laser_sound.set_volume(0.25)
death_sound = pygame.mixer.Sound('Sound/SFX/yoda.mp3')
enemy_death = pygame.mixer.Sound('Sound/SFX/splat.mp3')

# Fonts
font = pygame.font.Font("PublicPixel.ttf", 20)
small_font = pygame.font.Font("PublicPixel.ttf", 15)
title_font = pygame.font.Font("PublicPixel.ttf", 60)
score_font = pygame.font.Font("PublicPixel.ttf", 50)

def get_angle_to_mouse(player_pos, mouse_pos):
    dx, dy = mouse_pos[0] - (player_pos[0] + player_size[0] // 2), mouse_pos[1] - (player_pos[1] + player_size[1] // 2)
    return math.degrees(math.atan2(-dy, dx)) - 90

def draw_player(screen, image, position, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=(position[0] + player_size[0] // 2, position[1] + player_size[1] // 2))
    screen.blit(rotated_image, new_rect.topleft)

def draw_enemy(screen, enemy, position):
    screen.blit(enemy, position)

# Game Over
def gameover():
    gameover = True
    s = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)   # per-pixel alpha
    s.fill((0, 0, 0, 128))                         # notice the alpha value in the color
    screen.blit(s, (0,0))
    volume = 1.0
    while gameover:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        
        text_gameover = font.render(f"GAME OVER", True, RED)
        screen.blit(text_gameover, (WIDTH / 2 - 80, HEIGHT / 2 - 10))
        volume *= 0.97
        pygame.mixer.music.set_volume(volume)

        pygame.display.update()
        clock.tick(60)  # Maintain a consistent framerate even in pause



# Player setup
player_size = player_image.get_size()
player_pos = [WIDTH//2, HEIGHT//2]
player_speed = 5
shoot_cooldown = 0

# Crate setup
crate_image = pygame.transform.scale(pygame.image.load('Sprites/Crates/crate_yellow.png'),(50,50))
crate_size = crate_image.get_size()

# Bullet setup
bullet_image = pygame.image.load('Sprites/Bullets/bullet_acidspit.png')
spitter_bullet_image = pygame.image.load('Sprites/Bullets/bullet_laser.png')
bullet_size = list(bullet_image.get_size())
bullets = []
enemy_bullet_size = list(spitter_bullet_image.get_size())
enemy_bullets = []  # List to store enemy bullets

# Enemy setup
enemy_image = pygame.transform.scale(pygame.image.load('Sprites/Mobs/mob_spitter.png'), (50,50))
enemy_size = enemy_image.get_size()
enemy_speed = 2
enemy_shoot_cooldown = 20
initial_enemy_position = [random.randint(42, 1190 - enemy_size[0]), random.randint(53,631 - enemy_size[1])]
enemies = []

class Enemy:
    def __init__(self, position):
        self.image = pygame.transform.scale(pygame.image.load('Sprites/Mobs/mob_spitter.png'), (45,35))
        self.pos = list(position)
        self.size = self.image.get_size()
        self.health = 10
        self.shoot_delay = 500  # Time in milliseconds between shots
        self.last_shot_time = pygame.time.get_ticks()
        self.transparency = 255  # Max transparency

    def draw(self, screen):
        self.image.set_alpha(self.transparency)
        screen.blit(self.image, self.pos)

    def take_damage(self):
        self.health -= 1
        self.transparency = max(0, self.transparency - 25)  # Reduce transparency by 10% of 255
        if self.health <= 0:
            return True
        return False
    
    def move_enemy(self, player_pos):
        angle = math.atan2(player_pos[1] - self.pos[1], player_pos[0] - self.pos[0])
        self.pos[0] += enemy_speed * math.cos(angle)
        self.pos[1] += enemy_speed * math.sin(angle)
    
    def attempt_to_shoot(self, current_time, enemy_bullets):
        if current_time - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = current_time
            bullet_angle = math.atan2(player_pos[1] - self.pos[1], player_pos[0] - self.pos[0])
            enemy_bullets.append([self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2, bullet_angle])

class SpeedPowerUp:
    def __init__(self, position):
        self.pos = position
        self.image = pygame.image.load('Sprites/Powerups/powerup_gold.png')
        self.size = self.image.get_size()
    
    def draw(self):
        screen.blit(self.image, self.pos)

    

# List to store enemies
enemies = [Enemy(initial_enemy_position)]  # Add the initial enemy
for x in range(5):
    new_enemy_pos = (random.randint(0, WIDTH - enemy_size[0]), random.randint(0, HEIGHT - enemy_size[1]))
    enemies.append(Enemy(new_enemy_pos))

def draw_bullet(position):
    screen.blit(bullet_image, position)

def draw_enemy_bullet(enemy_pos):
    screen.blit(spitter_bullet_image, enemy_pos)

num_crates = 15  # Number of crates
crates = []
for x in range(num_crates):
    crates.append()
crates = [(random.randint(42, 1190 - crate_size[0] - 100), random.randint(53, 631 - crate_size[1] - 100)) for x in range(num_crates)]

def draw_crates(screen, crate_image, crate_positions):
    for pos in crate_positions:
        screen.blit(crate_image, pos)

def is_collision_with_crate(new_player_pos, crate_pos, crate_size):
    player_rect = pygame.Rect(new_player_pos, player_size)
    crate_rect = pygame.Rect(crate_pos, crate_size)
    return player_rect.colliderect(crate_rect)

def is_collision(rect1_pos, rect1_size, rect2_pos, rect2_size):
    list_rect2_pos = list(rect2_pos)
    list_rect2_pos[0] += 60
    list_rect2_pos[1] += 50
    rect2_pos = tuple(list_rect2_pos)
    list_rect2_size = list(rect2_size)
    list_rect2_size[0] /= 10
    list_rect2_size[1] /= 3
    rect2_size = tuple(list_rect2_size)
    rect1 = pygame.Rect(rect1_pos, rect1_size)
    rect2 = pygame.Rect(rect2_pos, rect2_size)
    return rect1.colliderect(rect2)

class UI(): 
    def __init__(self): 
        self.current_health = 100
        self.maximum_health = 100
        self.health_bar_length = 100
        self.health_ratio = self.maximum_health / self.health_bar_length 
        self.current_colour = None

    def display_health_bar(self): 
        pygame.draw.rect(screen, BLACK, (50, 58, self.health_bar_length * 3, 20)) # black

        if self.current_health >= 75:
            pygame.draw.rect(screen, GREEN, (50, 58, self.current_health * 3 * self.health_ratio, 20)) # green    
            self.current_colour = GREEN
        elif self.current_health >= 25:
            pygame.draw.rect(screen, YELLOW, (50, 58, self.current_health * 3, 20)) # yellow
            self.current_colour = YELLOW 
        elif self.current_health >= 0:
            pygame.draw.rect(screen, RED, (50, 58, self.current_health * 3, 20)) # red 
            self.current_colour = RED

        pygame.draw.rect(screen, WHITE, (50, 58, self.health_bar_length * 3, 20), 4) # white border

    def display_health_text(self):
        health_surface = font.render(f"{player_health}/{self.maximum_health}", False, self.current_colour) 
        health_rect = health_surface.get_rect(center = (423, 67))
        screen.blit(health_surface, health_rect)

    def adjust_health(self, player_health):
        self.current_health = player_health

    def display_powerups(self):
        text_powerups = font.render(f"Powerup", True, WHITE)
        screen.blit(text_powerups, (1000, 80))
        pygame.draw.rect(screen, WHITE, (1151, 55, 80, 80), 4) 

    def update(self, player_health): 
        self.adjust_health(player_health)
        self.display_health_bar()
        self.display_health_text()
        self.display_powerups()

ui = UI()

# Game loop
running = True
clock = pygame.time.Clock()
ENEMY_SPAWN = pygame.USEREVENT + 2
GAME_OVER = pygame.USEREVENT + 2
enemy_spawn_time = 3000  # Initial spawn time in milliseconds (e.g., 5000 ms = 5 seconds)
min_enemy_spawn_time = 1000  # Minimum spawn time in milliseconds
pygame.time.set_timer(ENEMY_SPAWN, enemy_spawn_time)
SPEED_PU_SPAWN = pygame.USEREVENT + 2
pygame.time.set_timer(SPEED_PU_SPAWN, 5000)
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == ENEMY_SPAWN:
            # Creates a new enemy at a random spot in the map
            new_enemy_pos = (random.randint(0, WIDTH - enemy_size[0]), random.randint(0, HEIGHT - enemy_size[1]))
            enemies.append(Enemy(new_enemy_pos))

            # Reduce spawn time for next enemy, respecting the minimum limit
            enemy_spawn_time = max(min_enemy_spawn_time, (int)(enemy_spawn_time * 0.99))
            pygame.time.set_timer(ENEMY_SPAWN, enemy_spawn_time)
        if running == True and event.type == SPEED_PU_SPAWN:
            speed_pu_pos = [random.randint(42, 1090), random.randint(53,531)]
            SpeedPowerUp()
    
    keys = pygame.key.get_pressed()
    mx, my = pygame.mouse.get_pos()

    # Player movement
    new_player_pos = player_pos.copy()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_player_pos[0] += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_player_pos[1] += player_speed

    if new_player_pos[0] < boundary.left: # Check left boundary
        new_player_pos[0] = boundary.left

    if new_player_pos[0] > boundary.right: # Check right boundary
        new_player_pos[0] = boundary.right
        
    if new_player_pos[1] < boundary.top: # Check top boundary
        new_player_pos[1] = boundary.top
        
    if new_player_pos[1] > boundary.bottom: # Check bottom boundary
        new_player_pos[1] = boundary.bottom

    if not any(is_collision_with_crate(new_player_pos, crate, crate_size) for crate in crates):
        player_pos = new_player_pos

    # setting widths and heights of players for collision checking
    player_width, player_height = player_size
    enemy_width, enemy_height = enemy_size

    if shoot_cooldown > 0:
        shoot_cooldown -= 1
    
    if enemy_shoot_cooldown > 0:
        enemy_shoot_cooldown -= 1

    # Shooting bullets
    if keys[pygame.K_SPACE]:
        if shoot_cooldown == 0:
            shoot_cooldown = SHOOT_COOLDOWN
            pygame.mixer.Channel(1).play(laser_sound)
            player_center_x = player_pos[0] + player_width // 2
            player_center_y = player_pos[1] + player_height // 2
            bullet_angle = math.atan2(my - player_center_y, mx - player_center_x)
            bullets.append([player_center_x, player_center_y, bullet_angle])

    # Update bullet positions
    new_bullets = []
    for bullet in bullets:
        bx, by, angle = bullet
        bullet_pos = (bx, by)
        bx += 10 * math.cos(angle)
        by += 10 * math.sin(angle)
        
        # Check collision with crates
        bullet_hit_crate = any(is_collision(bullet_pos, bullet_size, crate_pos, crate_size) for crate_pos in crates)

        # Check collision with enemy
        bullet_hit_enemy = False
        for enemy in enemies:
            if is_collision(bullet_pos, bullet_size, enemy.pos, enemy.size):
                bullet_hit_enemy = True
                enemy.health -= bullet_damage
                if enemy.take_damage():
                    pygame.mixer.Channel(0).play(enemy_death)
                    enemies.remove(enemy)
                break

        # Remove bullet if it hits a crate or the enemy, or if it goes off-screen
        if not bullet_hit_crate and not bullet_hit_enemy and 0 <= bx <= WIDTH and 0 <= by <= HEIGHT:
            new_bullets.append([bx, by, angle])
    bullets = new_bullets

    new_enemy_bullets = []
    for enemy_bullet in enemy_bullets:
        ex, ey, enemy_angle = enemy_bullet
        enemy_bullet_pos = (ex, ey)
        ex += 5 * math.cos(enemy_angle)
        ey += 5 * math.sin(enemy_angle)

        # Check collision with crates
        enemy_bullet_hit_crate = any(is_collision(enemy_bullet_pos, enemy_bullet_size, crate_pos, crate_size) for crate_pos in crates)

        # Check collision with player
        enemy_bullet_hit_player = is_collision(enemy_bullet_pos, enemy_bullet_size, player_pos, player_size)

        # Remove bullet if it hits a crate or the player, or if it goes off-screen
        if not enemy_bullet_hit_crate and not enemy_bullet_hit_player and 0 <= ex <= WIDTH and 0 <= ey <= HEIGHT:
            new_enemy_bullets.append([ex, ey, enemy_angle])
        if enemy_bullet_hit_player:
            if player_health - 1 >= 0:
                player_health -= 1
    enemy_bullets = new_enemy_bullets

    # Drawing
    screen.blit(background_image, (0, 0))  # Draw the background image

    # Calculate rotation angle and draw player
    player_angle = get_angle_to_mouse(player_pos, (mx, my))

    draw_player(screen, player_image, player_pos, player_angle)
    draw_crates(screen, crate_image, crates)
    for bullet in bullets:
        draw_bullet((int(bullet[0]) - 29, int(bullet[1]) - 30))
    for enemy_bullet in enemy_bullets:
        draw_enemy_bullet((int(enemy_bullet[0]) - 29, int(enemy_bullet[1]) - 30))
    for enemy in enemies:
        enemy.move_enemy(player_pos)
        enemy.draw(screen)
        enemy.attempt_to_shoot(current_time, enemy_bullets)
    
    ui.update(player_health)
    pygame.display.flip()

    # Game Over
    if player_health <= 0:
        pygame.mixer.Channel(2).play(death_sound)
        gameover()
    clock.tick(60)

pygame.quit()
sys.exit()