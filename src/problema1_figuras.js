/**
 * EVIDENCIA 2: Resolución a problemas algorítmicos aplicando estructuras de almacenamiento
 * Problema 1: Cálculo de Área y Perímetro de Figuras Planas
 * Código de Evidencia: GA3-220501093-AA3-EV02
 */

function calcularFiguras() {
    const seleccionMenu = prompt(
        "Seleccione la figura geométrica:\n1. Triángulo\n2. Rectángulo\n3. Cuadrado\n4. Círculo"
    );
    
    if (!seleccionMenu) return;

    const operacion = prompt("¿Qué desea calcular?\n1. Perímetro\n2. Área");
    if (!operacion) return;
    
    switch (seleccionMenu) {
        case "1": // Triángulo
            if (operacion === "1") {
                let a = parseFloat(prompt("Ingrese la longitud del lado 'a':"));
                let b = parseFloat(prompt("Ingrese la longitud de la base 'b':"));
                let c = parseFloat(prompt("Ingrese la longitud del lado 'c':"));
                let perimetro = a + b + c;
                alert(`El perímetro del Triángulo es: ${perimetro.toFixed(2)}`);
            } else {
                let b = parseFloat(prompt("Ingrese la longitud de la base 'b':"));
                let h = parseFloat(prompt("Ingrese la altura 'h':"));
                let area = (b * h) / 2;
                alert(`El área del Triángulo es: ${area.toFixed(2)}`);
            }
            break;
            
        case "2": // Rectángulo
            let bRect = parseFloat(prompt("Ingrese la base 'b':"));
            let aRect = parseFloat(prompt("Ingrese la altura 'a':"));
            if (operacion === "1") {
                let perimetro = 2 * (bRect + aRect);
                alert(`El perímetro del Rectángulo es: ${perimetro.toFixed(2)}`);
            } else {
                let area = bRect * aRect;
                alert(`El área del Rectángulo es: ${area.toFixed(2)}`);
            }
            break;
            
        case "3": // Cuadrado
            let lado = parseFloat(prompt("Ingrese la longitud del lado 'a':"));
            if (operacion === "1") {
                let perimetro = 4 * lado;
                alert(`El perímetro del Cuadrado es: ${perimetro.toFixed(2)}`);
            } else {
                let area = lado * lado;
                alert(`El área del Cuadrado es: ${area.toFixed(2)}`);
            }
            break;
            
        case "4": // Círculo
            let r = parseFloat(prompt("Ingrese el radio 'r':"));
            const PI = Math.PI;
            if (operacion === "1") {
                let perimetro = 2 * PI * r;
                alert(`El perímetro del Círculo es: ${perimetro.toFixed(2)}`);
            } else {
                let area = PI * (r ** 2);
                alert(`El área del Círculo es: ${area.toFixed(2)}`);
            }
            break;
            
        default:
            alert("Opción inválida.");
    }
}

// Para ejecutar en consola de navegador o entornos compatibles con prompt/alert
// calcularFiguras();
