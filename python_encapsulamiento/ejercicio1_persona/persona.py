class Persona:
    """
    Ejercicio 1: Implementación de Control de Edad (Protección)
    Objetivo: Aplicar el encapsulamiento para asegurar que un atributo solo tome valores válidos.
    """
    def __init__(self):
        # El constructor inicializa un atributo privado llamado __edad con un valor inicial de 0.
        self.__edad = 0

    def establecer_edad(self, nueva_edad):
        """
        Actúa como setter. Solo permite la asignación si nueva_edad está entre 0 y 120.
        """
        if 0 <= nueva_edad <= 120:
            self.__edad = nueva_edad
            print(f"Edad establecida correctamente a: {self.__edad}")
        else:
            print("Error: La edad debe estar entre 0 y 120 años.")

    def obtener_edad(self):
        """
        Actúa como getter y retorna el valor actual de __edad.
        """
        return self.__edad

# Ejemplo de uso:
if __name__ == "__main__":
    p = Persona()
    print(f"Edad inicial: {p.obtener_edad()}")
    
    p.establecer_edad(25)
    print(f"Edad actual: {p.obtener_edad()}")
    
    p.establecer_edad(150) # Esto debería mostrar un error
    print(f"Edad final (sin cambios): {p.obtener_edad()}")
