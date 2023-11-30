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
    cargoArea = [-260, 233]
    weighingScale = [22, 142]
    machineZone = [48, -88]
    def __init__(self, dim, vel, textures, idx, currentNode, other_lifters):
        self.dim = dim
        self.idx = idx
        self.other_lifters = other_lifters
        self.evasive_time = 5.0
        # Se inicializa una posicion aleatoria en el tablero
        # self.Position = [random.randint(-dim, dim), 6, random.randint(-dim, dim)]
        self.Position = [-255 - idx*20, 2, 238+idx*20]
        
        self.Direction = numpy.zeros(3);
        self.angle = 0
        self.vel = vel
        self.currentNode = currentNode;
        self.nextNode = currentNode;

        # Arreglo de texturas
        self.textures = textures

        # Control variables for platform movement
        self.platformHeight = -1.5
        self.platformUp = False
        self.platformDown = False
        self.weighingTime = 10
        #Control variable for collisions
        self.radiusCol = 10

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
     
    def liftBolsa(self, bolsa):
        self.bolsa = bolsa
    def dropBolsa(self):
        bolsaTemp = self.bolsa
        self.bolsa = None
        return bolsaTemp
   
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
        if nueva_direccion is not None:
            # Normalizar la nueva dirección para asegurar una magnitud adecuada
            Direccion = nueva_direccion

        # print(" Agent : %d \t State: %s \t Position : [%0.2f, 0 %0.2f] " %(self.idx, self.status, self.Position[0], self.Position[-1]) );

        if Distancia < 1:
            self.currentNode = self.nextNode

        mssg = "Agent:%d \t State:%s \t Position:[%0.2f,0,%0.2f] \t NodoActual:%d \t NodoSiguiente:%d" %(self.idx, self.status, self.Position[0], self.Position[-1], self.currentNode, self.nextNode); 
        print(mssg);

        match self.status:
            case "searching":
                # Update position
                self.Position += Direccion * self.vel;
                self.Direction = Direccion;
                self.angle = math.acos(self.Direction[0]) * 180 / math.pi
                if self.Direction[2] > 0:
                    self.angle = 360 - self.angle	
                if Distancia < 1: 
                    self.currentNode = self.nextNode
                    
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
                if self.platformHeight >= 2:
                    self.status = "delivering"
                else:
                    self.platformHeight += delta
                self.weighingTime = 20
            case "delivering":
                self.drawTrash()
                self.Position += Direccion * self.vel;
                self.Direction = Direccion;
                self.angle = math.acos(self.Direction[0]) * 180 / math.pi
                if self.Direction[2] > 0:
                    self.angle = 360 - self.angle	
                if Distancia < 1: 
                    self.currentNode = self.nextNode
            case "weighing":
                self.weighingTime -= delta
                if self.weighingTime < 0:
                    self.status = "delivering"
                #print(self.weighingTime)
            case "dropping":
                if self.platformHeight <= -1.5:
                    self.status = "searching"
                else:
                    self.platformHeight -= delta


    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glRotatef(self.angle, 0, 1, 0)
        glScaled(5, 5, 5)
        glColor3f(1.0, 1.0, 1.0)
        # front face
        glEnable(GL_TEXTURE_2D)


        glBindTexture(GL_TEXTURE_2D, self.textures[7])
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
        glBindTexture(GL_TEXTURE_2D, self.textures[1])
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
        glScaled(1.5, 1.5, 1.5)
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


        glPopMatrix()