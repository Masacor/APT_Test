// ==========================
// UTILIDADES
// ==========================

// Generar paleta de colores armoniosa
function generarColores(n){
    const baseHue = Math.floor(Math.random()*360);
    const colores = [];
    for(let i=0;i<n;i++){
        colores.push(`hsl(${(baseHue + i*30)%360}, 65%, 55%)`);
    }
    return colores;
}

// Crear o actualizar gráfico
function crearChart(id, tipo, labels, data){
    const ctx = document.getElementById(id);
    if(!ctx) return;

    // Destruir gráfico previo si existe
    if(ctx.chart) ctx.chart.destroy();

    ctx.chart = new Chart(ctx, {
        type: tipo,
        data: {
            labels: labels.length ? labels : ["Sin datos"],
            datasets: [{
                label: "Cantidad",
                data: data.length ? data : [0],
                backgroundColor: generarColores(data.length || 1),
                borderColor: "#333",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true, position: "bottom" },
                tooltip: { enabled: true, mode: 'index', intersect: false }
            },
            scales: tipo.includes("bar") || tipo.includes("line") ? {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            } : tipo === "polarArea" ? {
                r: {               // escala radial para polarArea
                    beginAtZero: true,
                    ticks: { display: false } // oculta los números de la escala
                }
            } : {}
        }
    });
}

// ==========================
// RENDER DE DATOS
// ==========================

const datosDjango = JSON.parse(document.getElementById("datos-django").textContent);

// Tipos de gráficos distintos
const tipos = {
    "chartMarca": "bar",
    "chartLaboratorio": "pie",
    "chartForma": "bar",
    "chartVia": "doughnut",
    "chartPrincipio": "polarArea"
};

// Renderizar gráfico con Top N opcional
function renderChart(id, topN){
    const labels = datosDjango[id].labels;
    const data = datosDjango[id].data;

    if(topN>0){
        crearChart(id, tipos[id], labels.slice(0, topN), data.slice(0, topN));
    } else {
        crearChart(id, tipos[id], labels, data);
    }
}

// Render inicial todos los gráficos
Object.keys(datosDjango).forEach(id => renderChart(id, 0));

// Event listener para Top N
document.querySelectorAll(".top-n").forEach(sel=>{
    sel.addEventListener("change", function(){
        const topN = parseInt(this.value);
        renderChart(this.dataset.chart, topN);
    });
});
