// Problema 3: Escribir el algoritmo que permite calcular la nota correspondiente al primer parcial de “análisis” para un estudiante cualquiera. 
// Se debe considerar que hay dos talleres y un quiz, que en conjunto valen un 30 % de la nota 
// y el resto (70 %) corresponde a la nota del examen parcial.

function calcularNotaParcial(notaTalleresQuiz, notaExamenParcial) {
    const pesoTalleresQuiz = 0.30;
    const pesoExamenParcial = 0.70;
    const notaFinal = (notaTalleresQuiz * pesoTalleresQuiz) + (notaExamenParcial * pesoExamenParcial);
    return notaFinal.toFixed(2);
}

// Ejemplo de uso:
const talleresQuiz = 4.5;
const examen = 3.8;
console.log(`La nota final del parcial es: ${calcularNotaParcial(talleresQuiz, examen)}`);
