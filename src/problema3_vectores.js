/**
 * EVIDENCIA 2: Resolución a problemas algorítmicos aplicando estructuras de almacenamiento
 * Problema 3: Mezcla Ordenada de dos Vectores Ascendentes
 * Código de Evidencia: GA3-220501093-AA3-EV02
 */

function capturarVectorAscendente(nombreVector) {
    let vector = [];
    const TAMANO = 5;
    alert(`A continuación ingresará los 5 números del ${nombreVector} de forma estrictamente ascendente.`);
    
    for (let i = 0; i < TAMANO; i++) {
        let numero;
        let esValido = false;
        
        while (!esValido) {
            let input = prompt(`${nombreVector} - Posición ${i + 1}:`);
            if (input === null) return null;
            
            numero = parseInt(input);
            
            if (isNaN(numero)) {
                alert("Error: Ingrese un número válido.");
                continue;
            }

            if (i > 0 && numero <= vector[i - 1]) {
                alert(`Error: El número debe ser mayor que el anterior (${vector[i - 1]}).`);
            } else {
                vector.push(numero);
                esValido = true;
            }
        }
    }
    return vector;
}

function unificarVectores() {
    let vector1 = capturarVectorAscendente("Vector A");
    if (!vector1) return;

    let vector2 = capturarVectorAscendente("Vector B");
    if (!vector2) return;

    // Unificar y ordenar (Mezcla)
    let listaUnificada = [...vector1, ...vector2].sort((a, b) => a - b);

    let resultado = `--- MEZCLA DE VECTORES ---
Vector A: [${vector1.join(", ")}]
Vector B: [${vector2.join(", ")}]
Lista Unificada Ordenada: [${listaUnificada.join(", ")}]`;

    console.log(resultado);
    alert(resultado);
}

// unificarVectores();
