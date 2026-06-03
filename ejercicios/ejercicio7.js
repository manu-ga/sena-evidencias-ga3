// Problema 7: Hacer un programa que registre el consumo realizado por los clientes de un restaurante, 
// si el consumo de cada cliente excede 50000 se hará un descuento del 20 %. 
// Se debe mostrar el pago de cada cliente y el total de todos los pagos.

function calcularConsumoRestaurante(consumos) {
    const umbral = 50000;
    const descuento = 0.20;
    let totalGeneral = 0;

    console.log("Detalle de pagos:");
    consumos.forEach((consumo, index) => {
        let pago = consumo;
        if (consumo > umbral) {
            pago = consumo * (1 - descuento);
        }
        totalGeneral += pago;
        console.log(`Cliente ${index + 1}: Consumo $${consumo} -> Pago Final $${pago.toFixed(2)}`);
    });

    console.log(`Total de todos los pagos: $${totalGeneral.toFixed(2)}`);
}

// Ejemplo de uso:
const consumosClientes = [60000, 45000, 80000, 30000];
calcularConsumoRestaurante(consumosClientes);
