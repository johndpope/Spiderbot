from cv2 import createTrackbar
import numpy as np


class ColorFilter:
    """This class contains the information about the colorfilter used for various objects"""

    def __init__(self, filename, scent):
        if isinstance(filename, basestring):
            self.filename = filename
            try:
                with open(filename) as f:
                    color_input = f.read()
                    color_input = color_input.split(" ")
                    self.min_hue = int(color_input[0])
                    self.max_hue = int(color_input[1])
                    self.min_sat = int(color_input[2])
                    self.max_sat = int(color_input[3])
                    self.min_val = int(color_input[4])
                    self.max_val = int(color_input[5])
            except IOError:
                # default values
                self.min_hue = 0
                self.max_hue = 255
                self.min_sat = 0
                self.max_sat = 255
                self.min_val = 0
                self.max_val = 255

            self.lower_color = np.array([self.min_hue, self.min_sat, self.min_val])
            self.upper_color = np.array([self.max_hue, self.max_sat, self.max_val])

            # this is the scent the robot gets
            self.scent = scent

        else:
            raise TypeError

    def set_min_hue(self, value):
        self.min_hue = value
        self.update_colorfilter()

    def set_max_hue(self, value):
        self.max_hue = value
        self.update_colorfilter()

    def set_min_sat(self, value):
        self.min_sat = value
        self.update_colorfilter()

    def set_max_sat(self, value):
        self.max_sat = value
        self.update_colorfilter()

    def set_min_val(self, value):
        self.min_val = value
        self.update_colorfilter()

    def set_max_val(self, value):
        self.max_val = value
        self.update_colorfilter()

    def update_colorfilter(self):
        with open(self.filename, 'w') as f:
            out = str(self.min_hue) + " " + \
                  str(self.max_hue) + " " + \
                  str(self.min_sat) + " " + \
                  str(self.max_sat) + " " + \
                  str(self.min_val) + " " + \
                  str(self.max_val)
            f.write(out)
        self.lower_color = np.array([self.min_hue, self.min_sat, self.min_val])
        self.upper_color = np.array([self.max_hue, self.max_sat, self.max_val])

    def createTrackbar(self, windowname):
        createTrackbar('min_hue', windowname, self.min_hue, 255, self.set_min_hue)
        createTrackbar('max_hue', windowname, self.max_hue, 255, self.set_max_hue)
        createTrackbar('min_sat', windowname, self.min_sat, 255, self.set_min_sat)
        createTrackbar('max_sat', windowname, self.max_sat, 255, self.set_max_sat)
        createTrackbar('min_val', windowname, self.min_val, 255, self.set_min_val)
        createTrackbar('max_val', windowname, self.max_val, 255, self.set_max_val)