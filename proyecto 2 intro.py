# proyecto 2 intro



# Importa la librería pygame para gráficos y manejo de eventos
import pygame
# Importa módulo random para operaciones aleatorias
import random
# Importa json para guardar/leer puntuaciones en formato JSON
import json
# Importa time para mediciones temporales simples
import time
# Importa collections por si se usan estructuras como deque, Counter, etc.
import collections
# Importa os para operaciones con sistema de archivos (rutas, existencias)
import os
# Importaciones de tipos para anotaciones estáticas (List, Tuple, Optional, Dict)
from typing import List, Tuple, Optional, Dict

# ----------------------------
# Configuración general
# ----------------------------
# Ancho de la ventana en píxeles
WINDOW_WIDTH = 960
# Alto de la ventana en píxeles
WINDOW_HEIGHT = 720
# Número de filas de la cuadrícula lógica
GRID_ROWS = 20
# Número de columnas de la cuadrícula lógica
GRID_COLS = 25
# Tamaño en píxeles de cada celda visible de la cuadrícula
CELL_SIZE = 28  # cuadrícula visible
# Cuadros por segundo objetivo (velocidad de actualización)
FPS = 20

# colores (tuplas RGB)
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (160,160,160)
DARKGRAY = (70,70,70)
GREEN = (50,200,50)
RED = (200,50,50)
BLUE = (50,50,200)
YELLOW = (230,230,30)
BROWN = (150,100,50)
PURPLE = (160,60,200)

# Nombre de archivo donde se guardan las puntuaciones
SCORES_FILE = "scores.json"

# ----------------------------
# Terrenos (cada uno como clase)
# ----------------------------
# Clase base que representa un tipo de terreno en la cuadrícula
class Terrain:
    # Identificador numérico del terreno (por defecto 0)
    id: int = 0
    # Nombre legible del terreno
    name: str = "Terrain"
    # Indica si el jugador puede caminar sobre este terreno
    walkable_for_player = True
    # Indica si los enemigos pueden caminar sobre este terreno
    walkable_for_enemy = True
    # Color por defecto para representar el terreno en pantalla
    color = GRAY

    # Representación en string de la clase/instancia (útil para depuración)
    def __repr__(self):
        return f"{self.name}"

# Subclase que representa un camino transitable por ambos
class Camino(Terrain):
    # Identificador específico de Camino
    id = 0
    # Nombre legible
    name = "Camino"
    # Jugador puede caminar
    walkable_for_player = True
    # Enemigos pueden caminar
    walkable_for_enemy = True
    # Color visual del camino
    color = (200,200,200)

# Subclase que representa un muro no transitable
class Muro(Terrain):
    # Identificador de Muro
    id = 1
    # Nombre legible
    name = "Muro"
    # Jugador NO puede caminar
    walkable_for_player = False
    # Enemigo NO puede caminar
    walkable_for_enemy = False
    # Color visual del muro
    color = (60,60,60)

# Subclase que representa lianas (obstáculo para jugador, transitable por enemigo)
class Lianas(Terrain):
    # Identificador de Lianas
    id = 2
    # Nombre legible
    name = "Lianas"
    # Jugador NO puede caminar (ej. requiere herramienta)
    walkable_for_player = False
    # Enemigos SÍ pueden moverse por las lianas
    walkable_for_enemy = True
    # Color representativo
    color = (34,139,34)

# Subclase que representa túnel (transitable por jugador, bloquea enemigos)
class Tunel(Terrain):
    # Identificador de Tunel
    id = 3
    # Nombre legible
    name = "Tunel"
    # Jugador puede pasar por túnel
    walkable_for_player = True
    # Enemigos NO pueden pasar
    walkable_for_enemy = False
    # Color representativo del túnel
    color = (135,206,235)
# Diccionario que asocia IDs numéricos de terreno con sus clases correspondientes.
TERRAINS = {
    0: Camino,   # Terreno transitable para jugador y enemigos
    1: Muro,     # Terreno bloqueante para ambos
    2: Lianas,   # Bloquea al jugador, permite enemigos
    3: Tunel,    # Permite jugador, bloquea enemigos
}

