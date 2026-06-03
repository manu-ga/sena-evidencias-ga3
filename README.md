# Evidencias GA3-220501093-AA2-EV03 - Programación Orientada a Objetos (SENA)

Este repositorio contiene las soluciones técnicas para la evidencia **GA3-220501093-AA2-EV03**, enfocada en el concepto de **Encapsulamiento** dentro de la Programación Orientada a Objetos (POO), utilizando el lenguaje **Python**.

## Descripción de la Actividad
Según las directrices del instructor Ricardo Alfonso González Vargas, se han implementado tres ejercicios prácticos que demuestran el uso de atributos privados, métodos getter/setter y el uso de decoradores `@property` para asegurar la integridad de los datos.

## Estructura del Repositorio
Los ejercicios están organizados en carpetas individuales dentro del directorio `python_encapsulamiento/`:

```text
sena-evidencias-ga3/
├── python_encapsulamiento/
│   ├── ejercicio1_persona/
│   │   └── persona.py       # Control de edad (0-120) con atributos privados.
│   ├── ejercicio2_coche/
│   │   └── coche.py         # Control de velocidad usando decoradores @property.
│   └── ejercicio3_producto/
│       └── producto.py      # Control de inventario (Stock) con validaciones.
└── README.md                # Guía del proyecto
```

## Detalle de los Ejercicios

### 1. Clase Persona (Protección de Edad)
Implementación de una clase donde el atributo `edad` es privado (`__edad`). Se utiliza un método `establecer_edad()` que valida que el valor esté en el rango de 0 a 120 años antes de realizar la asignación.

### 2. Clase Coche (Uso de @property)
Uso de decoradores estándar de Python para manejar el acceso a la velocidad. El setter valida que la velocidad no sea negativa y que no supere el límite máximo de 200 km/h.

### 3. Clase Producto (Control de Inventario)
Una aplicación más compleja que gestiona el stock de un producto. Incluye validaciones para asegurar que no se pueda aumentar stock con valores negativos ni disminuir más de lo que hay disponible en existencia.

## Requisitos de Ejecución
Para ejecutar estos scripts, debe tener instalado **Python 3.x**. Puede correr cada ejercicio desde la terminal:

```bash
python3 python_encapsulamiento/ejercicio1_persona/persona.py
python3 python_encapsulamiento/ejercicio2_coche/coche.py
python3 python_encapsulamiento/ejercicio3_producto/producto.py
```

## Autor
- **Aprendiz:** Manuel David Carvajal Machado
- **Programa:** Análisis y Desarrollo de Software
- **Instructor:** Ricardo Alfonso González Vargas
- **SENA**

---
*Evidencia técnica desarrollada para el módulo de Programación y Algoritmia.*
