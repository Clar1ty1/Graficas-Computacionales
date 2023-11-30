import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Bascula:

    def __init__(self, position):
        # Se inicializa las coordenadas de los vertices del cubo

        self.Position = position


