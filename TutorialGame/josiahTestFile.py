import pygame
import sys
from sys import exit
import math
import random
from NewSettings import *

pygame.init()

# Screen dimensions and setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background_image = pygame.transform.scale(pygame.image.load('Sprites/Maps/blue.png').convert(), (1280,720))
pygame.display.set_caption("Rectangle and Triangle Game")

# Load Player
player_image = pygame.image.load('Sprites/Characters/character_main.png')
player_size = player_image.get_size() 

def get_angle_to_mouse(player_pos, mouse_pos):
    dx, dy = mouse_pos[0] - (player_pos[0] + player_size[0] // 2), mouse_pos[1] - (player_pos[1] + player_size[1] // 2)
    return math.degrees(math.atan2(-dy, dx)) - 90

def draw_player(screen, image, position, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=(position[0] + player_size[0] // 2, position[1] + player_size[1] // 2))
    screen.blit(rotated_image, new_rect.topleft)

# Load other Images
bullet_image = pygame.image.load('Sprites/Bullets/bullet_laser.png')
enemy_image = pygame.image.load('Sprites/Mobs/mob_spitter.png')


# Player setup
player_size = player_image.get_size()
player_pos = [WIDTH//2, HEIGHT//2]
player_speed = 5

# Crate setup
crate_image = pygame.image.load('Sprites/Crates/crate_yellow.png')
object_size = crate_image.get_size()

# Bullet setup
bullet_size = bullet_image.get_size()
bullets = []

# Enemy setup
enemy_size = enemy_image.get_size()
enemy_pos = [random.randint(0, WIDTH-enemy_size[0]), random.randint(0, HEIGHT-enemy_size[1])]
enemy_speed = 2
shoot_cooldown = 0

def draw_bullet(position):
    screen.blit(bullet_image, position)

def draw_enemy(position):
    screen.blit(enemy_image, position)

def move_enemy(player_pos, enemy_pos):
    angle = math.atan2(player_pos[1] - enemy_pos[1], player_pos[0] - enemy_pos[0])
    enemy_pos[0] += enemy_speed * math.cos(angle)
    enemy_pos[1] += enemy_speed * math.sin(angle)
    return enemy_pos

num_objects = 8
objects = []
while len(objects) < num_objects:
    new_pos = (random.randint(0, WIDTH - object_size[0]), random.randint(0, HEIGHT - object_size[1]))
    if not any(pygame.Rect(new_pos, object_size).colliderect(pygame.Rect(obj, object_size)) for obj in objects):
        objects.append(new_pos)

def draw_object(position):
    screen.blit(crate_image, position)

def is_collision_with_crate(new_player_pos, crate_pos, crate_size):
    player_rect = pygame.Rect(new_player_pos, player_size)
    crate_rect = pygame.Rect(crate_pos, crate_size)
    return player_rect.colliderect(crate_rect)

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
    new_player_pos = player_pos.copy()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        new_player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        new_player_pos[0] += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        new_player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        new_player_pos[1] += player_speed

    if not any(is_collision_with_crate(new_player_pos, obj, object_size) for obj in objects):
        player_pos = new_player_pos

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
    # Calculate rotation angle and draw player
    player_angle = get_angle_to_mouse(player_pos, (mx, my))
    draw_player(screen, player_image, player_pos, player_angle)
    for obj in objects:
        draw_object(obj)
    for bullet in bullets:
        draw_bullet((int(bullet[0]) - 29, int(bullet[1]) - 30))
    draw_enemy(enemy_pos)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()