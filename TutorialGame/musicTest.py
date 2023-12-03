import pygame
pygame.init()

# Set up the screen and player
screen = pygame.display.set_mode((1920,960))
background = pygame.transform.scale(pygame.image.load("Sprites/Maps/blue.png").convert(), (1920,960)) 
player = pygame.Rect(100, 100, 50, 50) # The player as a rectangle
boundary = pygame.Rect(100, 100, 900, 900) # The boundary rectangle

# Handle music
pygame.mixer.init()
pygame.mixer.music.load("surreal_sippin.mp3")
pygame.mixer.music.play(-1) # Loop indefinitely


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    speed = 1 # Speed of the player

    # Move the player
    if keys[pygame.K_LEFT]:
        player.x -= speed
        if player.left < boundary.left: # Check left boundary
            player.left = boundary.left

    if keys[pygame.K_RIGHT]:
        player.x += speed
        if player.right > boundary.right: # Check right boundary
            player.right = boundary.right

    if keys[pygame.K_UP]:
        player.y -= speed
        if player.top < boundary.top: # Check top boundary
            player.top = boundary.top

    if keys[pygame.K_DOWN]:
        player.y += speed
        if player.bottom > boundary.bottom: # Check bottom boundary
            player.bottom = boundary.bottom

    # Drawing
    screen.blit(background, (0, 0))
    pygame.draw.rect(screen, (255, 0, 0), player) # Draw the player
    pygame.draw.rect(screen, (255, 255, 255), boundary, 2) # Draw the boundary

    pygame.display.flip()

pygame.quit()