# ----------------------------
# Utilidades de mapa y generación
# ----------------------------

# Función que verifica si una celda (r,c) está dentro de los límites válidos del grid
def in_bounds(r,c):
    # Retorna True si fila y columna están dentro del rango permitido
    return 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS

# Generador que retorna vecinos ortogonales válidos (arriba, abajo, izquierda, derecha)
def neighbors(r,c):
    # Recorre desplazamientos verticales y horizontales
    for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        # Calcula nueva posición vecina
        nr, nc = r+dr, c+dc
        # Si el vecino está dentro del grid, se produce mediante yield
        if in_bounds(nr,nc):
            yield nr, nc

# Función principal que genera un laberinto y añade terrenos especiales
def generate_maze_with_features() -> List[List[int]]:
    # Crea una matriz llena de muros (1 = muro)
    grid = [[1 for _ in range(GRID_COLS)] for __ in range(GRID_ROWS)]

    # Función interna recursiva que excava el laberinto usando DFS
    def carve(r,c):
        # Lista de direcciones en saltos de 2 celdas (propio del maze generation)
        dirs = [(-2,0),(2,0),(0,-2),(0,2)]
        # Mezcla las direcciones para obtener laberintos distintos cada vez
        random.shuffle(dirs)
        # Itera sobre las direcciones en orden aleatorio
        for dr,dc in dirs:
            # Nueva posición candidata
            nr, nc = r+dr, c+dc
            # Si está dentro del grid y la celda destino aún es muro → se puede excavar
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and grid[nr][nc]==1:
                # Abre la celda final al convertirla en camino
                grid[nr][nc] = 0
                # Abre también la celda intermedia para conectar túnel
                grid[r+dr//2][c+dc//2] = 0
                # Llamada recursiva para extender el maze desde la nueva celda
                carve(nr,nc)

    # Determina celda inicial para el DFS, idealmente en posiciones impares del grid
    sr = 1 if GRID_ROWS>2 else 0
    sc = 1 if GRID_COLS>2 else 0
    # Marca celda inicial como camino
    grid[sr][sc] = 0
    # Genera el laberinto desde esa celda
    carve(sr,sc)

    # Tras el DFS, la matriz contiene un laberinto perfecto (0 caminos, 1 muros).
    # Ahora se reemplazan algunos caminos por túneles o lianas con cierta probabilidad.
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            # Solo modificamos si la celda es camino
            if grid[r][c] == 0:
                # Se toma un valor aleatorio para determinar el tipo de terreno
                p = random.random()
                # 5% de probabilidad de tunel
                if p < 0.05:
                    grid[r][c] = 3  # tunel
                # 7% siguiente de probabilidad de lianas
                elif p < 0.12:
                    grid[r][c] = 2  # lianas
                else:
                    # El resto sigue siendo camino
                    grid[r][c] = 0  
            else:
                # Los muros permanecen como muros
                grid[r][c] = 1

    # No se seleccionan aquí salida ni inicio; solo se retorna el grid generado
    return grid

# Encuentra aleatoriamente una celda que pertenezca a un conjunto de tipos permitidos
def find_random_cell_of_type(grid, allowed_types=[0]):
    # Intentos aleatorios para encontrar una celda válida
    tries = 0
    while tries < 1000:
        # Selecciona una fila aleatoria
        r = random.randrange(GRID_ROWS)
        # Selecciona una columna aleatoria
        c = random.randrange(GRID_COLS)
        # Verifica si la celda tiene un tipo permitido
        if grid[r][c] in allowed_types:
            return r,c
        # Incrementa contador
        tries += 1

    # Si falló en modo aleatorio, recorre secuencialmente toda la matriz
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            # Retorna la primera celda compatible que encuentre
            if grid[r][c] in allowed_types:
                return r,c

    # Si no se encuentra ninguna, se retorna un fallback (0,0)
    return 0,0