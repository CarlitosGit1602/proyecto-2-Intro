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

# ----------------------------
# Pathfinding: BFS en terreno permitido
# ----------------------------
def bfs_shortest_path(grid, start, goal, for_enemy=True):
    # Se crea una cola doble (deque) para implementar BFS
    q = collections.deque()
    # Se inicializa la cola con la posición inicial
    q.append(start)

    # Diccionario que almacena de dónde venimos para reconstruir el camino
    prev = {start: None}

    # Mientras haya nodos por explorar
    while q:
        cur = q.popleft()   # Se obtiene la posición actual desde el frente de la cola
        # Si ya alcanzamos la meta, debemos reconstruir el camino
        if cur == goal:
            path = []   # Lista para guardar el camino
            # Comenzamos desde la meta y seguimos los padres hacia atrás
            node = cur
            while node:
                path.append(node)
                node = prev[node]
            path.reverse()  # Como se reconstruye al revés, se invierte
            return path

        # Extraemos fila y columna actual
        r,c = cur

        # Recorremos vecinos válidos 
        for nr,nc in neighbors(r,c):
            # Solo procesamos vecinos no visitados previamente
            if (nr,nc) not in prev:
                # Obtenemos el tipo de terreno numérico
                t = grid[nr][nc]
                # Obtenemos la clase de terreno asociada
                cls = TERRAINS.get(t, Camino)

                # Según si el BFS es para enemigo o para jugador, revisamos si ese terreno es transitable
                if for_enemy:
                    # Caminable por enemigo
                    if cls.walkable_for_enemy:
                        prev[(nr,nc)] = cur
                        q.append((nr,nc))
                else:
                    # Caminable por jugador
                    if cls.walkable_for_player:
                        prev[(nr,nc)] = cur
                        q.append((nr,nc))
    # Si se agotó BFS (Busaqueda por amplitud) sin encontrar ruta, no hay camino posible
    return None

class Player:
    def __init__(self, r, c, name="Player"):
        # Posición de la celda del jugador
        self.r = r
        self.c = c
        # Nombre del jugador
        self.name = name

        # Energía actual y máxima del jugador
        self.energy = 100.0
        self.max_energy = 100.0

        # Coste por segundo de usar sprint
        self.sprint_cost = 25.0
        # Velocidad al hacer sprint (tiles por tick)
        self.sprint_speed = 2
        # Velocidad normal del jugador
        self.base_speed = 1

        # Bandera que indica si el jugador está esprintando
        self.sprinting = False

        # Número de trampas que puede colocar
        self.traps_available = 3
        # Tiempo mínimo entre colocaciones
        self.trap_cooldown = 5.0
        # Última vez en que colocó una trampa
        self.last_trap_time = -999.0

        # Puntuación acumulada
        self.score = 0

        # Estado de vida (para terminar juego)
        self.alive = True

    # Determina si el jugador puede o no colocar una trampa
    def can_place_trap(self, now, active_traps_count):
        # Limitación: máximo 3 trampas activas simultáneamente
        if active_traps_count >= 3:
            return False
        # Limitación de cooldown entre uso
        if now - self.last_trap_time < self.trap_cooldown:
            return False
        # Si pasó el cooldown y no hay exceso de trampas, puede colocar
        return True

class Enemy:
    def __init__(self, r, c, id_=0):
        # Posición del enemigo
        self.r = r
        self.c = c
        # ID para distinguir enemigos
        self.id = id_

        # Si está vivo (puede morir por trampas)
        self.alive = True

        # Cuando muere se programa un respawn (segundos en el futuro)
        self.respawn_time = None

        # Velocidad del enemigo en tiles por tick
        self.speed = 1

        # Enemigos se mueven cada cierto tiempo (cooldown en segundos)
        self.move_cooldown = 1.0

        # Última vez que se movió
        self.last_move = 0.0

    # Retorna la posición como tupla (r,c)
    def as_tuple(self):
        return (self.r, self.c)

