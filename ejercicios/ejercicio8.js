// Problema 8: Diseñar un algoritmo que permita ingresar la hora, minutos y segundos, 
// y que calcule la hora en el siguiente segundo ("0<= H <=23", "0<= M <=59" "0<= S<=59").

function siguienteSegundo(h, m, s) {
    s++;
    if (s >= 60) {
        s = 0;
        m++;
        if (m >= 60) {
            m = 0;
            h++;
            if (h >= 24) {
                h = 0;
            }
        }
    }
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// Ejemplo de uso:
console.log(`La hora en el siguiente segundo es: ${siguienteSegundo(23, 59, 59)}`);
