import pygame, random, math, numpy, yaml
from pygame.locals import *
from Cubo import Cubo
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import os

# Cargar las coordenadas desde el archivo YAML
with open('Nodos.yaml', 'r') as file:
    nodos_yaml = yaml.safe_load(file)

tupla = []
coordenadas_original = []
for nodos in nodos_yaml:
    if nodos[0] == '(':
        tupla.append(nodos[1:])
    size = len(nodos)
    if nodos[size-1] == ')':
        tupla.append(nodos[:-1])
        coordenadas_original.append(tupla)
        tupla = []

coordenadas_modificadas = [[float(x), 2.0, float(y)] for [x, y] in coordenadas_original]
NodosVisita = numpy.asarray(coordenadas_modificadas, dtype=numpy.float64)
print(NodosVisita)

A = numpy.zeros((3,3))

A[0,1] = 1;
A[1,2] = 1;
A[2,0] = 1;

class Lifter:
    def __init__(self, dim, vel, textures, idx, position, currentNode, other_lifters):
        self.dim = dim
        self.idx = idx
        self.other_lifters = other_lifters
        self.evasive_time = 50.0
        self.max_evasive_time = 50.0
        self.wait_time = 75.0
        self.max_wait_time = 75.0
        self.Position = position
        self.distance_traveled = 0.0 

        # Se inicializa un vector de direccion aleatorio
        self.Direction = numpy.zeros(3);
        self.angle = 0
        self.vel = vel
        self.max_vel = vel
        self.currentNode = currentNode;
        self.nextNode = currentNode;
        # El vector aleatorio debe de estar sobre el plano XZ (la altura en Y debe ser fija)
        # Se normaliza el vector de direccion

        # Arreglo de texturas
        self.textures = textures

        # Control variables for platform movement
        self.platformHeight = -1.5
        self.platformUp = False
        self.platformDown = False

        #Control variable for collisions
        self.radiusCol = 5

        #Control variables for animations
        self.status = "searching"
        self.trashID = -1

    def maniobraEvasiva(self):
        for other_lifter in self.other_lifters:
            if other_lifter.idx != self.idx:
                # Calcular la distancia entre este montacargas y el otro montacargas
                distancia = numpy.linalg.norm(numpy.array(self.Position) - numpy.array(other_lifter.Position))
                # Definir una distancia de seguridad (ajusta este valor según sea necesario)
                distancia_seguridad = 10.0

                if distancia < distancia_seguridad:
                    # Calcular el vector entre los montacargas
                    vector_entre_montacargas = numpy.array(other_lifter.Position) - numpy.array(self.Position)

                    # Calcular el vector perpendicular rotando 90 grados en sentido horario (en el plano XZ)
                    direccion_evasiva = numpy.array([-vector_entre_montacargas[2], 0, vector_entre_montacargas[0]])

                    # Normalizar la nueva dirección para asegurar una magnitud adecuada
                    direccion_evasiva /= numpy.linalg.norm(direccion_evasiva)

                    # Disminuir la velocidad solo si este montacargas tiene un índice mayor
                    if self.idx > other_lifter.idx:
                        self.vel = self.vel * 0.8  # Disminuir la velocidad en un 20%

                    # Actualizar la dirección del montacargas para evitar la colisión
                    return direccion_evasiva
                else:
                    return None



    def search(self):
        # Change direction randomly
        u = numpy.random.rand(3);
        u[1] = 0;
        u /= numpy.linalg.norm(u);
        self.Direction = u;

    def targetCenter(self):
        # Set direction to center
        dirX = -self.Position[0]
        dirZ = -self.Position[2]
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 4, (dirZ / magnitude)]
        
    def ComputeDirection(self, Posicion, NodoSiguiente):
        Direccion = NodosVisita[NodoSiguiente,:] - Posicion
        Direccion = numpy.asarray( Direccion)
        Distancia = numpy.linalg.norm( Direccion )
        Direccion /= Distancia
        return Direccion, Distancia
    
    def RetrieveNextNode(self, NodoActual):
        if NodoActual == len(NodosVisita) - 1 :
            return 0;
        else:
            return NodoActual + 1

    def update(self, delta):

        self.nextNode = self.RetrieveNextNode(self.currentNode);
		
        Direccion, Distancia =  self.ComputeDirection(self.Position, self.nextNode);

        nueva_direccion = self.maniobraEvasiva()

        # Si hay una nueva dirección y estamos dentro del tiempo de evasión
        if nueva_direccion is not None and self.evasive_time > 0.0:
            # Normalizar la nueva dirección para asegurar una magnitud adecuada
            Direccion = nueva_direccion
            self.evasive_time -= 1

        # Si estamos dentro del tiempo de espera
        if self.wait_time > 0.0:
            self.wait_time -= 1
        else:
            # Restablecer el tiempo de espera y el tiempo de evasión
            self.wait_time = self.max_wait_time
            self.evasive_time = self.max_evasive_time
            self.vel = self.max_vel
        
        self.distance_traveled += Distancia

        # print(" Agent : %d \t State: %s \t Position : [%0.2f, 0 %0.2f] " %(self.idx, self.status, self.Position[0], self.Position[-1]) );

        if Distancia < 1:
            self.currentNode = self.nextNode

        mssg = "Agent:%d \t State:%s \t Position:[%0.2f,0,%0.2f] \t NodoActual:%d \t NodoSiguiente:%d \t DistanceTraveled:%0.2f" % (
            self.idx, self.status, self.Position[0], self.Position[-1], self.currentNode, self.nextNode, self.distance_traveled)

        print(mssg);

        match self.status:
            case "searching":
                # Update position
                self.Position += Direccion * self.vel;
                self.Direction = Direccion;
                self.angle = math.acos(self.Direction[0]) * 180 / math.pi
                if self.Direction[2] > 0:
                    self.angle = 360 - self.angle	

                # Move platform
                if self.platformUp:
                    if self.platformHeight >= 0:
                        self.platformUp = False
                    else:
                        self.platformHeight += delta
                elif self.platformDown:
                    if self.platformHeight <= -1.5:
                        self.platformUp = True
                    else:
                        self.platformHeight -= delta		
            case "lifting":
                if self.platformHeight >= 0:
                    self.targetCenter()
                    self.status = "delivering"
                else:
                    self.platformHeight += delta
            case "delivering":
                if (self.Position[0] <= 10 and self.Position[0] >= -10) and (self.Position[2] <= 10 and self.Position[2] >= -10):
                    self.status = "dropping"
                else:
                    newX = self.Position[0] + self.Direction[0] * self.vel
                    newZ = self.Position[2] + self.Direction[2] * self.vel
                    if newX - 10 < -self.dim or newX + 10 > self.dim:
                        self.Direction[0] *= -1
                    else:
                        self.Position[0] = newX
                    if newZ - 10 < -self.dim or newZ + 10 > self.dim:
                        self.Direction[2] *= -1
                    else:
                        self.Position[2] = newZ
                    self.angle = math.acos(self.Direction[0]) * 180 / math.pi
                    if self.Direction[2] > 0:
                        self.angle = 360 - self.angle
            case "dropping":
                if self.platformHeight <= -1.5:
                    self.status = "returning"
                else:
                    self.platformHeight -= delta
            case "returning":
                if (self.Position[0] <= 20 and self.Position[0] >= -20) and (self.Position[2] <= 20 and self.Position[2] >= -20):
                    self.Position[0] -= (self.Direction[0] * (self.vel/4))
                    self.Position[2] -= (self.Direction[2] * (self.vel/4))
                else:
                    self.search()
                    self.status = "searching"


    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glRotatef(self.angle, 0, 1, 0)
        glScaled(3.5, 3.5, 3.5)
        glColor3f(1.0, 1.0, 1.0)
        # front face
        glEnable(GL_TEXTURE_2D)
        if os.name == "posix":
            glBindTexture(GL_TEXTURE_2D, self.textures[7])
        else:
            glBindTexture(GL_TEXTURE_2D, self.textures[10])

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, 1)

        # 2nd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-2, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-2, -1, 1)

        # 3rd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-2, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-2, -1, -1)

        # 4th face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, -1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, -1)

        # top
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, -1)
        glEnd()

        # Head

        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glScaled(0.8, 0.8, 0.8)
        glColor3f(1.0, 1.0, 1.0)
        head = Cubo(self.textures, 0)
        head.draw()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        # Wheels
        glEnable(GL_TEXTURE_2D)
        if os.name == "posix":
            glBindTexture(GL_TEXTURE_2D, self.textures[8])
        else:
            glBindTexture(GL_TEXTURE_2D, self.textures[6])
        glPushMatrix()
        glTranslatef(-1.2, -1, 1)
        glScaled(0.3, 0.3, 0.3)
        glColor3f(1.0, 1.0, 1.0)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -1, 1)
        glScaled(0.3, 0.3, 0.3)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -1, -1)
        glScaled(0.3, 0.3, 0.3)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-1.2, -1, -1)
        glScaled(0.3, 0.3, 0.3)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        # Lifter
        glPushMatrix()
        if self.status in ["lifting","delivering","dropping"]:
            self.drawTrash()
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, self.platformHeight, 0)  # Up and down
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(3, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(3, 1, 1)
        glEnd()
        glPopMatrix()
        glPopMatrix()

    def drawTrash(self):
        glPushMatrix()
        glTranslatef(2, (self.platformHeight + 1.5), 0)
        glScaled(0.5, 0.5, 0.5)
        glColor3f(1.0, 1.0, 1.0)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[3])

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
