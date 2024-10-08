import yaml, pygame, random, glob, math, numpy, pandas, time
from Lifter import Lifter
from Bolsa import Bolsa
from Edificio import Edificio
from Bascula import Bascula
from Maquinaria import Maquinaria

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

textures = [];
lifters = [];
bolsas = [];
delta = 0;

def loadSettingsYAML(File):
	class Settings: pass
	with open(File) as f:
		docs = yaml.load_all(f, Loader = yaml.FullLoader)
		for doc in docs:
			for k, v in doc.items():
				setattr(Settings, k, v)
	return Settings;


Settings = loadSettingsYAML("Settings.yaml");	


def Texturas(filepath):
    # Arreglo para el manejo de texturas
    global textures;
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
def Init(Options):
    global textures, bolsas, lifters
    screen = pygame.display.set_mode( (Settings.screen_width, Settings.screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Simulacion")
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(Settings.FOVY, Settings.screen_width/Settings.screen_height, Settings.ZNEAR, Settings.ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
    Settings.EYE_X,
    Settings.EYE_Y,
    Settings.EYE_Z,
    Settings.CENTER_X,
    Settings.CENTER_Y,
    Settings.CENTER_Z,
    Settings.UP_X,
    Settings.UP_Y,
    Settings.UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


    
    for File in glob.glob(Settings.Materials + "*.*"):
        Texturas(File)

    Positions = [
        [-220,4,260],
        [-220,4,280],
        [-220,4,300],
        [-220,4,320],
        [-220,4,340],
    ]    
    start = time.time()
    for i in range(0, Options.lifters):
        # i es el identificator del agente
        lifters.append(Lifter(Settings.DimBoard, 0.7, textures, i, Positions[i],  0, lifters, start))
    


          
def planoText():
    # activate textures
    glEnable(GL_TEXTURE_2D)
    if os.name == "posix":
        glBindTexture(GL_TEXTURE_2D, textures[2])
    else:
        glBindTexture(GL_TEXTURE_2D, textures[12])
        
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-Settings.DimBoard, -4, -Settings.DimBoard)
    
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-Settings.DimBoard, -4, Settings.DimBoard)
    
    glTexCoord2f(1.0, 1.0)
    glVertex3d(Settings.DimBoard, -4, Settings.DimBoard)
    
    glTexCoord2f(1.0, 0.0)
    glVertex3d(Settings.DimBoard, -4, -Settings.DimBoard)
    
    glEnd()
    # glDisable(GL_TEXTURE_2D)

def checkCollisions():
    for c in lifters:
        for b in bolsas:
            distance = math.sqrt(math.pow((b.Position[0] - c.Position[0]), 2) + math.pow((b.Position[2] - c.Position[2]), 2))
            if distance <= c.radiusCol:
                if c.status == "searching" and b.alive:
                    bolsas.pop()
                    c.status = "lifting"
                    c.liftBolsa(b)
                    return

def checkLifterInWeighingScale():
    for c in lifters:
        distance = math.sqrt(math.pow((weighingScale.Position[0] - c.Position[0]), 2) + math.pow((weighingScale.Position[2] - c.Position[2]), 2))
        if distance <= c.radiusCol:
            #print("Collition")
            if c.status == "delivering" and c.weighingTime > 0:
                c.status = "weighing"
        #print(f"weighingScale {weighingScale.Position} lifters {c.Position} distance {distance}") 
def checkLifterInMachinery():
    for c in lifters:
        distance = math.sqrt(math.pow((maquinaria.Position[0] - c.Position[0]), 2) + math.pow((maquinaria.Position[2] - c.Position[2]), 2))
        if distance <= c.radiusCol:
         #   print("Collition")
            if c.status == "delivering":
                c.status = "dropping"
                maquinaria.addBolsa(c.dropBolsa())
        #print(f"maquinaria {maquinaria.Position} lifters {c.Position} distance {distance}") 
    

def display():
    global lifters, bolsas, delta, weighingScale, maquinaria
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    #Draw the lifters
    for lifter in lifters:
        lifter.draw()
        lifter.update(delta)

    glColor3f(1,1,1)
    #Draw the map
    planoText()
    glDisable(GL_TEXTURE_2D)
    weighingScale = Bascula([20, 2, 139])
    maquinaria = Maquinaria([47, 2, -85])

    txtIndex = 0
    if os.name == "posix":
        txtIndex = 9
    else:
        txtIndex = 6
    maquinariaBuilding = Edificio(textures = textures, position=[10,2,-22], scale=5, txtIndex=txtIndex)

     #Right face 
    maquinariaBuilding.setFace1Width(3.6)
    maquinariaBuilding.setFace1Heigth(5)
    maquinariaBuilding.setFace1DistanceFromOrigin(9)
    # Front face
    maquinariaBuilding.setFace2Width(9)
    maquinariaBuilding.setFace2Heigth(5)
    maquinariaBuilding.setFace2DistanceFromOrigin(3.6)

    # Left face
    maquinariaBuilding.setFace3Width(3.6)
    maquinariaBuilding.setFace3Heigth(5)
    maquinariaBuilding.setFace3DistanceFromOrigin(9)

    # Back face
    maquinariaBuilding.setFace4Width(9)
    maquinariaBuilding.setFace4Heigth(5)
    maquinariaBuilding.setFace4DistanceFromOrigin(3.6)

    # Top Face
    maquinariaBuilding.setFace5Width(9)
    maquinariaBuilding.setFace5Heigth(3.6)
    maquinariaBuilding.setFace5DistanceFromOrigin(5)

    maquinariaBuilding.draw()

    if os.name == "posix":
        txtIndex = 11
    else:
        txtIndex = 4
    hibrido = Edificio(textures = textures, position=[3,2,-10], scale=5, txtIndex=txtIndex)
    
    #Right face
    hibrido.setFace1Width(5.7)
    hibrido.setFace1Heigth(5)
    hibrido.setFace1DistanceFromOrigin(5.7)

    # Front face
    hibrido.setFace2Width(5.7)
    hibrido.setFace2Heigth(5)
    hibrido.setFace2DistanceFromOrigin(5.7)

    # Left face
    hibrido.setFace3Width(5.7)
    hibrido.setFace3Heigth(5)
    hibrido.setFace3DistanceFromOrigin(5.7)

    # Back Face
    hibrido.setFace4Width(5.7)
    hibrido.setFace4Heigth(5)
    hibrido.setFace4DistanceFromOrigin(5.7)

    # Top Face
    hibrido.setFace5Width(5.7)
    hibrido.setFace5Heigth(5.7)
    hibrido.setFace5DistanceFromOrigin(5)
    
    hibrido.draw()

    if os.name == "posix":
        txtIndex = 5
    else:
        txtIndex = 0
    area_de_seleccion = Edificio(textures = textures, position=[38.5,4,-45], scale=5, txtIndex=txtIndex)
    
    #Right face
    area_de_seleccion.setFace1Width(15)
    area_de_seleccion.setFace1Heigth(5)
    area_de_seleccion.setFace1DistanceFromOrigin(21)

    # Front face
    area_de_seleccion.setFace2Width(21.5)
    area_de_seleccion.setFace2Heigth(5)
    area_de_seleccion.setFace2DistanceFromOrigin(15)

    # Left face
    area_de_seleccion.setFace3Width(15)
    area_de_seleccion.setFace3Heigth(5)
    area_de_seleccion.setFace3DistanceFromOrigin(21)

    # Back Face
    area_de_seleccion.setFace4Width(21.5)
    area_de_seleccion.setFace4Heigth(5)
    area_de_seleccion.setFace4DistanceFromOrigin(15)

    # Top Face
    area_de_seleccion.setFace5Width(21.5)
    area_de_seleccion.setFace5Heigth(15)
    area_de_seleccion.setFace5DistanceFromOrigin(5)
    
    area_de_seleccion.draw()

    if os.name == "posix":
        txtIndex = 0
    else:
        txtIndex = 3
    zona1 = Edificio(textures = textures, position=[12.5,0,5], scale=4, txtIndex=txtIndex)
    
    #Right face
    zona1.setFace1Width(38.4)
    zona1.setFace1Heigth(6)
    zona1.setFace1DistanceFromOrigin(16.5)

    # Left face
    zona1.setFace3Width(38.4)
    zona1.setFace3Heigth(6)
    zona1.setFace3DistanceFromOrigin(16.5)

    # Front face
    zona1.setFace2Width(0)
    zona1.setFace2Heigth(0)
    zona1.setFace2DistanceFromOrigin(16)

    # Back Face
    zona1.setFace4Width(16.5)
    zona1.setFace4Heigth(6)
    zona1.setFace4DistanceFromOrigin(38.5)

    # Top Face
    zona1.setFace5Width(0)
    zona1.setFace5Heigth(0)
    zona1.setFace5DistanceFromOrigin(5)
    
    zona1.draw()

    if os.name == "posix":
        txtIndex = 0
    else:
        txtIndex = 3
    zona2 = Edificio(textures = textures, position=[55,0,10], scale=4, txtIndex=txtIndex)
    
    #Right face
    zona2.setFace1Width(38.4)
    zona2.setFace1Heigth(6)
    zona2.setFace1DistanceFromOrigin(20)

    # Left face
    zona2.setFace3Width(38.4)
    zona2.setFace3Heigth(6)
    zona2.setFace3DistanceFromOrigin(20)

    # Front face
    zona2.setFace2Width(20)
    zona2.setFace2Heigth(6)
    zona2.setFace2DistanceFromOrigin(38.5)

    # Back Face
    zona2.setFace4Width(20)
    zona2.setFace4Heigth(6)
    zona2.setFace4DistanceFromOrigin(38.5)

    # Top Face
    zona2.setFace5Width(20)
    zona2.setFace5Heigth(38.4)
    zona2.setFace5DistanceFromOrigin(5)
    
    zona2.draw()
    #checkCollisions()
    if os.name == "posix":
        txtIndex = 11
    else:
        txtIndex = 4
    hibridoTwo = Edificio(textures = textures, position=[3,2,13], scale=5, txtIndex=txtIndex)
    #Right face
    hibridoTwo.setFace1Width(13.2)
    hibridoTwo.setFace1Heigth(5)
    hibridoTwo.setFace1DistanceFromOrigin(5.7)

    # Front face
    hibridoTwo.setFace2Width(5.7)
    hibridoTwo.setFace2Heigth(5)
    hibridoTwo.setFace2DistanceFromOrigin(13.2)

    # Left face
    hibridoTwo.setFace3Width(13.2)
    hibridoTwo.setFace3Heigth(5)
    hibridoTwo.setFace3DistanceFromOrigin(5.7)

    # Back Face
    hibridoTwo.setFace4Width(5.7)
    hibridoTwo.setFace4Heigth(5)
    hibridoTwo.setFace4DistanceFromOrigin(13.2)

    # Top Face
    hibridoTwo.setFace5Width(5.7)
    hibridoTwo.setFace5Heigth(13.2)
    hibridoTwo.setFace5DistanceFromOrigin(5)

    hibridoTwo.draw()

    if os.name == "posix":
        txtIndex = 11
    else:
        txtIndex = 4
    hibridoThree = Edificio(textures = textures, position=[14.7,2,-10], scale=5, txtIndex=txtIndex)
    
    #Right face
    hibridoThree.setFace1Width(5.7)
    hibridoThree.setFace1Heigth(5)
    hibridoThree.setFace1DistanceFromOrigin(3)

    # Front face
    hibridoThree.setFace2Width(3)
    hibridoThree.setFace2Heigth(5)
    hibridoThree.setFace2DistanceFromOrigin(5.7)

    # Left face
    hibridoThree.setFace3Width(5.7)
    hibridoThree.setFace3Heigth(5)
    hibridoThree.setFace3DistanceFromOrigin(3)

    # Back Face
    hibridoThree.setFace4Width(3)
    hibridoThree.setFace4Heigth(5)
    hibridoThree.setFace4DistanceFromOrigin(5.7)

    # Top Face
    # hibridoThree.setFace5Width(5.7)
    # hibridoThree.setFace5Heigth(5.7)
    hibridoThree.setFace5Width(3)
    hibridoThree.setFace5Heigth(5.7)
    hibridoThree.setFace5DistanceFromOrigin(5)
    
    hibridoThree.draw()

    if os.name == "posix":
        txtIndex = 11
    else:
        txtIndex = 4
    hibridoThreeHelper = Edificio(textures = textures, position=[20,2,-12.7], scale=5, txtIndex=txtIndex)
    
    #Right face
    hibridoThreeHelper.setFace1Width(3)
    hibridoThreeHelper.setFace1Heigth(5)
    hibridoThreeHelper.setFace1DistanceFromOrigin(3)

    # Front face
    hibridoThreeHelper.setFace2Width(3)
    hibridoThreeHelper.setFace2Heigth(5)
    hibridoThreeHelper.setFace2DistanceFromOrigin(3)

    # Left face
    hibridoThreeHelper.setFace3Width(3)
    hibridoThreeHelper.setFace3Heigth(5)
    hibridoThreeHelper.setFace3DistanceFromOrigin(3)

    # Back Face
    hibridoThreeHelper.setFace4Width(3)
    hibridoThreeHelper.setFace4Heigth(5)
    hibridoThreeHelper.setFace4DistanceFromOrigin(3)

    # Top Face
    # hibridoThreeHelper.setFace5Width(5.7)
    # hibridoThreeHelper.setFace5Heigth(5.7)
    hibridoThreeHelper.setFace5Width(3)
    hibridoThreeHelper.setFace5Heigth(3)
    hibridoThreeHelper.setFace5DistanceFromOrigin(5)
    
    hibridoThreeHelper.draw()

    if os.name == "posix":
        txtIndex = 10
    else:
        txtIndex = 8
    polipropeno = Edificio(textures = textures, position=[17.3,2,4.5], scale=5, txtIndex=txtIndex)
    
    #Right face
    polipropeno.setFace1Width(4.5)
    polipropeno.setFace1Heigth(5)
    polipropeno.setFace1DistanceFromOrigin(5.5)

    # Front face
    polipropeno.setFace2Width(5.5)
    polipropeno.setFace2Heigth(5)
    polipropeno.setFace2DistanceFromOrigin(4.5)

    # Left face
    polipropeno.setFace3Width(4.5)
    polipropeno.setFace3Heigth(5)
    polipropeno.setFace3DistanceFromOrigin(5.5)

    # Back Face
    polipropeno.setFace4Width(5.5)
    polipropeno.setFace4Heigth(5)
    polipropeno.setFace4DistanceFromOrigin(4.5)

    # Top Face
    # polipropeno.setFace5Width(5.7)
    # polipropeno.setFace5Heigth(5.7)
    polipropeno.setFace5Width(5.5)
    polipropeno.setFace5Heigth(4.5)
    polipropeno.setFace5DistanceFromOrigin(5)
    
    polipropeno.draw()

    if os.name == "posix":
        txtIndex = 1
    else:
        txtIndex = 2
    bultosListos = Edificio(textures = textures, position=[17.3,2,20.7], scale=5, txtIndex=txtIndex)
    
    #Right face
    bultosListos.setFace1Width(6.4)
    bultosListos.setFace1Heigth(5)
    bultosListos.setFace1DistanceFromOrigin(5.5)

    # Front face
    bultosListos.setFace2Width(5.5)
    bultosListos.setFace2Heigth(5)
    bultosListos.setFace2DistanceFromOrigin(6.4)

    # Left face
    bultosListos.setFace3Width(6.4)
    bultosListos.setFace3Heigth(5)
    bultosListos.setFace3DistanceFromOrigin(5.5)

    # Back Face
    bultosListos.setFace4Width(5.5)
    bultosListos.setFace4Heigth(5)
    bultosListos.setFace4DistanceFromOrigin(6.4)

    # Top Face
    # .setFace5Width(5.7)
    # .setFace5Heigth(5.7)
    bultosListos.setFace5Width(5.5)
    bultosListos.setFace5Heigth(6.4)
    bultosListos.setFace5DistanceFromOrigin(5)
    
    bultosListos.draw()

    if os.name == "posix":
        txtIndex = 3
    else:
        txtIndex = 7
    oficina = Edificio(textures = textures, position=[17.3,2,32.2], scale=5, txtIndex=txtIndex)
    
    #Right face
    oficina.setFace1Width(2.2)
    oficina.setFace1Heigth(5)
    oficina.setFace1DistanceFromOrigin(5.5)

    # Front face
    oficina.setFace2Width(5.5)
    oficina.setFace2Heigth(5)
    oficina.setFace2DistanceFromOrigin(2.2)

    # Left face
    oficina.setFace3Width(2.2)
    oficina.setFace3Heigth(5)
    oficina.setFace3DistanceFromOrigin(5.5)

    # Back Face
    oficina.setFace4Width(5.5)
    oficina.setFace4Heigth(5)
    oficina.setFace4DistanceFromOrigin(2.2)

    # Top Face
    # .setFace5Width(5.7)
    # .setFace5Heigth(5.7)
    oficina.setFace5Width(5.5)
    oficina.setFace5Heigth(2.2)
    oficina.setFace5DistanceFromOrigin(5)
    
    oficina.draw()

    if os.name == "posix":
        txtIndex = 12
    else:
        txtIndex = 9
    tarimas = Edificio(textures = textures, position=[3,2,32.2], scale=5, txtIndex=txtIndex)
    
    #Right face
    tarimas.setFace1Width(2.2)
    tarimas.setFace1Heigth(2)
    tarimas.setFace1DistanceFromOrigin(5.5)

    # Front face
    tarimas.setFace2Width(5.5)
    tarimas.setFace2Heigth(2)
    tarimas.setFace2DistanceFromOrigin(2.2)

    # Left face
    tarimas.setFace3Width(2.2)
    tarimas.setFace3Heigth(2)
    tarimas.setFace3DistanceFromOrigin(5.5)

    # Back Face
    tarimas.setFace4Width(5.5)
    tarimas.setFace4Heigth(2)
    tarimas.setFace4DistanceFromOrigin(2.2)

    # Top Face
    # .setFace5Width(5.7)
    # .setFace5Heigth(5.7)
    tarimas.setFace5Width(5.5)
    tarimas.setFace5Heigth(2.2)
    tarimas.setFace5DistanceFromOrigin(2)
    
    tarimas.draw()

def lookAt(theta, pos):
    glLoadIdentity()
    rad = theta * math.pi / 180
    newX = Settings.EYE_X * math.cos(rad) + Settings.EYE_Z * math.sin(rad) + pos
    newZ = -Settings.EYE_X * math.sin(rad) + Settings.EYE_Z * math.cos(rad) + pos

    gluLookAt(
        newX,
        Settings.EYE_Y,
        newZ,
        Settings.CENTER_X,
        Settings.CENTER_Y,
        Settings.CENTER_Z,
        Settings.UP_X,
        Settings.UP_Y,
        Settings.UP_Z
    )	

def Simulacion(Options):
	# Variables para el control del observador
    global delta;
    global bolsas
    theta = 0
    pos = 0
    radius = Options.radious
    delta = Options.Delta
    Init(Options);
    cleanFile = open('Report.csv', 'w')
    cleanFile.close()
    csv = open('Report.csv', 'a')
    csv.write('tiempo,idMontacargas,nodosActuales,paquetesTrasladados,distanciaRecorrida,pesoLevantado\n')
    csv.close()

    cleanFile2 = open('Report2.csv', 'w')
    cleanFile2.close()
    csv2 = open('Report2.csv', 'a')
    csv2.write('tiempo,idPaquete,nodo\n')
    csv2.close()
    bolsaId = 0
    tiempo = []
    idMontacargas = []
    nodosActuales=[]
    paquetesTrasladados=[]
    distanciaRecorrida=[]
    pesoLevantado=[]
    while True:
        keys = pygame.key.get_pressed()  # Checking pressed keys
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                    pygame.quit()	
                    return

        if keys[pygame.K_RIGHT]:
            if theta > 359.0:
                theta = 0
            else:
                theta += 1.0
   

            lookAt(theta, pos)
        if keys[pygame.K_LEFT]:
            if theta < 1.0:
                theta = 360.0;
            else:
                theta -= 1.0
       
            lookAt(theta, pos)

            
        display()
        probability = 0.0015
        if numpy.random.rand(1)[0] < probability:
            bolsa = Bolsa([-260, 4, 233], textures, 1, 0)
            bolsas.append(bolsa)
        for bolsa in bolsas:
            bolsa.draw()
        checkCollisions()
        checkLifterInWeighingScale()
        checkLifterInMachinery()



        pygame.display.flip()
        pygame.time.wait(5)






