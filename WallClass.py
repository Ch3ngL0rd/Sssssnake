import pygame
class Wall:
    def __init__(self,colour,position):
        self.colour = colour
        self.position = position

    def render(self,screen,block_size):
        pygame.draw.rect(screen, self.colour, (self.position[0]*block_size,self.position[1]*block_size,block_size,block_size))