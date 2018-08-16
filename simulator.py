import cv2
import pygame
import threading

import numpy as np

from field import Field
from robot import Robot

from numpy import random


class Simulator:
    """
    Simulator class
    """
    robots = pygame.sprite.Group()

    def __init__(self):
        self.stop_ev = threading.Event()
        # for testing, can be fired to start "walking"
        self.camera_found_robot_event = threading.Event()
        self.robot_found_event = pygame.event.Event(
            pygame.USEREVENT, robots=self.robots)

        # for testing -> artifical robots are created and walking is simulated
        self.robot_walks = threading.Thread(target=self.walking)
        self.robot_stops = threading.Event()

    def send_event(self, queue):
        try:
            queue.put(self.robots)
        except pygame.error as e:
            print "The Event queue is probably full"
            raise e
        except Exception as e:
            raise e
        finally:
            self.camera_found_robot_event.clear()

    def stop(self):
        self.stop_ev.set()
        self.robot_stops.set()

    def run(self, queue, stop_queue):
        if not self.robot_walks.is_alive():
            print ">> start simulation <<"

            robot = Robot(x=0, y=150, width=10, height=10, scent='blue')
            self.robots.add(robot)

            robot = Robot(x=200, y=150, width=10, height=10, scent='orange')
            self.robots.add(robot)

            self.robot_walks.start()
            while not self.stop_ev.wait(0.1):
                self.send_event(queue)
            print "stopped simulation"
        else:
            print "sim already running"

    def walking(self, stepsize=20, max_steps=int(1e8)):
        finished_steps = 0
        while not self.robot_stops.wait(0.3):
            for robot in self.robots:
                # direction = random.randint(0, 4)
                direction = 0
                if direction == 0:
                    robot.rect.x += stepsize
                elif direction == 1:
                    robot.rect.x -= stepsize
                elif direction == 2:
                    robot.rect.y += stepsize
                elif direction == 3:
                    robot.rect.y -= stepsize
            if finished_steps > max_steps:
                print "stopping robot walk thread"
                break
            finished_steps += 1
