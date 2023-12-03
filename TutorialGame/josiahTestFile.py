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
boundary = pygame.Rect(42, 60, 1148, 563)
pygame.display.set_caption("Top Down Shooter")

# Load Player
player_image = pygame.transform.scale(pygame.image.load('Sprites/Characters/character_main.png'), (50,40))
player_size = player_image.get_size()
player_health = 100

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

# Load other Images
bullet_image = pygame.image.load('Sprites/Bullets/bullet_laser.png')



# Player setup
player_size = player_image.get_size()
player_pos = [WIDTH//2, HEIGHT//2]
player_speed = 5

# Crate setup
crate_image = pygame.transform.scale(pygame.image.load('Sprites/Crates/crate_yellow.png'),(50,50))
crate_size = crate_image.get_size()

# Bullet setup
bullet_size = list(bullet_image.get_size())
bullets = []
enemy_bullets = []  # List to store enemy bullets

# Enemy setup
enemy_image = pygame.transform.scale(pygame.image.load('Sprites/Mobs/mob_spitter.png'), (100,100))
enemy_size = enemy_image.get_size()
enemy_pos = [random.randint(0, WIDTH-enemy_size[0]), random.randint(0, HEIGHT-enemy_size[1])]
enemy_speed = 2
shoot_cooldown = 0
enemy_shoot_cooldown = 0

enemy_health = 100

def get_angle_to_target(source_pos, target_pos, source_size):
    dx = target_pos[0] - (source_pos[0] + source_size[0] // 2)
    dy = target_pos[1] - (source_pos[1] + source_size[1] // 2)
    return math.degrees(math.atan2(-dy, dx)) - 90

def draw_rotated_image(screen, image, position, angle, size):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=(position[0] + size[0] // 2, position[1] + size[1] // 2))
    screen.blit(rotated_image, new_rect.topleft)

def draw_bullet(position):
    screen.blit(bullet_image, position)

def move_enemy(player_pos, enemy_pos):
    angle = math.atan2(player_pos[1] - enemy_pos[1], player_pos[0] - enemy_pos[0])
    enemy_pos[0] += enemy_speed * math.cos(angle)
    enemy_pos[1] += enemy_speed * math.sin(angle)
    return enemy_pos

num_crates = 15  # Number of crates
crates = [(random.randint(100, WIDTH - crate_size[0] - 100), random.randint(100, HEIGHT - crate_size[1] - 100)) for _ in range(num_crates)]

def draw_crates(screen, crate_image, crate_positions):
    for pos in crate_positions:
        screen.blit(crate_image, pos)

def draw_crate(position):
    screen.blit(crate_image, position)

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
            pygame.draw.rect(screen, GREEN, (50, 58, self.current_health * 3, 20)) # green    
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

    def display_powerups(self):
        text_powerups = font.render(f"Powerup", True, WHITE)
        screen.blit(text_powerups, (1120, 15))
        pygame.draw.rect(screen, WHITE, (1160, 40, 80, 80), 4) 

    def update(self): 
        self.display_health_bar()
        self.display_health_text()
        self.display_powerups()

ui = UI()

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

    # Keep player in screen bounds
    player_width, player_height = player_size

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # Shooting bullets
    if keys[pygame.K_SPACE]:
        if shoot_cooldown == 0:
            shoot_cooldown = PLAYER_SHOOT_COOLDOWN
            player_center_x = player_pos[0] + player_width // 2
            player_center_y = player_pos[1] + player_height // 2
            bullet_angle = math.atan2(my - player_center_y, mx - player_center_x)
            bullets.append([player_center_x, player_center_y, bullet_angle])

    # Enemy bullets
    if enemy_shoot_cooldown == 0:
        enemy_shoot_cooldown = 3000
        ex, ey = enemy_pos
        player_center_x = player_pos[0] + player_size[0] // 2
        player_center_y = player_pos[1] + player_size[1] // 2
        enemy_bullet_angle = get_angle_to_target(enemy_pos, (player_center_x, player_center_y), enemy_size)
        enemy_bullets.append([ex + enemy_size[0] // 2, ey + enemy_size[1] // 2, enemy_bullet_angle])

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
        bullet_hit_enemy = is_collision((bx, by), bullet_size, enemy_pos, enemy_size)
        if bullet_hit_enemy:
            enemy_health -= 10  # Adjust damage value as needed
            if enemy_health <= 0:
                # Handle enemy defeat (e.g., respawn, increase score)
                pass
        else:
            new_bullets.append(bullet)

        # Remove bullet if it hits a crate or the enemy, or if it goes off-screen
        if not bullet_hit_crate and not bullet_hit_enemy and 0 <= bx <= WIDTH and 0 <= by <= HEIGHT:
            new_bullets.append([bx, by, angle])
        if bullet_hit_enemy:
            # Handle enemy hit (e.g., respawn enemy, increase score, etc.)
            enemy_pos = [random.randint(0, WIDTH - enemy_size[0]), random.randint(0, HEIGHT - enemy_size[1])]
    bullets = new_bullets
    
    # Update enemy bullets
    new_enemy_bullets = []
    for enemy_bullet in new_enemy_bullets:
        ex, ey, angle = enemy_bullet
        enemy_bullet_pos = (ex, ey)
        ex += 10 * math.cos(angle)
        ey += 10 * math.sin(angle)
        # Check collision with crates
        bullet_hit_crate = any(is_collision(enemy_bullet_pos, bullet_size, crate_pos, crate_size) for crate_pos in crates)

        # Check collision with olayer
        bullet_hit_player = is_collision((ex, ey), bullet_size, player_pos, player_size)
        if bullet_hit_player:
            player_health -= 10  # Adjust damage value as needed
            if player_health <= 0:
                # Handle player defeat (e.g., game over logic)
                pass
        else:
            new_enemy_bullets.append(enemy_bullet)

        # Remove bullet if it hits a crate or the enemy, or if it goes off-screen
        if not bullet_hit_crate and not bullet_hit_player and 0 <= ex <= WIDTH and 0 <= ey <= HEIGHT:
            new_enemy_bullets.append([ex, ey, angle])
        if bullet_hit_player:
            # Handle enemy hit (e.g., respawn enemy, increase score, etc.)
            player_health -= 1
    enemy_bullets = new_enemy_bullets

    # Move enemy
    enemy_pos = move_enemy(player_pos, enemy_pos)

    # Drawing
    screen.blit(background_image, (0, 0))  # Draw the background image

    # Draw and rotate enemy to face player
    enemy_angle = get_angle_to_target(enemy_pos, player_pos, enemy_size)
    draw_rotated_image(screen, enemy_image, enemy_pos, enemy_angle, enemy_size)

    # Calculate rotation angle and draw player
    player_angle = get_angle_to_mouse(player_pos, (mx, my))
    ui.update()
    draw_player(screen, player_image, player_pos, player_angle)
    draw_crates(screen, crate_image, crates)

    # Drawing enemy bullets
    for bullet in bullets:
        draw_bullet((int(bullet[0]) - 29, int(bullet[1]) - 30))
    for bullet in enemy_bullets:
        draw_bullet((int(bullet[0]), int(bullet[1])))
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()