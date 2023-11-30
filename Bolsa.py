import pygame, numpy
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math


class Bolsa:
    def __init__(self, position, textures, txtIndex):

        self.Position = position
        
        #Arreglo de texturas
        self.textures = textures

        #Index de la textura a utilizar
        self.txtIndex = txtIndex

        #Control variable for drawing
        self.alive = True

        self.weight = numpy.random.randint(800, 1200)


    def draw(self):
        if self.alive:
            glPushMatrix()
            glTranslatef(self.Position[0], self.Position[1], self.Position[2])
            glScaled(8, 8, 8)
            glColor3f(1.0, 1.0, 1.0)

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textures[self.txtIndex])

            glBegin(GL_QUADS)

            # Front face
            glTexCoord2f(0.0, 0.0)
            glVertex3d(1, 1, 1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(-1, 1, 1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(-1, -1, 1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(1, -1, 1)

            # Back face
            glTexCoord2f(0.0, 0.0)
            glVertex3d(-1, 1, -1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(1, 1, -1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(1, -1, -1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(-1, -1, -1)

            # Left face
            glTexCoord2f(0.0, 0.0)
            glVertex3d(-1, 1, 1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(-1, 1, -1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(-1, -1, -1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(-1, -1, 1)

            # Right face
            glTexCoord2f(0.0, 0.0)
            glVertex3d(1, 1, -1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(1, 1, 1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(1, -1, 1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(1, -1, -1)

            # Top face
            glTexCoord2f(0.0, 0.0)
            glVertex3d(-1, 1, 1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(1, 1, 1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(1, 1, -1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(-1, 1, -1)

            # Bottom face
            glTexCoord2f(0.0, 0.0)
            glVertex3d(-1, -1, 1)
            glTexCoord2f(1.0, 0.0)
            glVertex3d(1, -1, 1)
            glTexCoord2f(1.0, 1.0)
            glVertex3d(1, -1, -1)
            glTexCoord2f(0.0, 1.0)
            glVertex3d(-1, -1, -1)

            glEnd()
            glDisable(GL_TEXTURE_2D)

            glPopMatrix()