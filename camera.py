from copy import copy
import cv2
import pygame
import threading
import numpy as np

from robot import Robot
from Queue import Empty as QueueEmptyError
from colorfilter import ColorFilter


class Camera:
    """
    This class is all about tracking
    There is still much testing stuff implemented
    """
    cross = [200, 200]  # for testing
    # This is the Group that holds all robots. This is used in other classes e.g. to check for collisions with fields
    robots_carry = pygame.sprite.Group()
    robots_no_carry = pygame.sprite.Group()
    robots = pygame.sprite.Group()

    # noinspection PyArgumentList
    def __init__(self, capture_source):
        self.capture_source = capture_source

        self.stop_ev = threading.Event()  # This event is fired if the threads should stop e.g. end of program
        self.camera_found_robot_event = threading.Event()  # for testing, can be fired to start "walking"
        self.robot_mutex = threading.Lock()  # a lock object, so that robots is Threadsafe
        print "initilaizing Camera"
        # a pygame event, fired when robots are found, and contains the robots -> not sure if mutex is needed anymore
        self.robot_found_event = pygame.event.Event(pygame.USEREVENT, robots=self.robots, robot_mutex=self.robot_mutex)

        # for testing -> artifical robots are created and walking is simulated
        self.robot_walks = threading.Thread(target=self.walking)
        self.robot_stops = threading.Event()

        # Variables needed for tracking
        # they hold the maximum and minimum values for hue, saturation and value (HSV) for the colorfilter
        self.colorfilter_no_carry = ColorFilter("colorfilter_no_carry", "orange")
        self.colorfilter_carry = ColorFilter("colorfilter_carry", "blue")

        self.MAX_NUM_OBJECTS = 10  # if the number of found objects exceeds this, then we declare too much noise
        self.MIN_OBJECT_AREA = 20 * 20
        self.objects = []
        self.debug = False

    def send_event(self, event_queue):
        print "Camera is sending an event"
        try:
            # pygame.event.post(self.robot_found_event)
            event_queue.put(self.robots)
        except pygame.error:
            print "The Event queue is probably full"
        except Exception as e:
            print e
        finally:
            self.camera_found_robot_event.clear()

    def stop(self):
        self.stop_ev.set()
        self.robot_stops.set()

    def run(self, queue):
        print "start"
        while not self.stop_ev.wait(0.1):
            print "wait"
            # if self.camera_found_robot_event.wait(0.1):
            self.send_event(queue)
            try:
                if not self.robot_walks.is_alive():
                    self.robot_walks.start()
            except RuntimeError:
                del self.robot_walks
                self.robot_walks = threading.Thread(target=self.walking)
                self.robot_walks.start()

            # print "camera is running"
        print "stopped camera"

    def walking(self):
        counter = 0
        maxcounter = 50
        while not self.robot_stops.wait(0.3):
            print "robot walks"
            print "mutex: ", self.robot_mutex.locked()
            ret = self.robot_mutex.acquire(True)
            print "acquired mutex", ret
            for robot in self.robots:
                robot.rect.x -= 5
                # robot.rect.y -= 5
                print robot.rect.x, robot.rect.y
                self.send_event()
            self.robot_mutex.release()
            if counter > maxcounter:
                print "stopping robot walk thread"
                try:
                    self.robot_mutex.release()
                except threading.ThreadError as e:
                    print "could not release mutex"
                    print e
                break
            counter += 1

    @staticmethod
    def morph_ops(thresh):
        """
        A binary image is processed so that noise is filtered out, and the object can be seen more clearly
        :param thresh: binary image to process
        :return: processed image
        """
        erode_kern = np.ones((3, 3), np.uint8)
        dilate_kern = np.ones((8, 8), np.uint8)
        thresh = cv2.erode(thresh, erode_kern, thresh, iterations=2)
        thresh = cv2.dilate(thresh, dilate_kern, thresh, iterations=2)

        return thresh

    def draw_object(self, frame):
        for obj in self.objects:
            cv2.circle(frame, (obj[0], obj[1]), 20, (0, 255, 0))

    def track_filtered_object(self, threshold, robot_list, scent, camera_feed):

        temp = copy(threshold)
        # find contours of filtered image using openCV findContours function
        if cv2.__version__ == "3.2.0":
            im2, contours, hierarchy = cv2.findContours(temp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(temp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        # use moments method to find our filtered object
        self.objects = []
        robot_list.empty()
        try:  # if hierarchy.shape[1] > 0:

            first = True
            num_objects = hierarchy.shape[1]
            # if number of objects greater than MAX_NUM_OBJECTS we have a noisy filter
            if num_objects < self.MAX_NUM_OBJECTS:
                self.robot_mutex.acquire()
                for index in range(num_objects):

                    moment = cv2.moments(contours[index])
                    area = moment['m00']

                    # if the area is less than 20 px by 20px then it is probably just noise
                    # if the area is the same as the 3 / 2 of the image size, probably just a bad filter
                    # we only want the object with the largest area so we safe a reference area each
                    # iteration and compare it to the area in the next iteration.
                    if area > self.MIN_OBJECT_AREA:
                        # print "found position: ", moment['m10'], " + ", moment['m01']
                        # will be used for calibration
                        self.objects.append([int(moment['m10'] / area), int(moment['m01'] / area)])
                        robot_list.add(Robot(int(moment['m10'] / area), int(moment['m01'] / area), width=20, height=20,
                                             scent=scent))

                        object_found = True

                    else:
                        object_found = False

                    # // let user know you found an object
                    if object_found:
                        pass
                    # // draw object location on screen
                    #     self.draw_object(camera_feed)
                self.robot_mutex.release()
            else:
                print "too much noise!"
                cv2.putText(camera_feed, "TOO MUCH NOISE! ADJUST FILTER", (0, 50), 1, 2, (0, 0, 255), 2)
        except:
            print "did not find objects"

    def start_capture(self, queue, stop_queue):

        cap = cv2.VideoCapture(self.capture_source)
        # cap = cv2.VideoCapture(0)

        if self.debug:
            # Kalibrierung #######
            cv2.namedWindow('Trackbar_no_carry', 1)
            cv2.moveWindow('Trackbar_no_carry', 20, 20)

            cv2.namedWindow('Trackbar_carry', 1)
            cv2.moveWindow('Trackbar_carry', 400, 20)

            self.colorfilter_no_carry.createTrackbar('Trackbar_no_carry')
            self.colorfilter_carry.createTrackbar('Trackbar_carry')

            ########################

            cv2.namedWindow('frame', flags=cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow('frame', 20, 400)
            cv2.namedWindow('mask_carry', flags=cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow('mask_carry', 800, 20)
            cv2.namedWindow('mask_no_carry', flags=cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow('mask_no_carry', 800, 400)

            if self.capture_source != '0':
                cv2.resizeWindow('frame', 800, 400)
                cv2.resizeWindow('mask_carry', 800, 400)
                cv2.resizeWindow('mask_no_carry', 800, 400)
        # cv2.namedWindow('res', flags=cv2.WINDOW_AUTOSIZE)
        # # cv2.resizeWindow('res', 800, 400)
        # cv2.moveWindow('res', 800, 400)

        while True:  # not self.stop_ev.wait(0.05):
            # if self.camera_found_robot_event.wait(0.05):
            ok, frame = cap.read()
            if ok:
                if self.capture_source != '0':
                    frame = cv2.resize(frame, (640, 360), frame, 0, 0, cv2.INTER_CUBIC)

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                mask_carry = cv2.inRange(hsv, self.colorfilter_carry.lower_color, self.colorfilter_carry.upper_color)
                mask_carry = self.morph_ops(mask_carry)
                self.track_filtered_object(mask_carry, self.robots_carry, self.colorfilter_carry.scent, frame)

                mask_no_carry = cv2.inRange(hsv, self.colorfilter_no_carry.lower_color,
                                            self.colorfilter_no_carry.upper_color)
                mask_no_carry = self.morph_ops(mask_no_carry)
                self.track_filtered_object(mask_no_carry, self.robots_no_carry, self.colorfilter_no_carry.scent, frame)
                # res = cv2.bitwise_and(frame, frame, mask=mask)

                if self.debug:
                    # Kalibrierung
                    cv2.imshow('frame', frame)
                    cv2.imshow('mask_carry', mask_carry)
                    cv2.imshow('mask_no_carry', mask_no_carry)
                    ############

                # cv2.imshow('res', res)

                self.robots.empty()
                self.robots.add(self.robots_carry)
                self.robots.add(self.robots_no_carry)
                self.send_event(queue)

                k = cv2.waitKey(5) & 0xff
                if k == 27:
                    break
            else:
                break

            try:
                stop_event = stop_queue.get(True, 0.05)
                if stop_event:
                    break
            except QueueEmptyError:
                pass

        cv2.destroyAllWindows()
        cap.release()
