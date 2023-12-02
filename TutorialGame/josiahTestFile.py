import pygame
pygame.init()

# Set up the screen, sprite, and walls
screen = pygame.display.set_mode((800, 600))
sprite = pygame.Rect(100, 100, 50, 50) # Your sprite as a rectangle
walls = [pygame.Rect(300, 300, 200, 50), pygame.Rect(50, 400, 50, 150)] # List of walls

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    speed = 1 # Change this value to make the sprite move faster or slower
    new_position = sprite.copy()

    # Move the sprite
    if keys[pygame.K_LEFT]:
        new_position.x -= speed
    if keys[pygame.K_RIGHT]:
        new_position.x += speed
    if keys[pygame.K_UP]:
        new_position.y -= speed
    if keys[pygame.K_DOWN]:
        new_position.y += speed

    # Collision detection
    for wall in walls:
        if new_position.colliderect(wall):
            break
    else:
        sprite = new_position

    # Drawing
    screen.fill((0, 0, 0)) # Clear screen
    pygame.draw.rect(screen, (255, 0, 0), sprite) # Draw the sprite
    for wall in walls:
        pygame.draw.rect(screen, (0, 255, 0), wall) # Draw the walls

    pygame.display.flip()

pygame.quit()