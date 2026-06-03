class Producto:
    """
    Ejercicio 3: Control de Inventario (Aplicación Completa)
    Objetivo: Integrar el encapsulamiento en una aplicación más compleja.
    """
    def __init__(self, nombre, stock_inicial):
        # Inicializa dos atributos privados: __nombre y __stock.
        self.__nombre = nombre
        self.__stock = int(stock_inicial)

    def obtener_info(self):
        """
        Devuelve una cadena con el nombre y el stock actual.
        """
        return f"Producto: {self.__nombre} | Stock actual: {self.__stock}"

    def aumentar_stock(self, cantidad):
        """
        Permite aumentar el stock si la cantidad es positiva.
        """
        if cantidad > 0:
            self.__stock += cantidad
            print(f"Se aumentaron {cantidad} unidades. Nuevo stock: {self.__stock}")
        else:
            print("Error: La cantidad a aumentar debe ser positiva.")

    def disminuir_stock(self, cantidad):
        """
        Permite disminuir el stock si la cantidad es positiva y hay suficiente disponible.
        """
        if cantidad <= 0:
            print("Error: La cantidad a disminuir debe ser positiva.")
        elif cantidad > self.__stock:
            print(f"Error: Stock insuficiente. Solo hay {self.__stock} unidades disponibles.")
        else:
            self.__stock -= cantidad
            print(f"Se disminuyeron {cantidad} unidades. Nuevo stock: {self.__stock}")

# Ejemplo de uso:
if __name__ == "__main__":
    p = Producto("Laptop", 10)
    print(p.obtener_info())
    
    p.aumentar_stock(5)
    p.disminuir_stock(3)
    p.disminuir_stock(20) # Error: insuficiente
    p.aumentar_stock(-5)  # Error: no positiva
    
    print(p.obtener_info())
