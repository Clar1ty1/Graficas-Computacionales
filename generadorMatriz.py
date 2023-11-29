import cv2
import numpy as np
import os

# Lista para almacenar los nodos con sus coordenadas
nodes = []
# Función para calcular la distancia entre dos puntos (nodos)
def calculate_distance(node1, node2):
    x1, y1 = node1
    x2, y2 = node2
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Función para actualizar la matriz de adyacencia
def update_adjacency_matrix(selected_nodes):
    num_nodes = len(selected_nodes)
    adjacency_matrix = np.zeros((num_nodes, num_nodes))

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            distance = calculate_distance(selected_nodes[i], selected_nodes[j])
            adjacency_matrix[i, j] = distance
            adjacency_matrix[j, i] = distance

    return adjacency_matrix

# Función para manejar los clics
def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Dimensiones del plano
        plano_width = 800  # (aproximadamente 200 * 2)
        plano_height = 505  # (aproximadamente 200 * 2)

        # Dimensiones de la pantalla
        screen_width = 1300
        screen_height = 800

        # Establecer la relación entre las coordenadas de la imagen y del plano
        escala_x = plano_width / screen_width
        escala_y = plano_height / screen_height

        # Convertir las coordenadas de la imagen a las coordenadas del plano
        x_plano = round(((x * escala_x) - (plano_width / 2))) + 100
        y_plano = round((y * escala_y) - (plano_height / 2)) - 45

        print("Nodo:", x_plano, y_plano)

        nodes.append((x_plano, y_plano))
        cv2.circle(img, (x, y), 10, (255, 255, 255), -1)
        cv2.imshow('image', img)
    pass

def handle_user_input():
    global nodes

    key = cv2.waitKey(0) & 0xFF

    if key == ord('q'):  # Presiona 'q' para salir
        return "quit"
    elif key == ord('c'):  # Presiona 'c' para calcular la matriz de adyacencia
        print("Llego")
        cv2.setMouseCallback('image', lambda *args: None)  # Deshabilita la detección de clics
        cv2.destroyAllWindows()

        print("Nodos registrados:", nodes)
        print("Numero de nodos: ", len(nodes))
        selected_nodes = []
        while True:
            connected_nodes = input("Cuáles nodos están conectados? (ejemplo: 1,2,3,4) ")
            connected_nodes = list(map(int, connected_nodes.split(',')))

            if all(node in range(1, len(nodes) + 1) for node in connected_nodes):
                selected_nodes = [nodes[node - 1] for node in connected_nodes]
                break
            else:
                print("Nodos no válidos. Inténtalo de nuevo.")

        adjacency_matrix = update_adjacency_matrix(selected_nodes)
        print("Matriz de adyacencia:")
        print(adjacency_matrix)
        file = open("Matriz.yaml", "w")
        file.write("Matriz : " + str(adjacency_matrix))
        file = open("Nodos.yaml", "w")
        file.write(str(nodes))
        return "calculate_matrix"

    return "continue"

def main(Options = ""):
    global img, nodes
    if os.name == "posix":
        img_path = "Materials/zPlano.jpeg"
    else:
        img_path = 'Materials\\zPlano.jpeg'

    img = cv2.imread(img_path, 1)

    if img is not None:
        cv2.imshow('image', img)
        cv2.setMouseCallback('image', click_event)
    else:
        print('Error al cargar la imagen')
        return

    while True:
        result = handle_user_input()
        
        if result == "quit":
            break
        elif result == "calculate_matrix":
            break

    cv2.destroyAllWindows()
