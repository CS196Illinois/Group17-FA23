import pygame
import random

pygame.init()

# Set up the screen and player
screen_size = (1280, 720)
screen = pygame.display.set_mode(screen_size)
player = pygame.Rect(100, 100, 50, 50)
boundary = pygame.Rect(50, 50, 700, 500)

# Power-up setup
powerup_image = pygame.image.load("Sprites/Powerups/powerup_gold.png").convert_alpha()
powerup_hit_box = pygame.Rect(random.randint(boundary.left, boundary.right-50), 
                      random.randint(boundary.top, boundary.bottom-50), 50, 50)
powerup_active = False
BULLET_SPEED = 5  # Initial bullet speed

def spawn_powerup():
    global powerup_active
    powerup.x = random.randint(boundary.left, boundary.right-50)
    powerup.y = random.randint(boundary.top, boundary.bottom-50)
    powerup_active = True

# Timing for power-up appearance
POWERUP_TIME = 1000  # Time in milliseconds
next_powerup = pygame.time.get_ticks() + POWERUP_TIME

running = True
while running:
    current_time = pygame.time.get_ticks()

    # Check for power-up spawn
    if current_time >= next_powerup and not powerup_active:
        spawn_powerup()
        next_powerup = current_time + POWERUP_TIME

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement and boundary checking here

    # Check for collision with power-up
    if powerup_active and player.colliderect(powerup):
        BULLET_SPEED += 5  # Increase bullet speed
        powerup_active = False  # Hide power-up

    # Drawing
    screen.fill((0, 0, 0))  # Clear screen
    pygame.draw.rect(screen, (255, 0, 0), player)  # Draw the player
    if powerup_active:
        pygame.draw.rect(screen, (0, 0, 255), powerup)  # Draw the power-up

    pygame.display.flip()

pygame.quit()