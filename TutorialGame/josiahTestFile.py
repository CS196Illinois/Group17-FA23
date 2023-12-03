import pygame
from sys import exit
import math
import random
from NewSettings import *

pygame.init()

# Screen dimensions and setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background_image = pygame.transform.scale(pygame.image.load('Sprites/Maps/blue.png').convert(), (1280,720))
pygame.display.set_caption("Rectangle and Triangle Game")

# Load images
player_image = pygame.image.load('Sprites/Characters/character_main.png')
bullet_image = pygame.image.load('Sprites/Bullets/bullet_laser.png')
enemy_image = pygame.image.load('Sprites/Mobs/mob_spitter.png')

# Player setup
player_size = player_image.get_size()
player_pos = [WIDTH//2, HEIGHT//2]
player_speed = 5

# Bullet setup
bullet_size = bullet_image.get_size()
bullets = []

# Enemy setup
enemy_size = enemy_image.get_size()
enemy_pos = [random.randint(0, WIDTH-enemy_size[0]), random.randint(0, HEIGHT-enemy_size[1])]
enemy_speed = 2
shoot_cooldown = 0

def draw_player(position):
    screen.blit(player_image, position)

def draw_bullet(position):
    screen.blit(bullet_image, position)

def draw_enemy(position):
    screen.blit(enemy_image, position)

def move_enemy(player_pos, enemy_pos):
    angle = math.atan2(player_pos[1] - enemy_pos[1], player_pos[0] - enemy_pos[0])
    enemy_pos[0] += enemy_speed * math.cos(angle)
    enemy_pos[1] += enemy_speed * math.sin(angle)
    return enemy_pos

def is_collision(enemy_pos, bullet):
    bx, by = bullet
    enemy_width, enemy_height = enemy_size
    ex, ey = enemy_pos[0] + enemy_width // 2, enemy_pos[1] + enemy_height // 2
    distance = math.sqrt((ex - bx) ** 2 + (ey - by) ** 2)
    return distance < enemy_height // 2

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    mx, my = pygame.mouse.get_pos()

    # Player movement
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_pos[0] += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player_pos[1] += player_speed

    # Keep player in screen bounds
    player_width, player_height = player_size
    player_pos[0] = max(0, min(player_pos[0], WIDTH - player_width))
    player_pos[1] = max(0, min(player_pos[1], HEIGHT - player_height))

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # Shooting bullets
    if keys[pygame.K_SPACE]:
        if shoot_cooldown == 0:
            shoot_cooldown = SHOOT_COOLDOWN
            player_center_x = player_pos[0] + player_width // 2
            player_center_y = player_pos[1] + player_height // 2
            bullet_angle = math.atan2(my - player_center_y, mx - player_center_x)
            bullets.append([player_center_x, player_center_y, bullet_angle])

    # Update bullet positions
    new_bullets = []
    for bullet in bullets:
        bx, by, angle = bullet
        bx += 10 * math.cos(angle)
        by += 10 * math.sin(angle)
        if 0 <= bx <= WIDTH and 0 <= by <= HEIGHT:
            new_bullets.append([bx, by, angle])
        if is_collision(enemy_pos, (bx, by)):      
            enemy_width, enemy_height = enemy_size
            enemy_pos = [random.randint(0, WIDTH - enemy_width), random.randint(0, HEIGHT - enemy_height)]
    bullets = new_bullets

    # Move enemy
    enemy_pos = move_enemy(player_pos, enemy_pos)

    # Drawing
    screen.blit(background_image, (0, 0))  # Draw the background image
    draw_player(player_pos)
    for bullet in bullets:
        draw_bullet((int(bullet[0]), int(bullet[1])))
    draw_enemy(enemy_pos)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()