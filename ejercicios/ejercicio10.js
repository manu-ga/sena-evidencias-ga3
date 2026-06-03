// Problema 10: Realizar un algoritmo que muestre por pantalla la tabla de multiplicar decreciente 
// de cualquier número, ingresado entre el 1 y el 10.

function tablaMultiplicarDecreciente(numero) {
    if (numero < 1 || numero > 10) {
        return "El número debe estar entre 1 y 10.";
    }
    console.log(`Tabla del ${numero} (Decreciente):`);
    for (let i = 10; i >= 1; i--) {
        console.log(`${numero} x ${i} = ${numero * i}`);
    }
}

// Ejemplo de uso:
tablaMultiplicarDecreciente(7);
