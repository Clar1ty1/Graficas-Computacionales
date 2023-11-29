
import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *



import random
import math


class Edificio:

    face1 = [
        [1, 1, 1],
        [1, 1, -1],
        [1, -1, -1],
        [1, -1, 1],
    ]

    face2 = [
        [-1, 1, 1],
        [1, 1, 1],
        [1, -1, 1],
        [-1, -1, 1],
    ]

    face3 = [
        [-1, 1, -1],
        [-1, 1, 1],
        [-1, -1, 1],
        [-1, -1, -1],
    ]

    face4 = [
        [1, 1, -1],
        [-1, 1, -1],
        [-1, -1, -1],
        [1, -1, -1],
    ]
    face5 = [
        [1, 1, 1],
        [-1, 1, 1],
        [-1, 1, -1],
        [1, 1, -1],
    ]

    """
        Initializes the coordinates of the cube vertices.

        Parameters:
            textures (list): An array of textures.
            txtIndex (int): The index of the texture to use.
            position (tuple): The position of the cube.
            scale (float): The scale of the cube.

        Returns:
            None
    """
    def __init__(self, textures, position, scale,  txtIndex):
        # Se inicializa las coordenadas de los vertices del cubo

        self.Position = position

        self.Scale = scale

        #Arreglo de texturas
        self.textures = textures

    

        self.txtIndex = txtIndex

    def setFace1DistanceFromOrigin(self, width):
        self.face1[0][0] = width
        self.face1[1][0] = width
        self.face1[2][0] = width
        self.face1[3][0] = width
        #self.draw()
    def setFace1Heigth(self, height):
        self.face1[0][1] = height
        self.face1[1][1] = height
        self.face1[2][1] = -height
        self.face1[3][1] = -height
        #self.draw()
    def setFace1Width(self, distance):
        self.face1[0][2] = distance
        self.face1[1][2] = -distance
        self.face1[2][2] = -distance
        self.face1[3][2] = distance
        #self.draw()
    def setFace2Width(self, width):
        self.face2[0][0] = -width
        self.face2[1][0] = width
        self.face2[2][0] = width
        self.face2[3][0] = -width
        #self.draw()
    def setFace2Heigth(self, height):
        self.face2[0][1] = height
        self.face2[1][1] = height
        self.face2[2][1] = -height
        self.face2[3][1] = -height
        #self.draw()
    def setFace2DistanceFromOrigin(self, distance):
        self.face2[0][2] = distance
        self.face2[1][2] = distance
        self.face2[2][2] = distance
        self.face2[3][2] = distance
        #self.draw()
    def setFace3DistanceFromOrigin(self, distance):
        self.face3[0][0] = -distance
        self.face3[1][0] = -distance
        self.face3[2][0] = -distance
        self.face3[3][0] = -distance
        #self.draw()
    def setFace3Heigth(self, height):
        self.face3[0][1] = height
        self.face3[1][1] = height
        self.face3[2][1] = -height
        self.face3[3][1] = -height
        #self.draw()
    def setFace3Width(self, width):
        self.face3[0][2] = -width
        self.face3[1][2] = width
        self.face3[2][2] = width
        self.face3[3][2] = -width
        #self.draw()
    def setFace4Width(self, width):
        self.face4[0][0] = width
        self.face4[1][0] = -width
        self.face4[2][0] = -width
        self.face4[3][0] = width
        #self.draw()
    def setFace4Heigth(self, height):
        self.face4[0][1] = height
        self.face4[1][1] = height
        self.face4[2][1] = -height
        self.face4[3][1] = -height
        #self.draw()
    def setFace4DistanceFromOrigin(self, distance):
        self.face4[0][2] = -distance
        self.face4[1][2] = -distance
        self.face4[2][2] = -distance
        self.face4[3][2] = -distance
        #self.draw()
    def setFace5Width(self, width):
        self.face5[0][0] = width
        self.face5[1][0] = -width
        self.face5[2][0] = -width
        self.face5[3][0] = width
        ##self.draw()
    def setFace5DistanceFromOrigin(self, distance):
        self.face5[0][1] = distance
        self.face5[1][1] = distance
        self.face5[2][1] = distance
        self.face5[3][1] = distance
        #self.draw()
    def setFace5Heigth(self, height):
        self.face5[0][2] = height
        self.face5[1][2] = height
        self.face5[2][2] = -height
        self.face5[3][2] = -height
        #self.draw()
    
    def draw(self):
        glPushMatrix()
        glScalef(self.Scale, self.Scale, self.Scale)
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[self.txtIndex])
        glBegin(GL_QUADS)
        
        #glColor3f(self.color[0], self.color[1], self.color[2])
        
        #1st face
        glTexCoord2f(0, 0)
        glVertex3d(self.face1[0][0], self.face1[0][1], self.face1[0][2])
        glTexCoord2f(1, 0)
        glVertex3d(self.face1[1][0], self.face1[1][1], self.face1[1][2])
        glTexCoord2f(1, 1)
        glVertex3d(self.face1[2][0], self.face1[2][1], self.face1[2][2])
        glTexCoord2f(0, 1)
        glVertex3d(self.face1[3][0], self.face1[3][1], self.face1[3][2])

        #2nd face
        glTexCoord2f(0, 0)
        glVertex3d(self.face2[0][0], self.face2[0][1], self.face2[0][2])
        glTexCoord2f(1, 0)
        glVertex3d(self.face2[1][0], self.face2[1][1], self.face2[1][2])
        glTexCoord2f(1, 1)
        glVertex3d(self.face2[2][0], self.face2[2][1], self.face2[2][2])
        glTexCoord2f(0, 1)
        glVertex3d(self.face2[3][0], self.face2[3][1], self.face2[3][2])

        #3rd face
        glTexCoord2f(0, 0)
        glVertex3d(self.face3[0][0], self.face3[0][1], self.face3[0][2])
        glTexCoord2f(1, 0)
        glVertex3d(self.face3[1][0], self.face3[1][1], self.face3[1][2])
        glTexCoord2f(1, 1)
        glVertex3d(self.face3[2][0], self.face3[2][1], self.face3[2][2])
        glTexCoord2f(0, 1)
        glVertex3d(self.face3[3][0], self.face3[3][1], self.face3[3][2])

        #4th face
        glTexCoord2f(0, 0)
        glVertex3d(self.face4[0][0], self.face4[0][1], self.face4[0][2])
        glTexCoord2f(1, 0)
        glVertex3d(self.face4[1][0], self.face4[1][1], self.face4[1][2])
        glTexCoord2f(1, 1)
        glVertex3d(self.face4[2][0], self.face4[2][1], self.face4[2][2])
        glTexCoord2f(0, 1)
        glVertex3d(self.face4[3][0], self.face4[3][1], self.face4[3][2])
     

        #5th face
        glTexCoord2f(1, 1)
        glVertex3d(self.face5[0][0], self.face5[0][1], self.face5[0][2])
        glTexCoord2f(0, 1)
        glVertex3d(self.face5[1][0], self.face5[1][1], self.face5[1][2])
        glTexCoord2f(0, 0)
        glVertex3d(self.face5[2][0], self.face5[2][1], self.face5[2][2])
        glTexCoord2f(1, 0)
        glVertex3d(self.face5[3][0], self.face5[3][1], self.face5[3][2])


        #glColor3f(0,0,0)
        #glDisable(GL_TEXTURE_2D)
        glEnd()
        glPopMatrix()

        #glEnableClientState(GL_VERTEX_ARRAY)
        #glEnableClientState(GL_COLOR_ARRAY)
        #glVertexPointer(3, GL_FLOAT, 0, self.vertexCoords)
        #glColorPointer(3, GL_FLOAT, 0, self.vertexColors)
        #glDrawElements(GL_QUADS, 24, GL_UNSIGNED_INT, self.elementArray)
        #glDisableClientState(GL_VERTEX_ARRAY)
        #glDisableClientState(GL_COLOR_ARRAY)