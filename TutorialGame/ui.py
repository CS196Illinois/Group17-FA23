from typing import Any, Iterable, Union
import pygame
from sys import exit
import math
from csv import reader
from pygame.sprite import AbstractGroup, Group
from setting import *
from os import walk
import random

pygame.init()

# Creating the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# fonts
font = pygame.font.Font("font/PublicPixel.ttf", 20)
small_font = pygame.font.Font("font/PublicPixel.ttf", 15)
title_font = pygame.font.Font("font/PublicPixel.ttf", 60)
score_font = pygame.font.Font("font/PublicPixel.ttf", 50)

# Loads background images
background = pygame.image.load("background/ground.png").convert()
plain_bg = pygame.image.load("background/black bg.png").convert()


game_active = True
beat_game = False
current_time = 0
level_over_time = 0
ready_to_spawn = False
display_countdown_time = False
first_level = True


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.rotozoom(pygame.image.load("player/0.png").convert_alpha(), 0, PLAYER_SIZE)
        self.base_player_image = self.image

        self.pos = pos
        self.vec_pos = pygame.math.Vector2(pos)
        self.hitbox_rect = self.base_player_image.get_rect(center = pos)
        self.rect = self.hitbox_rect.copy()
        
        self.player_speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0

        self.health = 100
        
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)
    
    def player_turning(self):
        self.mouse_coords = pygame.mouse.get_pos()

        self.x_change_mouse_player = (self.mouse_coords[0] - (WIDTH // 2))
        self.y_change_mouse_player = (self.mouse_coords[1] - (HEIGHT // 2))
        self.angle = int(math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player)))
        self.angle = (self.angle) % 360

        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center = self.hitbox_rect.center)

    def player_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()
        if keys [pygame.K_w]:
            self.velocity_y = -self.player_speed
        if keys [pygame.K_a]:
            self.velocity_x = -self.player_speed
        if keys [pygame.K_s]:
            self.velocity_y = self.player_speed
        if keys [pygame.K_d]:
            self.velocity_x = self.player_speed
        
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x  /= math.sqrt(2)
            self.velocity_y  /= math.sqrt(2)
        
        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()

        else:
            self.shoot = False

        if event.type == pygame.KEYUP:
            if pygame.mouse.get_pressed() == (1, 0, 0):
                self.shoot = False
    
    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def handle_collision(self, enemy_group):
        for enemy in enemy_group:
            if self.rect.colliderect(enemy.rect):
                if pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(enemy.rect.center) == 0:
                    separation_vector = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(enemy.rect.center)
                else:
                # Calculate the separation vector between the player and the enemy
                    separation_vector = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(enemy.rect.center)
                    separation_vector.normalize_ip()
                separation_vector *= self.speed
                

                # Move the player away from the enemy
                self.rect.x += separation_vector.x
                self.rect.y += separation_vector.y

    def get_damage(self, amount):
        if ui.current_health > 0:
            ui.current_health -= amount
            self.health -= amount
            #if ui.current_health > 0:
            #    hurt_sound.play()
            #else:
            #    death_sound.play()
        if ui.current_health <= 0: # dead
            ui.current_health = 0
            self.health = 0
            
        
    def increase_health(self, amount):
        if ui.current_health < ui.maximum_health:
            ui.current_health += amount
            self.health += amount
        if ui.current_health >= ui.maximum_health:
            ui.current_health = ui.maximum_health
            self.health = ui.maximum_health
    

    def update(self):
        self.player_turning()
        self.player_input()
        self.move()
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.shoot:
            self.is_shooting()

class UI(): 
    def __init__(self): 
        self.current_health = 100
        self.maximum_health = 100
        self.health_bar_length = 100
        self.health_ratio = self.maximum_health / self.health_bar_length 
        self.current_colour = None

    def display_health_bar(self): 
        pygame.draw.rect(screen, BLACK, (10, 15, self.health_bar_length * 3, 20)) # black

        if self.current_health >= self.maximum_health * 0.75:
            pygame.draw.rect(screen, GREEN, (10, 15, self.current_health * 3, 20)) # green    
            self.current_colour = GREEN
        elif self.current_health >= self.maximum_health * 0.25:
            pygame.draw.rect(screen, YELLOW, (10, 15, self.current_health * 3, 20)) # yellow
            self.current_colour = YELLOW 
        elif self.current_health >= 0:
            pygame.draw.rect(screen, RED, (10, 15, self.current_health * 3, 20)) # red 
            self.current_colour = RED

        pygame.draw.rect(screen, WHITE, (10, 15, self.health_bar_length * 3, 20), 4) # white border

    def display_health_text(self):
        health_surface = font.render(f"{player.health} / {self.maximum_health}", False, self.current_colour) 
        health_rect = health_surface.get_rect(center = (410, 25))
        screen.blit(health_surface, health_rect)

# wave deleted

# coin
    """def display_coin(self):
        coin_image = pygame.image.load("items/coin/0.png").convert_alpha()
        coin_image = pygame.transform.scale_by(coin_image, 3)
        coin_image_rect = coin_image.get_rect(center = (1162,30))
        coin_text = font.render(f"x {game_stats['coins']}", True, (255,223,91))
        screen.blit(coin_text, (1200, 20))
        screen.blit(coin_image, coin_image_rect)"""
    def display_powerups(self):
        text_powerups = font.render(f"Powerup", True, WHITE)
        screen.blit(text_powerups, (1120, 15))
        pygame.draw.rect(screen, WHITE, (1160, 40, 80, 80), 4)
# countdown deleted

    def display_enemy_count(self):
        text_1 = font.render(f"Enemies: {game_stats['number_of_enemies'][game_stats['current_wave'] - 1] - game_stats['enemies_killed_or_removed']}",True, GREEN)
        screen.blit(text_1, (655, 18))

    def update(self): 
        self.display_health_bar()
        self.display_health_text()
        # self.display_coin()
        self.display_powerups()
        self.display_enemy_count()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("bullet/1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.x_vel = math.cos(self.angle * (2*math.pi/360)) * self.speed
        self.y_vel = math.sin(self.angle * (2*math.pi/360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks() # gets the specific time that the bullet was created
    
    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()
    
    def update(self):
        self.bullet_movement()

# Groups
all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

player = Player((1000, 900))
all_sprites_group.add(player)

ui = UI()

necromancer_image = pygame.image.load("necromancer/sprites/sprite_00.png").convert_alpha()
necromancer_image = pygame.transform.rotozoom(necromancer_image ,0, 1.5)
necromancer_image_rect = necromancer_image.get_rect(center = (190,225))

nightborne_image = pygame.image.load("nightborne/sprites/00.png").convert_alpha()
nightborne_image = pygame.transform.rotozoom(nightborne_image,0,2)
nightborne_image_rect = nightborne_image.get_rect(center = (220,340))

coin_image = pygame.image.load("items/coin/0.png").convert_alpha()
coin_image = pygame.transform.rotozoom(coin_image, 0, 4)
coin_image_rect = coin_image.get_rect(center = (215,540))

start_time = 0

def display_end_screen():
    screen.fill((40,40,40))
    screen.blit(necromancer_image, necromancer_image_rect)
    screen.blit(nightborne_image, nightborne_image_rect)
    screen.blit(coin_image, coin_image_rect)
    if beat_game:
        beat_game_surface = font.render("You beat the game! Thanks for playing!", True, WHITE)
        screen.blit(beat_game_surface, (300, 50))
    else:
        game_over_surface = title_font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_surface, (350, 50))
    text_surface = font.render("> Press 'P' to play again", True, WHITE)
    text_1 = font.render(f"You killed:", True, WHITE)
    text_2 = font.render(f"{game_stats['necromancer_death_count']} x", True, WHITE) 
    text_3 = font.render(f"{game_stats['nightborne_death_count']} x", True, WHITE)
    text_4 = font.render(f"You collected:", True, WHITE)
    text_5 = font.render(f"{game_stats['coins']} x",True, WHITE)
    
    screen.blit(text_surface, (WIDTH / 2 - 70, HEIGHT * 7 / 8))
    screen.blit(text_1, (100, 150))
    screen.blit(text_2, (100, 250))
    screen.blit(text_3, (100, 350))
    screen.blit(text_4, (100, 450))
    screen.blit(text_5, (100, 530))
    score_text_1 = font.render(f"Your score:", False, WHITE)
    score_text_2 = score_font.render(f"{score:,}", False, WHITE)
    screen.blit(score_text_1, (550,150))
    screen.blit(score_text_2, (550,250))

def end_game():
    global game_active 
    game_active = False
"""    for item in items_group:
        item.kill()
    for enemy in enemy_group:
        enemy.kill()
    enemy_group.empty() 
    items_group.empty() """

while True:
    current_time = pygame.time.get_ticks()
    if player.health <= 0:
        end_game()

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if not game_active and keys[pygame.K_p]:
            player.health, ui.current_health = 100, 100
            game_active = True
            game_stats["current_wave"] = 1
            start_time = pygame.time.get_ticks()            
            
            game_stats["necromancer_death_count"] = 0
            game_stats["nightborne_death_count"] = 0
            game_stats["enemies_killed_or_removed"] = 0
            game_stats["coins"] = 0
    
    if game_active:
        screen.blit(plain_bg, (0, 0))
        all_sprites_group.update()
        ui.update()
    

    all_sprites_group.draw(screen)
    all_sprites_group.update()
    # pygame.draw.rect(screen, "red", player.hitbox_rect, width = 2)
    # pygame.draw.rect(screen, "yellow", player.rect, width = 2)

    pygame.display.update()
    clock.tick(FPS)
