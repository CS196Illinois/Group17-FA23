import pygame
from sys import exit
import math
from settings import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top_Down_Shooter")
clock = pygame.time.Clock()