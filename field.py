import pygame
import threading

import numpy

from robot import Robot


class Field(pygame.sprite.Sprite):
    """
    This class describes a single field on the playingfied
    It will change its color according to what happens
    If it is a queens field, then the color is black, and nothing else happens
    If it is a food field, then the color is green, and nothing else happens
    If a robot enters the field, its color changes, depending on if the robot is carrying anything
    carries stuff -> blue
    carries nothing -> orange

    The color will decay over time, which is configurable
    Also the color will no get stronger if the robot stays in the field. Only when a new robot enters it
    """
    scent_decay_time = 0.5  # the time between two decay events, can be configured to slow or fasten the decay time
    gradient = 5  # This is the amount of color which is taken in every decay time
    scent_increase = -50  # the amount of color which is added when a robot enters the field

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

    def __init__(self, x, y, width, height, color):
        """

        :param x: the x position of the field
        :param y: the y position of the field
        :param width: the width of the field
        :param height: the height of the field
        :param color: the color of the field
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

        # the the color gradient, how much the color changes if a robot enters the field
        self.INCREASE_BLUE = (self.scent_increase, self.scent_increase, 0)
        self.INCREASE_ORANGE = (0, self.scent_increase / 2, self.scent_increase)

        self.robot_is_inside = False
        self.robot_was_previously_inside = False
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

    def is_robot_inside(self, robots):
        """
        Check if a robot is inside the field, and if so set the color and start the scent

        :param robots: the Group of robots the camera found
        :param robot_mutex: lock object for thread safety
        :return: boolean if a robot is inside the field
        """
        # type: (pygame.sprite.Group(Robot)) -> bool

        collision_list = pygame.sprite.spritecollide(self, robots, False)
        if len(collision_list) > 0:
            # Only if the robot enters the field, then the thread to manage the scent on this field starts
            if not self.robot_is_inside:
                if not self.protected:
                    self.start_scent(collision_list)
                # the following will be done differently, but leave it as a reminder
                # else:
                #     if self.color == Field.GREEN:
                #         self.robot_picks_up_stuff(collision_list)
                #     elif self.color == Field.BLACK:
                #         self.robot_drops_stuff(collision_list)

                self.robot_is_inside = True
            return True
        else:
            # robot leaves
            self.robot_is_inside = False
            return False

    def set_color(self, color):
        self.color = color

    def scent(self):
        """Thread to manager the scent on this field"""
        print "scent thread is running", self.scent_t
        while not self.scent_stop.wait(self.scent_decay_time) and self.color != self.WHITE:
            # only decrease scent if no robot is inside the field
            if not self.robot_is_inside:
                # set the color gradient based on self.gradient and check that the value is not higher than 255
                # it was easier to set the gradient first as an array (easier access to single elements)
                # then we convert it into a tuple because then we can simply add the colors via numpy
                color_gradient = [0, 0, 0]
                for i in range(3):
                    if self.color[i] + self.gradient <= 255:
                        color_gradient[i] = self.gradient
                    else:
                        color_gradient[i] = self.color[i] - 255
                color_grad_tuple = tuple(color_gradient)
                self.color = tuple(numpy.add(self.color, color_grad_tuple))
        print "Thread stops: ", self.scent_t
        # to be safe, we set the color to white if the thread stops
        self.color = self.WHITE

    def stop_scent(self):
        self.scent_stop.set()

    def start_scent(self, colliding_robot):
        """
        We make some checks, and if they hold, the scent thread is started

        :param colliding_robot: output from the collision test
        :return: None
        """
        # check if the robot is carrying stuff and the the according color
        if colliding_robot.pop(0).carries_stuff:  # TODO: This seems not right !!!
            color_gradient = list(self.INCREASE_BLUE)
        else:
            color_gradient = list(self.INCREASE_ORANGE)

        # create the color gradient which is added, check that the value will not be below 0
        # it was easier to set the gradient first as an array (easier access to single elements)
        # then we convert it into a tuple because then we can simply add the colors via numpy
        for i in range(3):
            if self.color[i] + color_gradient[i] < 0:
                color_gradient[i] = - self.color[i]
        color_grad_tuple = tuple(color_gradient)
        self.set_color(tuple(numpy.add(self.color, color_grad_tuple)))
        # start the thread only if it is not already running
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
