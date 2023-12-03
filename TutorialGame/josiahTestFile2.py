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

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("Character/player.png").convert_alpha(), 0, PLAYER_SIZE)
        self.original_image = self.image
        self.flicker_image = self.image.copy()
        self.base_player_image = self.image
        self.flicker_timer = 0
        self.flicker_duration = FLICKER_DURATION
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

        if self.pos.x < boundary.left: # Check left boundary
            self.pos.x = boundary.left

        if self.pos.x > boundary.right: # Check right boundary
            self.pos.x = boundary.right
        
        if self.pos.y < boundary.top: # Check top boundary
            self.pos.y = boundary.top
        
        if self.pos.y > boundary.bottom: # Check bottom boundary
            self.pos.y = boundary.bottom

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
            laser_group.add(self.bullet)
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

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.player_rotation()
        self.user_input()
        self.move()
        self.handle_collision(enemy_group)  # Check and resolve collisions with enemies

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        bullet_hits = pygame.sprite.spritecollide(self, acid_group, True)  # Detect collisions and remove bullets
        if bullet_hits:
            self.health -= 0.01  # Remove the enemy when hit by a bullet
            self.flicker_timer = self.flicker_duration  # Start flickering when hit
        
        enemy_hits = pygame.sprite.spritecollide(self, enemy_group, False)
        if enemy_hits:
            self.health -= 0.01
            self.flicker_timer = self.flicker_duration

        if self.health == 0:
            self.kill()
        if self.flicker_timer > 0:
            # Flicker the sprite by changing its alpha (transparency)
            if self.flicker_timer % 2 == 0:
                self.image.set_alpha(0)  # Hide the sprite on even frames
            else:
                self.image = self.flicker_image  # Restore the original image on odd frames

            self.flicker_timer -= 1
        else:
            self.image = self.original_image

class Spitter(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Sprites/Mobs/mob_spitter.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)
        self.original_image = self.image  # Store the original image for rotation
        self.flicker_image = self.image.copy()  # Create a copy for flickering effect

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.health = SPITTER_HEALTH
        self.flicker_timer = 0
        self.flicker_duration = FLICKER_DURATION  # Adjust the duration as needed

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
            self.flicker_timer = self.flicker_duration  # Start flickering when hit

        if self.health == 0:
            self.kill()
        if self.flicker_timer > 0:
            # Flicker the sprite by changing its alpha (transparency)
            if self.flicker_timer % 2 == 0:
                self.image.set_alpha(25)  # Hide the sprite on even frames
            else:
                self.image = self.flicker_image  # Restore the original image on odd frames

            self.flicker_timer -= 1
        else:
            self.image = self.original_image

"""class Jumper(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Sprites/Mobs/mob_jumper.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.5)
        self.original_image = self.image
        self.flicker_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.health = JUMPER_HEALTH
        self.flicker_timer = 0
        self.flicker_duration = FLICKER_DURATION

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
            self.hurt_timer = self.hurt_duration  # Start flickering when hit

        if self.health == 0:
            self.kill()

        if self.hurt_timer > 0:
            # Flicker the sprite by changing its alpha (transparency)
            if self.hurt_timer % 2 == 0:
                self.image.set_alpha(0)  # Hide the sprite on even frames
            else:
                self.image = self.hurt_image  # Restore the original image on odd frames

            self.hurt_timer -= 1
        else:
            self.image = self.original_image

        self.update_slide_timer()

        # Update sprite position only if not sliding
        if self.slide_timer <= 0:
            self.position += self.velocity

        # Update sprite position
        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

        # Check if it's time to slide
        if self.movement_timer <= 0:
            self.slide()
            self.movement_timer = self.movement_interval
        else:
            self.movement_timer -= 1"""

class Gripper(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Sprites/Mobs/mob_gripper.png")
        self.image = pygame.transform.rotozoom(self.image, 0, 1)
        self.original_image = self.image
        self.flicker_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = position
        self.position = pygame.math.Vector2(position)
        self.direction = pygame.math.Vector2()
        self.speed = GRIPPER_SPEED

        self.health = GRIPPER_HEALTH
        self.flicker_timer = 0
        self.flicker_duration = FLICKER_DURATION

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
            self.speed = GRIPPER_SPEED

    def update(self):
        self.hunt_player()
        self.self_rotation()
        self.handle_collision(player)

        bullet_hits = pygame.sprite.spritecollide(self, laser_group, True)
        if bullet_hits:
            self.health -= 1
            self.flicker_timer = self.flicker_duration
        
        if self.flicker_timer > 0:
            if self.flicker_timer % 2 == 0:
                self.image.set_alpha(0)
            else:
                self.image = self.flicker_image
            
            self.flicker_timer -= 1
        else:
            self.image = self.original_image
        
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

class bulletSpeedPowerUp(pygame.sprite.Sprite):
    



all_sprites_group = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
acid_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

player = Player()
"""spitter = Spitter((SPITTER_START_X, SPITTER_START_Y))
jumper = Jumper((JUMPER_START_X, JUMPER_START_Y))
gripper = Gripper((GRIPPER_START_X, GRIPPER_START_Y))"""


all_sprites_group.add(player)

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(background, (0, 0))
    screen.blit(player.image, player.rect)
    player.update()

    all_sprites_group.update()
    pygame.draw.rect(screen, "red", player.hitbox_rect, width = 2)
    pygame.draw.rect(screen, "yellow", player.rect, width = 2)

    pygame.display.update()
    clock.tick(FPS)