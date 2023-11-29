import cv2
import numpy as np

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
        x_n = round((x * 175) / 1032)
        y_n = round((y * 100) / 589)
        print("Nodo:", x_n, y_n)

        nodes.append((x_n, y_n))
        cv2.circle(img, (x, y), 10, (255, 255, 255), -1)
        cv2.imshow('image', img)

def main(Options):
    global img 
    img = cv2.imread('./Materials/zPlano.png', 1)
    cv2.imshow('image', img)
    cv2.setMouseCallback('image', click_event)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Presiona 'q' para salir
            break
        elif key == ord('c'):  # Presiona 'c' para calcular la matriz de adyacencia
            cv2.setMouseCallback('image', lambda *args: None)  # Deshabilita la detección de clics
            cv2.destroyAllWindows()

            print("Nodos registrados:", nodes)
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
            break

    cv2.destroyAllWindows()