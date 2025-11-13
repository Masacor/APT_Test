// Convertimos los datos desde JSON a objetos JS
const edadDataRaw = JSON.parse(document.getElementById('edadData').textContent);
const registroData = JSON.parse(document.getElementById('registroData').textContent);
const comunaData = JSON.parse(document.getElementById('comunaData').textContent);

// -------------------- Agrupar por rango de edad --------------------
function agruparPorRango(edades, valores, rango=10) {
    let rangoDict = {};
    edades.forEach((edad, i) => {
        const inicio = Math.floor(edad / rango) * rango;
        const fin = inicio + rango - 1;
        const key = `${inicio}-${fin}`;
        if (!rangoDict[key]) rangoDict[key] = 0;
        rangoDict[key] += valores[i];
    });

    // Ordenar rangos
    const sortedKeys = Object.keys(rangoDict).sort(
        (a, b) => parseInt(a.split('-')[0]) - parseInt(b.split('-')[0])
    );
    const sortedValues = sortedKeys.map(k => rangoDict[k]);

    return { labels: sortedKeys, data: sortedValues };
}

const edadData = agruparPorRango(edadDataRaw.labels, edadDataRaw.data);

// -------------------- Gráfico de edades por rango --------------------
new Chart(document.getElementById('edadChart'), {
    type: 'bar', // barras verticales
    data: {
        labels: edadData.labels, // Rango de edad en eje X
        datasets: [{
            label: 'Cantidad de usuarios', // eje Y
            data: edadData.data,
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: { display: true, text: 'Rango de edad' }
            },
            y: {
                beginAtZero: true,
                title: { display: true, text: 'Cantidad de usuarios' }
            }
        }
    }
});

// -------------------- Gráfico de registros (línea) --------------------
new Chart(document.getElementById('registroChart'), {
    type: 'line',
    data: {
        labels: registroData.labels,
        datasets: [{
            label: 'Usuarios registrados',
            data: registroData.data,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: true,
            tension: 0.4
        }]
    },
    options: { responsive: true }
});

// -------------------- Gráfico por comuna (torta) --------------------
new Chart(document.getElementById('comunaChart'), {
    type: 'pie',
    data: {
        labels: comunaData.labels,
        datasets: [{
            label: 'Usuarios por comuna',
            data: comunaData.data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ]
        }]
    },
    options: { responsive: true }
});
