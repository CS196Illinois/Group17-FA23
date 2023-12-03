import pygame
from sys import exit
import math
from NewSettings import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.transform.scale(pygame.image.load("Sprites/Maps/blue.png").convert(), (1280,720)) 
boundary = pygame.Rect(67, 65, 1147, 593)

pygame.display.set_caption("Top_Down_Shooter")
clock = pygame.time.Clock()

font = pygame.font.Font("PublicPixel.ttf", 20)
small_font = pygame.font.Font("PublicPixel.ttf", 15)
title_font = pygame.font.Font("PublicPixel.ttf", 60)
score_font = pygame.font.Font("PublicPixel.ttf", 50)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("Sprites/Characters/character_main.png").convert_alpha(), 0, PLAYER_SIZE)
        self.original_image = self.image
        self.base_player_image = self.image
        self.health = PLAYER_HEALTH

        self.hitbox_rect = self.base_player_image.get_rect(center = self.pos)
        self.rect = self.hitbox_rect.copy()
        self.speed = PLAYER_SPEED
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)


    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coords[0] - WIDTH // 2)
        self.y_change_mouse_player = (self.mouse_coords[1] - HEIGHT // 2)
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center = self.hitbox_rect.center)

    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed

        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)
        
        # Calculate the new position based on user input
        new_x = self.pos.x + self.velocity_x
        new_y = self.pos.y + self.velocity_y

        self.pos.x = new_x
        self.pos.y = new_y

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Laser(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            screen.blit(self.image, self.rect)  
            laser_group.add(self.bullet)
            all_sprites_group.add(self.bullet)

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        bullet_hits = pygame.sprite.spritecollide(self, acid_group, True)  # Detect collisions and remove bullets
        if bullet_hits:
            self.health -= 0.01  # Remove the enemy when hit by a bullet
        
        enemy_hits = pygame.sprite.spritecollide(self, enemy_group, False)
        if enemy_hits:
            self.health -= 0.01

        if self.health == 0:
            self.kill()

class Spitter(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Sprites/Mobs/mob_spitter.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)
        self.original_image = self.image  # Store the original image for rotation

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.health = SPITTER_HEALTH

        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = SPITTER_SPEED

        self.position = pygame.math.Vector2(position)
        self.shoot_timer = 0
        self.shoot_interval = 60  # Shooting interval in ticks

    def hunt_player(self):
        player_vector = pygame.math.Vector2(player.hitbox_rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
            self.angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            
            if self.shoot_timer >= self.shoot_interval:
                self.enemy_shoot()  # Call the enemy_shoot method when facing the player
                self.shoot_timer = 0
            else:
                self.shoot_timer += 1
        else:
            self.direction = pygame.math.Vector2()

        self.velocity = self.direction * self.speed
        self.position += self.velocity

        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()

    def enemy_shoot(self):
        # Create a new bullet at the enemy's position and angle
        enemy_bullet = Acid(self.rect.centerx, self.rect.centery, self.angle)
        all_sprites_group.add(enemy_bullet, acid_group)

    def handle_collision(self, player):
        for enemy in enemy_group:
            if self.rect.colliderect(player.rect):
                separation_vector = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(player.rect.center)
                
                # Check if the separation_vector's length is greater than a small tolerance
                if separation_vector.length() > 1:  # You can adjust the tolerance as needed
                    separation_vector.normalize_ip()
                    separation_vector *= self.speed

                    # Move the enemy away from the player
                    self.rect.x += separation_vector.x
                    self.rect.y += separation_vector.y

    def update(self):
        self.hunt_player()

        self.handle_collision(player)

        # Check for collisions with bullets
        bullet_hits = pygame.sprite.spritecollide(self, laser_group, True)  # Detect collisions and remove bullets
        if bullet_hits:
            self.health -= 1  # Remove the enemy when hit by a bullet

        if self.health == 0:
            self.kill()

class Jumper(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Sprites/Mobs/mob_jumper.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.5)
        self.original_image = self.image
        self.slide_timer = 0

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.health = JUMPER_HEALTH

        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = JUMPER_SPEED
        self.movement_interval = MOVEMENT_INTERVAL
        self.movement_timer = 0

        self.position = pygame.math.Vector2(position)

    def move(self, speed):
        self.velocity = self.direction * speed

    def update_slide_timer(self):
        if self.slide_timer > 0:
            self.slide_timer -= 1

    def hunt_player(self):
        player_vector = pygame.math.Vector2(player.hitbox_rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
            self.angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.direction = pygame.math.Vector2()

        # Check if sliding is allowed and the slide timer is not active
        if self.slide_timer <= 0:
            self.move(self.speed)
        else:
            self.velocity *= 0  # Stop movement during slide cooldown

        self.position += self.velocity  # Update position even during slide cooldown

        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y


    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()
    
    def handle_collision(self, player):
        for enemy in enemy_group:
            if self.rect.colliderect(player.rect):
                separation_vector = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(player.rect.center)
                
                # Check if the separation_vector's length is greater than a small tolerance
                if separation_vector.length() > 0.001:  # You can adjust the tolerance as needed
                    separation_vector.normalize_ip()
                    separation_vector *= self.speed

                    # Move the enemy away from the player
                    self.rect.x += separation_vector.x
                    self.rect.y += separation_vector.y

    def update(self):
        self.hunt_player()

        self.handle_collision(player)

        # Check for collisions with bullets
        bullet_hits = pygame.sprite.spritecollide(self, laser_group, True)  # Detect collisions and remove bullets
        if bullet_hits:
            self.health -= 1  # Remove the enemy when hit by a bullet

        if self.health == 0:
            self.kill()

        self.update_slide_timer()

        # Update sprite position only if not sliding
        if self.slide_timer <= 0:
            self.position += self.velocity

        # Update sprite position
        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

        # Check if it's time to slide
        if self.movement_timer <= 0:
            #self.slide()
            self.movement_timer = self.movement_interval
        else:
            self.movement_timer -= 1

class Gripper(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Sprites/Mobs/mob_gripper.png")
        self.image = pygame.transform.rotozoom(self.image, 0, 1)
        self.original_image = self.image

        self.rect = self.image.get_rect()
        self.rect.center = position
        self.position = pygame.math.Vector2(position)
        self.direction = pygame.math.Vector2()
        self.speed = GRIPPER_SPEED

        self.health = GRIPPER_HEALTH

    def self_rotation(self):
        self.x_vector = (player.hitbox_rect.left - self.rect.left)
        self.y_vector = (player.hitbox_rect.top - self.rect.top)

        self.angle = math.degrees(math.atan2(self.y_vector, self.x_vector))
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center = self.rect.center)

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()

    def hunt_player(self):
        player_vector = pygame.math.Vector2(player.hitbox_rect.center)
        self_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, self_vector)

        if distance > 0:
            self.direction = (player_vector - self_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()

        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

    def handle_collision(self, player):
        if self.rect.colliderect(player.hitbox_rect):
            self.speed = 0
            self.rect.left = player.hitbox_rect.left
            self.rect.top = player.hitbox_rect.top
        else:
            self.speed = 3

    def update(self):
        self.hunt_player()
        self.self_rotation()
        self.handle_collision(player)

        bullet_hits = pygame.sprite.spritecollide(self, laser_group, True)
        if bullet_hits:
            self.health -= 1
        
        if self.health == 0:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("Sprites/Bullets/bullet_laser.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, LASER_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = LASER_SPEED
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = LASER_LIFETIME
        self.spawn_time = pygame.time.get_ticks()

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def update(self):
        self.bullet_movement()

class Acid(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("Sprites/Bullets/bullet_acidspit.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, ACID_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = ACID_SPEED
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = ACID_LIFETIME
        self.spawn_time = pygame.time.get_ticks()

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def update(self):
        self.bullet_movement()

class UI(): 
    def __init__(self): 
        self.current_health = 100
        self.maximum_health = 100
        self.health_bar_length = 100
        self.health_ratio = self.maximum_health / self.health_bar_length 
        self.current_colour = None

    def display_health_bar(self): 
        pygame.draw.rect(screen, BLACK, (10, 15, self.health_bar_length * 3, 20)) # black

        if self.current_health >= 75:
            pygame.draw.rect(screen, GREEN, (10, 15, self.current_health * 3, 20)) # green    
            self.current_colour = GREEN
        elif self.current_health >= 25:
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

    def update(self): 
        self.display_health_bar()
        self.display_health_text()


all_sprites_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
acid_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

player = Player()
spitter = Spitter((SPITTER_START_X, SPITTER_START_Y))
jumper = Jumper((JUMPER_START_X, JUMPER_START_Y))
gripper = Gripper((GRIPPER_START_X, GRIPPER_START_Y))

ui = UI()

all_sprites_group.add(player)
all_sprites_group.add(spitter)
all_sprites_group.add(jumper)
all_sprites_group.add(gripper)


while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(background, (0, 0))
    screen.blit(player.image, player.rect)
    screen.blit(spitter.image, spitter.rect)
    screen.blit(gripper.image, gripper.rect)
    screen.blit(jumper.image, jumper.rect)
    ui.update()
    all_sprites_group.update()
    laser_group.update()
    pygame.draw.rect(screen, "red", player.hitbox_rect, width = 2)
    pygame.draw.rect(screen, "yellow", player.rect, width = 2)

    pygame.display.update()
    clock.tick(FPS)