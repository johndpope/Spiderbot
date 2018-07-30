import pygame


class Robot(pygame.sprite.Sprite):
    """This class holds the coordinates of a robot and if he carries anything
    The class is derived from Sprite, so that the functionality of collision finding
    with rect is available
    """

    width = 20
    height = 20

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.carries_stuff = False

    def picks_up_stuff(self):
        self.carries_stuff = True

    def puts_down_stuff(self):
        self.carries_stuff = False
