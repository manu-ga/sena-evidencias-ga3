// Problema 1: Calcular el tiempo medio en minutos por kilómetro de un corredor de maratón.
// Un corredor de maratón (distancia 42,195 Km) ha recorrido la carrera en 2 horas 25 minutos. 
// Se desea un algoritmo que calcule el tiempo medio en minutos por kilómetro.

function calcularTiempoMedioMaraton(horas, minutos) {
    const distanciaKm = 42.195;
    const tiempoTotalMinutos = (horas * 60) + minutos;
    const tiempoMedioPorKm = tiempoTotalMinutos / distanciaKm;
    return tiempoMedioPorKm.toFixed(2);
}

// Ejemplo de uso:
const horas = 2;
const minutos = 25;
console.log(`El tiempo medio por kilómetro es: ${calcularTiempoMedioMaraton(horas, minutos)} minutos/km`);
