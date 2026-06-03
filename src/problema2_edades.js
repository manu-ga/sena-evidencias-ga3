/**
 * EVIDENCIA 2: Resolución a problemas algorítmicos aplicando estructuras de almacenamiento
 * Problema 2: Análisis de Vector de Edades (10 Personas)
 * Código de Evidencia: GA3-220501093-AA3-EV02
 */

function analizarEdades() {
    let edades = [];
    const TOTAL_PERSONAS = 10;
    
    // Captura y validación de datos
    for (let i = 0; i < TOTAL_PERSONAS; i++) {
        let edadIngresada;
        let esValida = false;
        
        while (!esValida) {
            let input = prompt(`Persona ${i + 1}: Ingrese la edad (1-120 años):`);
            if (input === null) return; // Cancelar
            
            edadIngresada = parseInt(input);
            
            if (!isNaN(edadIngresada) && edadIngresada >= 1 && edadIngresada <= 120) {
                edades.push(edadIngresada);
                esValida = true;
            } else {
                alert("Error: La edad ingresada no es válida. Debe estar estrictamente entre 1 y 120 años.");
            }
        }
    }
    
    // Inicialización de variables analíticas
    let menoresDeEdad = 0;
    let mayoresDeEdad = 0;
    let adultosMayores = 0;
    let sumaEdades = 0;
    let edadMinima = edades[0];
    let edadMaxima = edades[0];
    
    // Procesamiento del vector
    for (let i = 0; i < edades.length; i++) {
        let edadActual = edades[i];
        sumaEdades += edadActual;
        
        // Clasificación por rangos
        if (edadActual < 18) {
            menoresDeEdad++;
        } else {
            mayoresDeEdad++;
        }
        
        if (edadActual >= 60) {
            adultosMayores++;
        }
        
        // Determinación de extremos
        if (edadActual < edadMinima) edadMinima = edadActual;
        if (edadActual > edadMaxima) edadMaxima = edadActual;
    }
    
    let promedio = sumaEdades / TOTAL_PERSONAS;
    
    // Despliegue estructurado de resultados
    let resultados = `--- RESULTADOS DEL ANÁLISIS DE EDADES ---
Edades registradas: [${edades.join(", ")}]
Cantidad de menores de edad: ${menoresDeEdad}
Cantidad de mayores de edad: ${mayoresDeEdad}
Cantidad de adultos mayores (>= 60 años): ${adultosMayores}
Edad más baja registrada: ${edadMinima} años
Edad más alta registrada: ${edadMaxima} años
Promedio general de edades: ${promedio.toFixed(2)} años`;

    console.log(resultados);
    alert(resultados);
}

// analizarEdades();
