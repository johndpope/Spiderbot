import pygame
import threading

import numpy as np

from robot import Robot


class Field(pygame.sprite.Sprite):
    """
    This class describes a single field on the playingfied
    It will change its color according to what happens
    If it is a queens field, then the color is black, and nothing else happens
    If it is a food field, then the color is green, and nothing else happens
    If a robot is inside the field, it may leave a scent
    Scents decay over time
    """
    # color constants
    WHITE = (255, 255, 255)
    BRIGHT = (200, 200, 200)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 160, 0)
    VIOLET = (176, 0, 255)

    def __init__(self, x, y, width, height, color, scent_decay_time=0.5,
                 scent_decay_amount=0.05):
        """
        :param x: the x position of the field
        :param y: the y position of the field
        :param width: the width of the field
        :param height: the height of the field
        :param color: the color of the field
        :param scent_decay_time: time between two scent decay events
        :param scent_decay_amount: amount by which scent magnitude is decreased in each step
        """
        # TODO: bewegliches Ziel (Feind der sich bewegt)
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        # if this is a queen or green field then set the field to protected, otherwise not
        self.protected = (self.color in [self.GREEN, self.BLACK])
        self.width = width
        self.height = height
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.scent_decay_time = scent_decay_time
        self.scent_decay_amount = scent_decay_amount

        self.scent_color = None
        self.scent_magnitude = 0

        self.robot_is_inside = False

        # This thread starts running if a robot enters the field, so that the decay of the color starts
        # => the "color" is equvalent to the "scent"
        self.scent_t = threading.Thread(target=self.scent)
        self.scent_stop = threading.Event()

    # helper functions for the collision finding
    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y

    def get_rect(self):
        return self.rect

    def get_bottom(self):
        return self.rect.bottom

    def get_top(self):
        return self.rect.top

    def get_left(self):
        return self.rect.left

    def get_right(self):
        return self.rect.right

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height

    def check_if_robot_inside(self, robots):
        """
        Check if a robot is inside the field, and if so set the color and start the scent thread

        :param robots: the Group of robots the camera found
        :param robot_mutex: lock object for thread safety
        :return: boolean if a robot is inside the field
        """
        # type: (pygame.sprite.Group(Robot)) -> bool

        collisions = pygame.sprite.spritecollide(self, robots, False)
        if not collisions:
            self.robot_is_inside = False
            return False
        # TODO this case should be handled
        if len(collisions) > 1:
            raise ValueError('More than 1 robot in this field!')
        scent = collisions[0].is_releasing_scent()
        if scent is not None and not self.protected:
            if not self.robot_is_inside:
                self.add_scent(scent)
                self.start_scent(scent)
                self.robot_is_inside = True
        return True

    def set_color(self, color):
        """Set the color of the field."""
        self.color = color

    def scent(self):
        """Thread to manage the scent on this field"""
        while (not self.scent_stop.wait(self.scent_decay_time)
               and self.color != self.WHITE):
            if not self.robot_is_inside:
                self.decrease_scent_magnitude()
        self.color = self.WHITE
        self.scent_magnitude = 0
        self.scent_color = None
        print "Thread is dead"

    def stop_scent(self):
        self.scent_stop.set()

    def update_color(self):
        """Updates the color of the field according to current scent parameters."""
        if self.scent_color == 'orange':
            color = np.array(Field.ORANGE)
        elif self.scent_color == 'blue':
            color = np.array(Field.BLUE)
        else:
            raise ValueError('scent_color %s unknown' % self.scent_color)
        self.color = tuple((1 - self.scent_magnitude) * np.array(Field.WHITE)
                           + self.scent_magnitude * color)

    def increase_scent_magnitude(self):
        """Increases the scent magnitude."""
        self.scent_magnitude += (1 - self.scent_magnitude) / 2.0
        self.update_color()

    def decrease_scent_magnitude(self):
        """Decreases the scent magnitude."""
        self.scent_magnitude = max(
            0, self.scent_magnitude - self.scent_decay_amount)
        self.update_color()

    def add_scent(self, scent):
        """Adds scent to current scent."""
        if self.scent_color == scent:
            self.increase_scent_magnitude()
        elif self.scent_color == 'orange' and scent == 'blue':
            self.scent_color = 'blue'
            self.scent_magnitude = 0
            self.increase_scent_magnitude()
        elif self.scent_color == 'blue' and scent == 'orange':
            pass
        elif self.scent_color is None:
            self.scent_color = scent
            self.increase_scent_magnitude()
        else:
            raise NotImplementedError('This should never happen.')

    def start_scent(self, scent):
        """
        We make some checks, and if they hold, the scent thread is started

        :param scent: scent that is released by current robot
        :return: None
        """


        try:
            if not self.scent_t.is_alive():
                self.scent_t.start()
        except RuntimeError:
            del self.scent_t
            self.scent_t = threading.Thread(target=self.scent)
            self.scent_t.start()

    @staticmethod
    def robot_picks_up_stuff(colliding_robots):
        print "robot picks stuff up"
        for index in range(len(colliding_robots)):
            colliding_robots.pop(index).carries_stuff = True

    @staticmethod
    def robot_drops_stuff(colliding_robots):
        for index in range(len(colliding_robots)):
            colliding_robots.pop(index).carries_stuff = False
