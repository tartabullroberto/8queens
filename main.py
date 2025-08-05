import pygame
from nqueens_cython import NQueensGenerator
from collections import deque

class NQueensVisualizer:
    def __init__(self, n=8):
        self.n = n
        self.solutions_cache = deque(maxlen=1000)
        self.current_index = -1
        self.running = True
        self.auto_advance = False
        self.advance_speed = 1.0  # Segundos entre soluciones
        self.highlighted_queen = None
        
        pygame.init()
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        self.colors = {
            'light': (240, 217, 181),
            'dark': (181, 136, 99),
            'queen': (220, 20, 60),
            'background': (50, 50, 50),
            'panel': (70, 70, 70),
            'text': (255, 255, 255),
            'highlight': (100, 200, 255),
            'error': (255, 100, 100),
            'attack': (255, 255, 0, 100)
        }
        
        self.screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
        pygame.display.set_caption(f'N-Queens - {n}x{n}')
        self.reset_generator()
        self.update_controls()
        self.update_layout()

    def update_controls(self):
        """Actualiza la información de controles en el panel"""
        self.controls = [
            "CONTROLES:",
            "Flecha Izquierda: Solución siguiente",
            "Flecha Derecha: Solución anterior",
            "Espacio: Reproducir (On/Off)",
            "Flecha Arriba: +0.5s de delay",
            "Flecha Abajo: -0.5s de delay",
            "R: Reiniciar generador",
            "I: Incrementar tamaño (n)",
            "D: Decrementar tamaño (n)",
            "ESC: Salir",
            "",
            f"Detalles:",
            f"Tablero: {self.n}x{self.n}",
            f"Soluciones encontradas: {len(self.solutions_cache)}",
            f"Solución actual: {self.current_index + 1}",
            f"Reproducir: {'ON' if self.auto_advance else 'OFF'}",
            f"Velocidad: {self.advance_speed:.1f} seg/solución"
        ]

    def run(self):
        """Bucle principal de la aplicación"""
        clock = pygame.time.Clock()
        last_update = 0
        
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Manejar eventos de mouse
            mouse_pos = pygame.mouse.get_pos()
            self.highlighted_queen = self._get_queen_at_mouse_pos(mouse_pos)
            
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.update_layout()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        if not self.next_solution():
                            continue
                    elif event.key == pygame.K_LEFT:
                        self.previous_solution()
                    elif event.key == pygame.K_SPACE:
                        self.auto_advance = not self.auto_advance
                    elif event.key == pygame.K_DOWN:
                        # Aumentar velocidad (disminuir tiempo entre soluciones)
                        self.advance_speed = max(0.5, self.advance_speed - 0.5)
                        self.update_controls()
                    elif event.key == pygame.K_UP:
                        # Disminuir velocidad (aumentar tiempo entre soluciones)
                        self.advance_speed = min(5.0, self.advance_speed + 0.5)
                        self.update_controls()
                    elif event.key == pygame.K_r:
                        self.reset_generator()
                    elif event.key == pygame.K_i:  # Incrementar n
                        self.change_board_size(self.n + 1)
                    elif event.key == pygame.K_d:  # Decrementar n
                        if self.n > 1:  # No permitir n menor que 1
                            self.change_board_size(self.n - 1)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Reproducir
            if self.auto_advance and current_time - last_update > self.advance_speed * 1000:
                if not self.next_solution():
                    self.auto_advance = False
                last_update = current_time
            
            # Dibujar
            self.screen.fill(self.colors['background'])
            self.draw_panel()
            self.draw_board()
            
            pygame.display.flip()
            clock.tick(60)

    def change_board_size(self, new_n):
        """Cambia el tamaño del tablero y reinicia el generador"""
        self.n = new_n
        pygame.display.set_caption(f'N-Queens - {self.n}x{self.n}')
        self.reset_generator()
        self.update_controls()
        self.update_layout()

    def reset_generator(self):
        """Reinicia el generador de soluciones"""
        self.generator = NQueensGenerator(self.n).generate_solutions()
        self.solutions_cache.clear()
        self.current_index = -1
        self.has_solutions = True
        self._load_next_solution()  # Cargar primera solución

    def _load_next_solution(self):
        """Carga la siguiente solución del generador"""
        try:
            solution = next(self.generator)
            self.solutions_cache.append(solution)
            self.current_index = len(self.solutions_cache) - 1
            return True
        except StopIteration:
            if not self.solutions_cache:
                self.has_solutions = False
                self.current_solution = [0] * self.n
            return False

    def _get_current_solution(self):
        """Devuelve la solución actual"""
        if self.current_index >= 0:
            return self.solutions_cache[self.current_index]
        return [0] * self.n

    def update_layout(self):
        """Actualiza las dimensiones del tablero según el tamaño de la ventana"""
        window_width, window_height = self.screen.get_size()
        
        # Tamaño del panel lateral (ancho fijo)
        self.panel_width = 300
        
        # Calcular tamaño del tablero
        max_board_size = min(window_height - 40, window_width - self.panel_width - 40)
        self.square_size = max(5, int(max_board_size / self.n))
        self.board_size = self.square_size * self.n
        
        # Posición del tablero (centrado)
        self.board_offset_x = self.panel_width + (window_width - self.panel_width - self.board_size) // 2
        self.board_offset_y = (window_height - self.board_size) // 2

    def next_solution(self):
        """Avanza a la siguiente solución"""
        if not self.has_solutions:
            return False
        
        if self.current_index < len(self.solutions_cache) - 1:
            # Usar solución del cache
            self.current_index += 1
            return True
        else:
            # Cargar nueva solución
            if self._load_next_solution():
                return True
            return False

    def previous_solution(self):
        """Retrocede a la solución anterior"""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def draw_board(self):
        board_rect = pygame.Rect(
            self.board_offset_x, 
            self.board_offset_y, 
            self.board_size, 
            self.board_size
        )
        pygame.draw.rect(self.screen, self.colors['background'], board_rect)
        
        current_solution = self._get_current_solution()
        
        # Dibujar casillas normales
        for row in range(self.n):
            for col in range(self.n):
                rect = pygame.Rect(
                    self.board_offset_x + col * self.square_size,
                    self.board_offset_y + row * self.square_size,
                    self.square_size,
                    self.square_size
                )
                color = self.colors['light'] if (row + col) % 2 == 0 else self.colors['dark']
                pygame.draw.rect(self.screen, color, rect)
        
        # Resaltar trayectorias si hay una reina seleccionada
        if self.highlighted_queen:
            row, col = self.highlighted_queen
            self._draw_queen_attack_pattern(row, col)
        
        # Dibujar reinas
        for row in range(self.n):
            col = current_solution[row]
            if col >= 0:
                rect = pygame.Rect(
                    self.board_offset_x + col * self.square_size,
                    self.board_offset_y + row * self.square_size,
                    self.square_size,
                    self.square_size
                )
                center_x = rect.x + rect.width // 2
                center_y = rect.y + rect.height // 2
                radius = min(rect.width, rect.height) // 3
                pygame.draw.circle(self.screen, self.colors['queen'], (center_x, center_y), radius)

    def _draw_queen_attack_pattern(self, row, col):
        """Dibuja las casillas amenazadas por la reina en (row, col)"""
        s = self.square_size
        attack_surface = pygame.Surface((s, s), pygame.SRCALPHA)
        attack_surface.fill(self.colors['attack'])
        
        # Dibujar patrones de ataque
        for i in range(1, self.n):  # Comenzar desde 1 para omitir la posición actual
            # Horizontal
            if 0 <= col + i < self.n:
                self.screen.blit(attack_surface, 
                               (self.board_offset_x + (col + i) * s, self.board_offset_y + row * s))
            if 0 <= col - i < self.n:
                self.screen.blit(attack_surface,
                               (self.board_offset_x + (col - i) * s, self.board_offset_y + row * s))
            
            # Vertical
            if 0 <= row + i < self.n:
                self.screen.blit(attack_surface,
                               (self.board_offset_x + col * s, self.board_offset_y + (row + i) * s))
            if 0 <= row - i < self.n:
                self.screen.blit(attack_surface,
                               (self.board_offset_x + col * s, self.board_offset_y + (row - i) * s))
            
            # Diagonales (las 4 direcciones)
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                r, c = row + i*dr, col + i*dc
                if 0 <= r < self.n and 0 <= c < self.n:
                    self.screen.blit(attack_surface,
                                   (self.board_offset_x + c * s, self.board_offset_y + r * s))

    def _get_queen_at_mouse_pos(self, pos):
        """Devuelve (row, col) de la reina bajo el mouse, o None"""
        x, y = pos
        if not (self.board_offset_x <= x < self.board_offset_x + self.board_size and
                self.board_offset_y <= y < self.board_offset_y + self.board_size):
            return None
        
        col = (x - self.board_offset_x) // self.square_size
        row = (y - self.board_offset_y) // self.square_size
        
        current_solution = self._get_current_solution()
        if 0 <= row < self.n and current_solution[row] == col:
            return (row, col)
        return None

    def draw_panel(self):
        """Dibuja el panel lateral"""
        # Fondo del panel
        panel_rect = pygame.Rect(0, 0, self.panel_width, self.screen.get_height())
        pygame.draw.rect(self.screen, self.colors['panel'], panel_rect)
        
        # Título
        title = self.font.render(f"N-Queens {self.n}x{self.n}", True, self.colors['highlight'])
        self.screen.blit(title, (20, 20))
        
        # Actualizar controles
        self.update_controls()
        y_offset = 60
        for i, line in enumerate(self.controls):
            color = self.colors['highlight'] if i == 0 or i == 11 else self.colors['text']
            text = self.small_font.render(line, True, color)
            self.screen.blit(text, (20, y_offset))
            y_offset += 25
        
        # Mensaje si no hay soluciones
        if not self.has_solutions and not self.solutions_cache:
            error_msg = self.font.render("NO HAY SOLUCIONES", True, self.colors['error'])
            self.screen.blit(error_msg, (20, y_offset + 20))


if __name__ == "__main__":
    n = 8  # Tamaño del tablero (a partir de 32 falla)
    visualizer = NQueensVisualizer(n)
    visualizer.run()