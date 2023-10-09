import pygame
from sys import exit
import math

pygame.init()

#### Variables

# Game Setup
WIDTH = 1281
HEIGHT = 720
FPS = 60

# Player settings
PLAYER_START_X = 400
PLAYER_START_Y = 500
PLAYER_SIZE = 0.25
PLAYER_SPEED = 8

# Creating the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Shooter") # Sets name of window, not really important. Without it the window is named "pygame window"
clock = pygame.time.Clock() # Not sure what this does tbh

# Creates background image of the .jpg I downloaded off google, ".convert()" apparently makes the image better quality. 
# pygame.image.load() returns the image file inputted.
# pygame.transform.scale(image, scale variables) scales the image according to the inputted variables, note the syntax of how width and height have to be in parentheses.
background = pygame.transform.scale(pygame.image.load("grass_background.jpg").convert(), (WIDTH, HEIGHT)) 


class Player(pygame.sprite.Sprite):
    # constructor I assume, similar to "public Player(image im, Vector2 pos, int speed) { }" in java.
    def __init__(self):
        super().__init__() # not sure what the super class. Code runs without this line but maybe it's helpful in the future.
        self.image = pygame.transform.rotozoom(pygame.image.load("player.png").convert_alpha(), 0, PLAYER_SIZE)
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.speed = PLAYER_SPEED

    # this method is continuously called by the playerUpdate() method below. 
    def userInput(self):
        # x and y velocities are continuously set to 0 so that if you're only moving up if you're currently pressing "w".
        self.velocity_x = 0 
        self.velocity_y = 0

        keys = pygame.key.get_pressed() # stores which keys are being pressed at this instant.

        if keys[pygame.K_w]: # K_w is if Key "w" is pressed. Same goes for the following.
            self.velocity_y = -self.speed # negative y velocity means going up(weird).Positive goes down.
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed # negative x velocity means going left(normal). Positive goes right.
        if keys[pygame.K_s]:
            self.velocity_y = self.speed 
        if keys[pygame.K_d]:
            self.velocity_x = self.speed

        # This if statement is for diagonals. Without it, you go super fast when moving diagonally because x and y velocity are both non-0 values.
        if self.velocity_x != 0 and self.velocity_y != 0: 
            self.velocity_x /= math.sqrt(2) # Pythagorean theorem. In math class you learn that in a 45, 45, 90 triangle, the side values are x, x, and x(sqrt(2))
            self.velocity_y /= math.sqrt(2)

    # continuously changes position of Player object by x and y velocity.
    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)

    # this method is continuously called in the main method. It just continuously called userInput() and move() methods.
    def playerUpdate(self):
        self.userInput()
        self.move()

# main method starts here. Creates a player object and runs the while True forever.
player = Player()

while True:
    for event in pygame.event.get(): 
        # pygame.event is an event queue, probably stored as an array. Each iteration, it tests to see if you closed the window. If you close the window, this action is stored in event.type.
        # This loop will quit everything if the close window action is stored in event.type.
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # blit is how you put an image variable onto the window. the function call is blit(image, Vector2). Vector2 is a pygame object.
    screen.blit(background, (0, 0))
    screen.blit(player.image, player.pos)
    player.playerUpdate()
    
    pygame.display.update() # without this, you'll get a black screen.
    clock.tick(FPS) # idk lol