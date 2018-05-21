#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import attitude_estimation

ax = ay = az = 0.0
cx = cy = cz = 0.0

def resize(width, height):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def drawText(position, textString):
    font = pygame.font.SysFont("Courier", 18, True)
    textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0.0,0.0,-7.0)

    # glTranslatef(cz, cx, cy)

    osd_text = "pitch: " + str("{0:.2f}".format(ay)) + ", roll: " + str("{0:.2f}".format(ax)) + ", yaw: " + str("{0:.2f}".format(az))

    drawText((-20,-20, -36), osd_text)

    # the way I'm holding the IMU board, X and Y axis are switched
    # with respect to the OpenGL coordinate system
    glRotatef(az, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-axis
    glRotatef(ax ,1.0,0.0,0.0)    # Pitch, rotate around x-axis
    glRotatef(-ay ,0.0,0.0,1.0)   # Roll,  rotate around z-axis

    glBegin(GL_QUADS)
    glColor3f(0.0,1.0,0.0)
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f( 1.0, 0.2, 1.0)

    glColor3f(1.0,0.5,0.0)
    glVertex3f( 1.0,-0.2, 1.0)
    glVertex3f(-1.0,-0.2, 1.0)
    glVertex3f(-1.0,-0.2,-1.0)
    glVertex3f( 1.0,-0.2,-1.0)

    glColor3f(1.0,0.0,0.0)
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0,-0.2, 1.0)
    glVertex3f( 1.0,-0.2, 1.0)

    glColor3f(1.0,1.0,0.0)
    glVertex3f( 1.0,-0.2,-1.0)
    glVertex3f(-1.0,-0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)
    glVertex3f( 1.0, 0.2,-1.0)

    glColor3f(0.0,0.0,1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2,-1.0)
    glVertex3f(-1.0,-0.2,-1.0)
    glVertex3f(-1.0,-0.2, 1.0)

    glColor3f(1.0,0.0,1.0)
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f( 1.0,-0.2, 1.0)
    glVertex3f( 1.0,-0.2,-1.0)
    glEnd()

def read_gyro():
    global ax, ay, az
    rotation = attitude_estimation.get_rotation()
    ax = rotation[0] * 57.29578049
    ay = rotation[1] * 57.29578049
    az = rotation[2] * 57.29578049

def read_imu():
    global ax, ay, az, cx, cy, cz
    attitude = attitude_estimation.get_rotation()
    ax = attitude[0] * 57.29578049
    ay = attitude[1] * 57.29578049
    az = attitude[2] * 57.29578049
    cx = attitude[3]
    cy = attitude[4]
    cz = attitude[5]

if __name__ == '__main__':
    attitude_estimation.start_thread()

    pygame.init()
    screen = pygame.display.set_mode((640,480), OPENGL | DOUBLEBUF)
    pygame.display.set_caption("Press Esc to quit")
    resize(640,480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()

    while True:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        elif event.type == KEYDOWN and event.key == K_SPACE:
            attitude_estimation.stationary = True
        elif event.type == KEYUP and event.key == K_SPACE:
            attitude_estimation.stationary = False
        read_imu()
        draw()

        pygame.display.flip()
        frames += 1

    print("fps: %d" % ((frames * 1000) / (pygame.time.get_ticks() - ticks)))
