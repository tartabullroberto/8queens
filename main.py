import pygame
import sys
from itertools import cycle

def solve_n_queens(n):
    def is_safe(board, row, col):
        for i in range(row):
            if board[i] == col or \
               board[i] - i == col - row or \
               board[i] + i == col + row:
                return False
        return True
    
    def backtrack(row):
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(row + 1)
                board[row] = -1
    
    solutions = []
    board = [-1] * n
    backtrack(0)
    return solutions

def draw_board(screen, n, solution, square_size, colors, offset_x, offset_y):
    screen.fill(colors['background'])
    
    # Dibuja el tablero
    for row in range(n):
        for col in range(n):
            color = colors['light'] if (row + col) % 2 == 0 else colors['dark']
            pygame.draw.rect(screen, color, 
                            (offset_x + col * square_size, 
                             offset_y + row * square_size, 
                             square_size, square_size))
    
    # Dibuja las reinas
    for row, col in enumerate(solution):
        center_x = offset_x + col * square_size + square_size // 2
        center_y = offset_y + row * square_size + square_size // 2
        
        # reina
        pygame.draw.circle(screen, colors['queen'], 
                          (center_x, center_y), square_size // 2.5)

def create_text_with_background(text, font, text_color, bg_color, alpha=128):
    """Crea una superficie de texto con fondo semi-transparente"""
    text_surface = font.render(text, True, text_color)
    bg_surface = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10), pygame.SRCALPHA)
    bg_surface.fill((*bg_color[:3], alpha)) 
    bg_surface.blit(text_surface, (10, 5))
    
    return bg_surface

def main():
    pygame.init()
    pygame.font.init()
    
    # Configuración
    n = 8  # Tamaño del tablero (puedes cambiarlo)
    window_size = 600
    colors = {
        'light': (240, 217, 181),
        'dark': (181, 136, 99),
        'queen': (220, 20, 60),
        'queen_crown': (255, 215, 0),
        'background': (50, 50, 50),
        'text': (245, 245, 245),
        'text_bg': (0, 0, 0, 50)
    }
    
    square_size = window_size // (n + 1)
    board_size = n * square_size
    
    # Calcular offsets para centrar el tablero
    offset_x = (window_size - board_size) // 2
    offset_y = (window_size - board_size) // 2
    
    # Resolver el problema
    solutions = solve_n_queens(n)
    if not solutions:
        print("No hay soluciones para el tamaño de tablero seleccionado.")
        pygame.quit()
        sys.exit()
    
    # Configurar la ventana
    screen = pygame.display.set_mode((window_size, window_size))
    pygame.display.set_caption(f'Problema de las {n} Reinas')
    font = pygame.font.SysFont('Arial', 24, bold=True)
    
    # Ciclo de soluciones
    solutions_cycle = cycle(solutions)
    current_solution = next(solutions_cycle)
    solution_count = 0
    total_solutions = len(solutions)

    # Bucle principal
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_solution = next(solutions_cycle)
                    solution_count = (solution_count + 1) % total_solutions
                    last_change = current_time
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    # Retroceder a la solución anterior
                    for _ in range(total_solutions - 1):
                        current_solution = next(solutions_cycle)
                    solution_count = (solution_count - 1) % total_solutions
                    last_change = current_time
                elif event.key == pygame.K_RIGHT:
                    # Avanzar a la siguiente solución
                    current_solution = next(solutions_cycle)
                    solution_count = (solution_count + 1) % total_solutions
                    last_change = current_time
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic izquierdo
                    current_solution = next(solutions_cycle)
                    solution_count = (solution_count + 1) % total_solutions
                    last_change = current_time
        
        # Dibujar
        draw_board(screen, n, current_solution, square_size, colors, offset_x, offset_y)
        
        # Información
        solution_text = f"Solución {solution_count + 1} de {total_solutions}"
        controls_text = "Espacio/Flechas/Clic: Cambiar solución"
        
        # Crear superficies de texto
        solution_surface = create_text_with_background(
            solution_text, font, colors['text'], colors['text_bg'], colors['text_bg'][3])
        controls_surface = create_text_with_background(
            controls_text, font, colors['text'], colors['text_bg'], colors['text_bg'][3])
        
        screen.blit(solution_surface, (20, 20))
        screen.blit(controls_surface, (20, window_size - 40))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()