class Trap:
    def __init__(self, r,c, placed_time):
        # Trampa colocada en una celda específica
        self.r = r
        self.c = c
        # Momento exacto en que fue puesta (para expiración)
        self.placed_time = placed_time
        
        
        
# ----------------------------
# Manejo de puntuacion
# ----------------------------
def load_scores():
    # Verifica si existe el archivo de puntajes
    if os.path.exists(SCORES_FILE):
        try:
            # Intenta cargarlo y devolver su contenido dict
            with open(SCORES_FILE,"r") as f:
                return json.load(f)
        except Exception:
            pass
    # Si no existe o falla lectura, crea estructura base con dos modos
    # "escapa" y "cazador" cada uno con una lista de puntajes
    return {"escapa": [], "cazador": []}

def save_scores(scores):
    # Guarda la estructura de puntajes en JSON con indentación
    with open(SCORES_FILE,"w") as f:
        json.dump(scores, f, indent=2)

def update_top(scores, mode_key, player_name, score):
    # Obtiene el arreglo de puntajes de un modo concreto
    arr = scores.get(mode_key, [])
    # Añade el nuevo puntaje
    arr.append({"name":player_name, "score":score})

    # Ordena de mayor a menor puntaje y toma solo los 5 mejores
    arr = sorted(arr, key=lambda x: x["score"], reverse=True)[:5]

    # Actualiza estructura
    scores[mode_key] = arr

    # Guarda cambios
    save_scores(scores)


def draw_text(surface, text, x, y, size=20, color=WHITE):
    # Crea una fuente del sistema usando Arial y tamaño indicado
    font = pygame.font.SysFont("Arial", size)
    # Renderiza el texto en color especificado
    text_surf = font.render(text, True, color)
    # Dibuja el texto en la superficie (pantalla o subsuperficie)
    surface.blit(text_surf, (x,y))

