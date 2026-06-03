// Problema 6: Hacer un programa que sume 5 precios de camisas (en dólares) y que luego muestre el total de la venta en pesos.

function calcularVentaCamisas(preciosDolares, tipoCambio) {
    if (preciosDolares.length !== 5) {
        return "Debe ingresar exactamente 5 precios.";
    }
    const totalDolares = preciosDolares.reduce((sum, p) => sum + p, 0);
    const totalPesos = totalDolares * tipoCambio;
    return totalPesos.toFixed(2);
}

// Ejemplo de uso:
const precios = [15, 20, 10, 25, 30];
const trm = 4000;
console.log(`El total de la venta en pesos es: $${calcularVentaCamisas(precios, trm)}`);
