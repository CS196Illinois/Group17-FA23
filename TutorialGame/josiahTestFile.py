import pygame
pygame.init()

# Set up the screen and player
screen = pygame.display.set_mode((1280,720))
background = pygame.transform.scale(pygame.image.load("Sprites/Maps/blue.png").convert(), (1280,720)) 
player = pygame.Rect(100, 100, 50, 50) # The player as a rectangle
boundary = pygame.Rect(43, 48, 1195, 625) # The boundary rectangle
sprite_image = pygame.image.load("Sprites/Crates/crate_yellow.png")  # Replace "sprite.png" with your sprite image file
sprite_rect = sprite_image.get_rect()
crate = pygame.Rect((600, 300, 64, 64))


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
        elif player.left < crate.left:
            player.left = crate.left

    if keys[pygame.K_RIGHT]:
        player.x += speed
        if player.right > boundary.right: # Check right boundary
            player.right = boundary.right
        elif player.right > crate.right:
            player.right = crate.right

    if keys[pygame.K_UP]:
        player.y -= speed
        if player.top < boundary.top: # Check top boundary
            player.top = boundary.top
        elif player.top < crate.top:
            player.top = crate.top

    if keys[pygame.K_DOWN]:
        player.y += speed
        if player.bottom > boundary.bottom: # Check bottom boundary
            player.bottom = boundary.bottom
        elif player.bottom > crate.bottom:
            player.bottom = crate.bottom

    # Drawing
    screen.blit(background, (0, 0))
    pygame.draw.rect(screen, (255, 0, 0), player) # Draw the player
    pygame.draw.rect(screen, (255, 255, 255), boundary, 2) # Draw the boundary

    screen.blit(player)

    # Drawing Crate
    pygame.draw.rect(screen, (255, 0, 0), crate)
    # Draw the sprite over the rectangle
    sprite_position = (crate.centerx - sprite_rect.width // 2, crate.centery - sprite_rect.height // 2)
    screen.blit(sprite_image, sprite_position)

    pygame.display.flip()

pygame.quit()
