class Coche:
    """
    Ejercicio 2: Coche y Velocidad (Mejora con Properties)
    Objetivo: Utilizar el decorador @property (getters y setters a la Python) para controlar el acceso a un atributo.
    """
    def __init__(self):
        # Inicializa un atributo privado llamado __velocidad a 0.
        self.__velocidad = 0

    @property
    def velocidad(self):
        """
        Método getter usando el decorador @property.
        """
        return self.__velocidad

    @velocidad.setter
    def velocidad(self, valor):
        """
        Método setter usando el decorador @velocidad.setter.
        Verifica que no sea negativo y que no supere los 200.
        """
        if valor < 0:
            print("Error: La velocidad no puede ser negativa.")
        elif valor > 200:
            print("Error: La velocidad máxima permitida es 200.")
        else:
            self.__velocidad = valor
            print(f"Velocidad actualizada a: {self.__velocidad}")

# Ejemplo de uso:
if __name__ == "__main__":
    mi_coche = Coche()
    print(f"Velocidad inicial: {mi_coche.velocidad}")
    
    mi_coche.velocidad = 120
    print(f"Velocidad actual: {mi_coche.velocidad}")
    
    mi_coche.velocidad = -10 # Error: negativa
    mi_coche.velocidad = 250 # Error: supera el máximo
    print(f"Velocidad final: {mi_coche.velocidad}")
