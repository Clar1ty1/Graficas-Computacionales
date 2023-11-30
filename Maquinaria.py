import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Maquinaria:

    def __init__(self, position):
        # Se inicializa las coordenadas de los vertices del cubo
        self.Position = position
        self.bolsas = []

    def addBolsa(self, bolsa):
        self.bolsas.append(bolsa)