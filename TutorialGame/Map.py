import pygame, csv, os

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def TileMap():
        def __init__(self, filename, spritesheet):
            self.tile_size = 16
            self.start_x, self.start_y = 0, 0
            self.spritesheet = 
