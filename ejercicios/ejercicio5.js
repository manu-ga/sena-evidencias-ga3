// Problema 5: Elaborar un algoritmo que permita ingresar 20 números y muestre todos los números menores e iguales a 25.

function filtrarNumerosMenoresIguales25(numeros) {
    if (numeros.length !== 20) {
        return "Debe ingresar exactamente 20 números.";
    }
    return numeros.filter(num => num <= 25);
}

// Ejemplo de uso:
const listaNumeros = [10, 30, 5, 22, 40, 15, 25, 8, 12, 50, 3, 18, 28, 7, 11, 35, 1, 20, 45, 19];
console.log("Números menores o iguales a 25:", filtrarNumerosMenoresIguales25(listaNumeros));