# ----------------------------
# Clase del juego (principal)
# ----------------------------
class Game:
    # Constructor de la clase Game: inicializa Pygame, ventana, estado y valores por defecto
    def __init__(self):
        # Inicializa todos los módulos de pygame
        pygame.init()
        # Establece el título de la ventana
        pygame.display.set_caption("Escapa / Cazador")
        # Crea la ventana con tamaño predeterminado (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        # Reloj para controlar FPS y tiempos
        self.clock = pygame.time.Clock()
        # Flag para el bucle principal del juego
        self.running = True

        # Estado general del juego
        # Genera un laberinto/mapa con características (función externa)
        self.grid = generate_maze_with_features()
        # Modo actual de la interfaz: 'menu', 'escapa', 'cazador', 'playing', 'gameover'
        self.mode = "menu"
        # Nombre del jugador (se completa en registro)
        self.player_name = None

        # Entidades dinámicas del juego (se crearán en reset_game_state)
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.traps: List[Trap] = []
        # Carga puntuaciones/leaderboard desde almacenamiento persistente
        self.scores = load_scores()
        # Marca de tiempo de inicio (para medir tiempo jugado)
        self.start_time = time.time()
        # Tiempo transcurrido acumulado
        self.elapsed_time = 0.0

        # Ajustes de control / dificultad por defecto
        self.num_enemies = 4
        # Factor usado como cooldown de movimiento (más bajo = más rápido)
        self.enemy_speed = 1.0
        self.difficulty = "Normal"

        # Contador de frames (puede usarse para animaciones, ticks, etc.)
        self.frame_count = 0

        # Campos usados por el menú / registro
        self.input_text = ""
        # Fuente por defecto para textos del menú
        self.font = pygame.font.SysFont("Arial", 20)

        # Posiciones/layout: origen donde se dibuja la rejilla
        self.grid_origin = (20,20)
        # Posición X del HUD (a la derecha de la rejilla)
        self.hud_x = self.grid_origin[0] + GRID_COLS*CELL_SIZE + 20

        # Crea el estado inicial del mapa, jugador y enemigos
        self.reset_game_state()

    # Reinicia o inicializa el estado del juego (mapa, jugador, enemigos, trampas)
    def reset_game_state(self):
        # Regenera el laberinto con características (puertas, lianas, etc.)
        self.grid = generate_maze_with_features()
        # Selecciona aleatoriamente una celda de tipo transitable (camino o túnel) para el jugador
        pr, pc = find_random_cell_of_type(self.grid, allowed_types=[0,3])
        # Inicializa la celda de salida con la posición del jugador (se buscará una lejana)
        exit_r, exit_c = pr, pc
        # Calcula la celda más lejana (Manhattan) para colocar la salida
        maxdist = -1
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                # Considera solo celdas transitables (0=camino, 3=túnel)
                if self.grid[r][c] in (0,3):
                    dist = abs(r-pr) + abs(c-pc)
                    # Si la distancia es mayor, actualiza la celda de salida
                    if dist > maxdist:
                        exit_r, exit_c = r, c
                        maxdist = dist
        # Asegura conectividad entre jugador y salida: intenta buscar un camino válido
        attempts = 0
        while True:
            # Busca el camino más corto desde player a exit (para pathfinding de jugador)
            path = bfs_shortest_path(self.grid, (pr,pc), (exit_r,exit_c), for_enemy=False)
            # Si existe un camino, salimos del bucle
            if path:
                break
            # Si no hay camino, se reintenta hasta un límite, regenerando mapa si es necesario
            attempts += 1
            if attempts > 8:
                # Forzar nueva generación de mapa y nuevos puntos de inicio/salida
                self.grid = generate_maze_with_features()
                pr,pc = find_random_cell_of_type(self.grid, allowed_types=[0,3])
                exit_r, exit_c = find_random_cell_of_type(self.grid, allowed_types=[0,3])
                attempts = 0
            else:
                # Cambia la celda de salida por otra aleatoria y vuelve a verificar
                exit_r, exit_c = find_random_cell_of_type(self.grid, allowed_types=[0,3])

        # Crea la entidad Player en la posición elegida; usa player_name si existe o "ANON"
        self.player = Player(pr,pc,self.player_name or "ANON")
        # Guarda la celda de salida
        self.exit_cell = (exit_r, exit_c)
        # Lista de enemigos vacía (se llenará a continuación)
        self.enemies = []
        # Coloca enemigos en celdas permisibles (no demasiado cerca del jugador)
        placed = 0
        tries = 0
        while placed < self.num_enemies and tries < 1000:
            # Busca celdas donde los enemigos puedan aparecer (lianas o caminos)
            er, ec = find_random_cell_of_type(self.grid, allowed_types=[0,2])
            # Solo coloca si la distancia Manhattan al jugador es mayor a 6 (evita spawn inmediato)
            if abs(er-pr)+abs(ec-pc) > 6:
                # Crea enemigo con id incremental
                self.enemies.append(Enemy(er,ec, id_=placed))
                placed += 1
            tries += 1
        # Si no se colocó ninguno (caso raro), los genera en bordes como fallback
        if not self.enemies:
            for i in range(self.num_enemies):
                self.enemies.append(Enemy(0, i*2+1, id_=i))

        # Inicializa lista de trampas vacía
        self.traps = []
        # Reinicia tiempo de inicio
        self.start_time = time.time()
        # Flags de estado de juego
        self.game_over = False
        self.won = False

    # Dibuja y maneja la pantalla de registro (entrada de nombre y selección de modo)
    def handle_registration(self):
        # Limpia la pantalla pintando fondo negro
        self.screen.fill(BLACK)
        # Dibuja texto instructivo en la pantalla de registro
        draw_text(self.screen, "REGISTRO - Ingrese nombre (obligatorio) y presione Enter", 50, 30, size=22, color=WHITE)
        # Dibuja un rectángulo que actúa como caja de entrada visual
        pygame.draw.rect(self.screen, WHITE, (50,80,400,36), 2)
        # Renderiza el texto actualmente tecleado por el usuario
        txt_surf = self.font.render(self.input_text, True, WHITE)
        # Coloca el texto dentro de la caja de entrada (ligeramente desplazado)
        self.screen.blit(txt_surf, (58,88))
        # Instrucciones para seleccionar modo ESCAPA
        draw_text(self.screen, "Presione 1 para Modo ESCAPA (huir).", 50, 140)
        # Instrucciones para seleccionar modo CAZADOR
        draw_text(self.screen, "Presione 2 para Modo CAZADOR (cazar).", 50, 170)
        # Instrucciones para regenerar/actualizar el mapa si el usuario lo desea
        draw_text(self.screen, "Presione R para generar/actualizar mapa aleatorio", 50, 210)
        # Crea una superficie pequeña para previsualizar el mapa actual (miniatura)
        preview_surface = pygame.Surface((GRID_COLS*6, GRID_ROWS*6))
        # Llena la miniatura con negro como fondo
        preview_surface.fill(BLACK)
        # Recorre cada celda de la rejilla para pintar la miniatura
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                # Obtiene el valor de terreno en la celda
                val = self.grid[r][c]
                # Mapea el valor a la clase de terreno (fallback Camino)
                cls = TERRAINS.get(val, Camino)
                # Obtiene el color asociado al tipo de terreno
                color = cls.color
                # Dibuja un rectángulo pequeño representando la celda en la miniatura
                pygame.draw.rect(preview_surface, color, (c*6, r*6, 6, 6))
        # Blitea la miniatura en la ventana principal en posición (500,80)
        self.screen.blit(preview_surface, (500, 80))
        # Actualiza la pantalla para mostrar todo lo dibujado en este método
        pygame.display.flip()

    def draw_grid(self):
        # obtiene origen de dibujo (offset) en pantalla
        ox, oy = self.grid_origin
        # recorre filas de la rejilla
        for r in range(GRID_ROWS):
            # recorre columnas de la rejilla
            for c in range(GRID_COLS):
                # valor numérico del terreno en la celda (ej. camino, muro, liana, túnel...)
                val = self.grid[r][c]
                # obtiene la clase/definición del terreno a partir del mapa TERRAINS (fallback Camino)
                cls = TERRAINS.get(val, Camino)
                # color asociado al tipo de terreno
                color = cls.color
                # rectángulo donde se dibujará la celda (se deja 1px de separación visual)
                rect = pygame.Rect(ox + c*CELL_SIZE, oy + r*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1)
                # dibuja la celda en pantalla con su color
                pygame.draw.rect(self.screen, color, rect)
                # mark exit
        # dibuja rectángulo resaltando la celda de salida (exit_cell)
        er,ec = self.exit_cell
        pygame.draw.rect(self.screen, YELLOW, (ox + ec*CELL_SIZE, oy + er*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))

    def draw_entities(self):
        # obtiene offsets de dibujo
        ox, oy = self.grid_origin
        # dibuja jugador: obtiene posición de fila/columna
        pr,pc = self.player.r, self.player.c
        # dibuja rectángulo azul representando al jugador (ligeramente inset para verse mejor)
        pygame.draw.rect(self.screen, BLUE, (ox + pc*CELL_SIZE+4, oy + pr*CELL_SIZE+4, CELL_SIZE-8, CELL_SIZE-8))
        # dibuja enemigos
        for e in self.enemies:
            # solo dibuja si el enemigo está vivo
            if e.alive:
                # rectángulo rojo para enemigo (más pequeño que el jugador por margen visual)
                pygame.draw.rect(self.screen, RED, (ox + e.c*CELL_SIZE+6, oy + e.r*CELL_SIZE+6, CELL_SIZE-12, CELL_SIZE-12))
        # dibuja trampas
        for t in self.traps:
            # dibuja un círculo morado centrado en la celda de la trampa
            pygame.draw.circle(self.screen, PURPLE, (ox + t.c*CELL_SIZE+CELL_SIZE//2, oy + t.r*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//3)