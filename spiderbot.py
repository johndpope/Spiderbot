import pygame
import threading

from camera import Camera
from field import Field
from playingfield import PlayingField

# TODO: make this pretty, probably own class so that two processes can be spawned, important for raspbery pi

print "start"

# initialize pygame -> our graphics tool
pygame.init()

# the resolution of the beamer is 854 * 480
win = pygame.display.set_mode((854, 480))

pygame.display.set_caption("Chantys Spiderbot")
pygame.key.set_repeat(50, 50)  # so that a pressed key is recognized multiple times

# global run state, program will run as long as this is set to True
run = True

# initialize the playingfield
pf = PlayingField(854, 480)

# initialize the camera At this point, any other object can be initialized and hooked up to the program, which sends
# via an event the coordinates of the robots
camera = Camera()

t = threading.Thread(target=camera.start_capture)
t.start()
print "going on"

while run:
    # TODO: make the delay better, so that a constant frame rate is used -> pygame can do this
    pygame.time.delay(10)
    # check for pygame events, like keys and user events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            camera.stop_camera()
            pf.stop_threads()
        if event.type == pygame.KEYDOWN:
            # most important key combination -> STRG + q to quit the program
            if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                run = False
                camera.stop_camera()
                pf.stop_threads()
            if event.key == pygame.K_r:
                # used to start the artificial robots for testing
                print "pressed "r""
                camera.camera_found_robot_event.set()
            # these are no longer used, but we leave them, could be useful for debugging
            if event.key == pygame.K_LEFT:
                camera.cross[0] -= 5
            if event.key == pygame.K_RIGHT:
                camera.cross[0] += 5
            if event.key == pygame.K_UP:
                camera.cross[1] -= 5
            if event.key == pygame.K_DOWN:
                camera.cross[1] += 5
        # We wait for this user event from camera, it contains the robot positions, so the playingfield can process them
        if event.type == pygame.USEREVENT:
            try:
                pf.update_robot_position(event.robots, event.robot_mutex)
            except Exception as e:
                print "Exception while trying to update robot positin"
                print e

    # draw the screen
    win.fill(Field.BRIGHT)

    pf.update(win)
    camera.update(win)

    pygame.display.update()

pygame.quit()
