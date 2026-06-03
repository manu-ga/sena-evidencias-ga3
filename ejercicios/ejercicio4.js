// Problema 4: Un capital C está situado a un tipo de interés R anual ¿al término de cuántos años se doblará?

function calcularAniosParaDoblarCapital(tasaInteresAnual) {
    if (tasaInteresAnual <= 0) {
        return "La tasa de interés debe ser positiva.";
    }
    // Fórmula: C * (1 + R)^n = 2C => (1 + R)^n = 2 => n = log(2) / log(1 + R)
    const anios = Math.log(2) / Math.log(1 + (tasaInteresAnual / 100));
    return anios.toFixed(2);
}

// Ejemplo de uso:
const interes = 5; // 5% anual
console.log(`El capital se doblará en aproximadamente ${calcularAniosParaDoblarCapital(interes)} años`);
