// Problema 9: Dado N, escribir el producto desde 1 hasta N.

function productoHastaN(n) {
    if (n < 0) return "N debe ser no negativo.";
    if (n === 0) return 1;
    let producto = 1;
    for (let i = 1; i <= n; i++) {
        producto *= i;
    }
    return producto;
}

// Ejemplo de uso:
const n = 5;
console.log(`El producto de 1 hasta ${n} es: ${productoHastaN(n)}`);
