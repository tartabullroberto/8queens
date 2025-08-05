# cython: language_level=3

from libc.stdint cimport uint64_t
from cpython cimport array
import array

cdef class NQueensGenerator:
    cdef int n
    cdef int[:] current_solution
    
    def __init__(self, int n):
        if n < 1 or n > 32:
            raise ValueError("El tamaño del tablero debe estar entre 1 y 32")
        self.n = n
        self.current_solution = array.array('i', [0] * n)
    
    def generate_solutions(self):
        """Generador principal con enfoque iterativo"""
        # Casos base conocidos
        if self.n == 1:
            yield [0]
            return
        if self.n in {2, 3}:
            return
        
        # Stack para simular la recursión
        cdef uint64_t cols, diag1, diag2, available, col
        cdef int row, col_pos
        cdef list stack = []
        
        # Estado inicial: (cols, diag1, diag2, row, parent_solution)
        stack.append((0, 0, 0, 0, array.array('i', [0] * self.n)))
        
        while stack:
            cols, diag1, diag2, row, parent_solution = stack.pop()
            
            # Restaurar la solución actual
            for i in range(self.n):
                self.current_solution[i] = parent_solution[i]
            
            if row == self.n:
                yield list(self.current_solution)
                continue
            
            available = (~(cols | diag1 | diag2)) & ((1 << self.n) - 1)
            
            while available:
                col = available & -available
                col_pos = self._bit_position(col)
                self.current_solution[row] = col_pos
                
                # Crear una copia de la solución actual
                child_solution = array.array('i', [0] * self.n)
                for i in range(self.n):
                    child_solution[i] = self.current_solution[i]
                
                # Guardar el estado actual para procesar después
                stack.append((
                    cols | col,
                    (diag1 | col) << 1,
                    (diag2 | col) >> 1,
                    row + 1,
                    child_solution
                ))
                
                available &= available - 1
    
    cdef inline int _bit_position(self, uint64_t num):
        """Encuentra la posición del bit más bajo"""
        if num == 0:
            return -1
        cdef int pos = 0
        while (num & 1) == 0:
            num >>= 1
            pos += 1
        return pos