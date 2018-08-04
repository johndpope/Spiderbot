import pygame


class Robot(pygame.sprite.Sprite):
    """This class holds the coordinates of a robot and if he carries anything
    The class is derived from Sprite, so that the functionality of collision finding
    with rect is available
    """

    SCENTS = (None, 'orange', 'blue')

    def __init__(self, x, y, width=20, height=20, scent=None):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.carries_stuff = False
        self.scent = None
        self.set_scent(scent)

    def picks_up_stuff(self):
        self.carries_stuff = True

    def puts_down_stuff(self):
        self.carries_stuff = False

    def is_releasing_scent(self):
        return self.scent

    def set_scent(self, scent):
        if scent in Robot.SCENTS:
            self.scent = scent
        else:
            raise ValueError('Given scent %s unknown.' % scent)
