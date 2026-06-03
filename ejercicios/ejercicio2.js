// Problema 2: Realizar la conversión de una temperatura dada en grados Centígrados a grados Fahrenheit.
// Fórmula: F = (9/5) C + 32

function celsiusToFahrenheit(celsius) {
    const fahrenheit = (9 / 5) * celsius + 32;
    return fahrenheit.toFixed(2);
}

// Ejemplo de uso:
const gradosC = 25;
console.log(`${gradosC}°C equivalen a ${celsiusToFahrenheit(gradosC)}°F`);
