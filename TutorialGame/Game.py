import pygame
from sys import exit
import math
from settings import *

pygame.init()

# window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top_Down_Shooter")
clock = pygame.time.Clock()

MAP_WIDTH = 3024 #twice the screen width. this is just a placement number idk how big our map will be
MAP_HEIGHT = 1832 #twice the screen height. also a placement number.

# images
background = pygame.transform.rotozoom(pygame.image.load("Background/Skeld.png").convert(), 0, MAP_SIZE)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load("Character/player.png").convert_alpha(), 0, PLAYER_SIZE)
        self.base_player_image = self.image
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
        self.rect=self.image.get_rect(center = self.hitbox_rect.center)

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

        # Ensure the player doesn't go past the screen boundaries
        new_x = max(0, min(new_x, MAP_WIDTH - self.rect.width))
        new_y = max(0, min(new_y, MAP_HEIGHT - self.rect.height))

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
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            all_sprites_group.add(self.bullet)



    def move(self):
        #self.velocity_x = max(0, min(self.velocity_x, WIDTH))
       # self.velocity_y = max(0, min(self.velocity_y, HEIGHT))
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox_rect.center = self.pos
        self.rect.center = self.hitbox_rect.center

    def update(self):
        self.user_input()
        self.move()
        self.player_rotation()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("Bullets/1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__(enemy_group, all_sprites_group)
        self.image = pygame.image.load("Enemies/necromancer.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = ENEMY_SPEED

        self.position = pygame.math.Vector2(position)

    def hunt_player(self):
        player_vector = pygame.math.Vector2(player.hitbox_rect.center)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
        else:
            self.direction = pygame.math.Vector2()

        self.velocity = self.direction * self.speed
        self.position += self.velocity

        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

    def get_vector_distance(self, vector_1, vector_2):
        return (vector_1 - vector_2).magnitude()
    
    def update(self):
        self.hunt_player()


class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        self.floor_rect = background.get_rect(topleft = (0, 0))

    def custom_draw(self):
        self.offset.x = player.rect.centerx - (WIDTH // 2)
        self.offset.y = player.rect.centery - (HEIGHT // 2)
        self.offset.x = max(0, min(MAP_WIDTH - WIDTH, self.offset.x))
        self.offset.y = max(0, min(MAP_HEIGHT - HEIGHT, self.offset.y))

        floor_offset_pos = self.floor_rect.topleft - self.offset
        screen.blit(background, floor_offset_pos)

        for sprite in all_sprites_group:
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)
    


all_sprites_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

camera = Camera()
player = Player()
necromancer = Enemy((400, 400))


all_sprites_group.add(player)

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(background, (0, 0))
    
    camera.custom_draw()
    all_sprites_group.update()
    # pygame.draw.rect(screen, "red", player.hitbox_rect, width = 2)
    # pygame.draw.rect(screen, "yellow", player.rect, width = 2)

    pygame.display.update()
    clock.tick(FPS)