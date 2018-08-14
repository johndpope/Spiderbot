import pygame

from field import Field


class PlayingField:
    """The PlayingField defines the complete field.
    It waits for Events and add changes to the rooms"""

    fields = []  # type: List[Field]

    def __init__(self, width, height, draw_robots=False,
                 green_fields=((1, 3), (5, 5), (10, 10)),
                 queen_fields=((10, 5),)):

        self.draw_robots = draw_robots
        self.green_fields = list([list(field) for field in green_fields])
        self.queen_fields = list([list(field) for field in queen_fields])

        # Beamer area is 854 x 480
        self.width = width
        self.height = height
        self.number_of_fields_x = 20
        self.number_of_fields_y = 10

        # calculate the field width and height from the numbers of the complete playingfield
        self.field_width = self.width / self.number_of_fields_x
        self.field_height = self.height / self.number_of_fields_y

        self.robots = []

        self.create_fields()

    def create_fields(self):
        """
        Create all the fields that are present on the playingfield
        :return: None
        """
        # go through the number of fields in x and y direction
        for fx in range(self.number_of_fields_x):
            for fy in range(self.number_of_fields_y):
                # calculate the position of the field
                x = fx * self.field_width
                y = fy * self.field_height
                # determine the color of the field
                color = Field.WHITE
                # the field-number determines if the field will be food, queen or normal
                if [fx, fy] in self.green_fields:
                    color = Field.GREEN
                if [fx, fy] in self.queen_fields:
                    color = Field.BLACK
                self.fields.append(Field(x, y, self.field_width, self.field_height, color))

    def update_robot_position(self, robots):
        """
        check in which fields the robots are to set new trails
        :param robots: Group of robots from camera
        :param mutex: lock object for thread safety
        :return: None
        """
        for field in self.fields:
            try:
                field.check_if_robot_inside(robots)
            except ValueError:
                pass
        self.robots = robots

    def update(self, win):
        """
        Window update function
        :param win: window from pygame
        :return: None
        """
        for field in self.fields:
            pygame.draw.rect(win, field.color, field.rect, 0)

        if self.draw_robots:
            for robot in self.robots:
                pygame.draw.rect(win, Field.VIOLET, robot.rect, 0)

    def stop_threads(self):
        print "Trying to stop scent threads"
        for field in self.fields:
            field.stop_scent()
