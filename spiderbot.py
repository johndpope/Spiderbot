import pygame
import threading
from multiprocessing import Process, Queue
from Queue import Empty as QueueEmptyError

import camera
from camera import Camera
from simulator import Simulator
from field import Field
from playingfield import PlayingField

# TODO: make this pretty, probably own class so that two processes can be spawned, important for raspbery pi

# parameters
# the resolution of the beamer is 854 * 480
FIELD_WIDTH = 854
FIELD_HEIGHT = 480
simulation_mode = True
draw_robots = True

# initialize pygame -> our graphics tool
pygame.init()

win = pygame.display.set_mode((FIELD_WIDTH, FIELD_HEIGHT))

pygame.display.set_caption("Spiderbot")
pygame.key.set_repeat(50, 50)

# global run state, program will run as long as this is set to True
run = True

# initialize the playingfield
pf = PlayingField(FIELD_WIDTH, FIELD_HEIGHT, draw_robots=draw_robots)

# initialize the eventhandler
eventhandler = Simulator() if simulation_mode else Camera()
if not simulation_mode:
    t = Process(target=camera.start_capture, args=(camera_event_queue, ))
    t.start()

event_queue = Queue()

win.fill(Field.BRIGHT)
while run:
    # TODO: make the delay better, so that a constant frame rate is used -> pygame can do this
    pygame.time.delay(10)

    # check for pygame events, like keys and user events
    for event in pygame.event.get():
        if (event.type == pygame.QUIT
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_q)):
            # press Q or close pygame window to stop program
            run = False
            eventhandler.stop()
            pf.stop_threads()
        elif event.type == pygame.KEYDOWN:
            # press R for running simulation
            if simulation_mode:
                if event.key == pygame.K_r:
                    eventhandler_run_thread = threading.Thread(
                        target=eventhandler.run, args=[event_queue])
                    eventhandler_run_thread.start()
            else:
                # these are no longer used, but we leave them, could be useful for debugging
                if event.key == pygame.K_LEFT:
                    eventhandler.cross[0] -= 5
                if event.key == pygame.K_RIGHT:
                    eventhandler.cross[0] += 5
                if event.key == pygame.K_UP:
                    eventhandler.cross[1] -= 5
                if event.key == pygame.K_DOWN:
                    eventhandler.cross[1] += 5

        # TODO is this block still needed? possibly remove it
        # We wait for this user event from camera, it contains the robot positions, so the playingfield can process them
        elif event.type == pygame.USEREVENT:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            1/0
            pf.update_robot_position(event.robots, event.robot_mutex)

    try:
        robots = event_queue.get(True, 0.1)
        if robots:
            pf.update_robot_position(robots)
    except QueueEmptyError:
        pass

    # draw the screen
    pf.update(win)
    pygame.display.update()

pygame.quit()
print "done"
