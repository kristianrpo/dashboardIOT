async function fetchLatestGarbage() {
    try {
        const response = await fetch('/api/get-garbage-data/');
        const data = await response.json();
        const totalHeightGarbage = 100;

        occupancyRateRAAE = ((data.raae_distance) * 100)/totalHeightGarbage;
        occupancyRateCaps = ((data.caps_distance) * 100)/totalHeightGarbage;
        occupancyRateLuminaires = ((data.luminaires_distance) * 100)/totalHeightGarbage;
        occupancyRateBatteries = ((data.batteries_distance) * 100)/totalHeightGarbage;
        occupancyRateMedicines = ((data.medicines_distance) * 100)/totalHeightGarbage;
        occupancyRateOil = ((data.oil_distance) * 100)/totalHeightGarbage;
        

        document.getElementById("occupancy-rate-raae").innerHTML = occupancyRateRAAE.toFixed(2) + "%";
        document.getElementById("occupancy-rate-caps").innerHTML = occupancyRateCaps.toFixed(2) + "%";
        document.getElementById("occupancy-rate-luminaires").innerHTML = occupancyRateLuminaires.toFixed(2) + "%";
        document.getElementById("occupancy-rate-batteries").innerHTML = occupancyRateBatteries.toFixed(2) + "%";
        document.getElementById("occupancy-rate-medicines").innerHTML = occupancyRateMedicines.toFixed(2) + "%";
        document.getElementById("occupancy-rate-oils").innerHTML = occupancyRateOil.toFixed(2) + "%";

        if (occupancyRateRAAE <= 25 ) {
            document.getElementById(`fill-raae`).style.backgroundColor = `red`;
        }
        if (occupancyRateRAAE <= 50 && occupancyRateRAAE > 25) {
            document.getElementById(`fill-raae`).style.backgroundColor = `yellow`;
        }
        if (occupancyRateRAAE > 50) {
            document.getElementById(`fill-raae`).style.backgroundColor = `green`;
        }

        if (occupancyRateCaps <= 25 ) {
            document.getElementById(`fill-caps`).style.backgroundColor = `red`;
        }
        if (occupancyRateCaps <= 50 && occupancyRateCaps > 25) {
            document.getElementById(`fill-caps`).style.backgroundColor = `yellow`;
        }
        if (occupancyRateCaps > 50) {
            document.getElementById(`fill-caps`).style.backgroundColor = `green`;
        }

        if (occupancyRateLuminaires <= 25 ) {
            document.getElementById(`fill-luminaires`).style.backgroundColor = `red`;
        }
        if (occupancyRateLuminaires <= 50 && occupancyRateLuminaires > 25) {
            document.getElementById(`fill-luminaires`).style.backgroundColor = `yellow`;
        }
        if (occupancyRateLuminaires > 50) {
            document.getElementById(`fill-luminaires`).style.backgroundColor = `green`;
        }
        
        if (occupancyRateBatteries <= 25 ) {
            document.getElementById(`fill-batteries`).style.backgroundColor = `red`;
        }
        if (occupancyRateBatteries <= 50 && occupancyRateBatteries > 25) {
            document.getElementById(`fill-batteries`).style.backgroundColor = `yellow`;
        }
        if (occupancyRateBatteries > 50) {
            document.getElementById(`fill-batteries`).style.backgroundColor = `green`;
        }

        if (occupancyRateMedicines <= 25 ) {
            document.getElementById(`fill-medicines`).style.backgroundColor = `red`;
        }
        if (occupancyRateMedicines <= 50 && occupancyRateMedicines > 25) {
            document.getElementById(`fill-medicines`).style.backgroundColor = `yellow`;
        }
        if (occupancyRateMedicines > 50) {
            document.getElementById(`fill-medicines`).style.backgroundColor = `green`;
        }

        if (occupancyRateOil <= 25 ) {
            document.getElementById(`fill-oils`).style.backgroundColor = `red`;
        }
        if (occupancyRateOil <= 50 && occupancyRateOil > 25) {
            document.getElementById(`fill-oils`).style.backgroundColor = `yellow`;
        }
        if (occupancyRateOil > 50) {
            document.getElementById(`fill-oils`).style.backgroundColor = `green`;
        }

        document.getElementById(`fill-raae`).style.clipPath = `inset(${occupancyRateRAAE}% 0 0 0)`;
        document.getElementById(`fill-caps`).style.clipPath = `inset(${occupancyRateCaps}% 0 0 0)`;
        document.getElementById(`fill-luminaires`).style.clipPath = `inset(${occupancyRateLuminaires}% 0 0 0)`;
        document.getElementById(`fill-batteries`).style.clipPath = `inset(${occupancyRateBatteries}% 0 0 0)`;
        document.getElementById(`fill-medicines`).style.clipPath = `inset(${occupancyRateMedicines}% 0 0 0)`;
        document.getElementById(`fill-oils`).style.clipPath = `inset(${occupancyRateOil}% 0 0 0)`;
        
    } catch (error) {
        console.error("Error al obtener los datos:", error);
    }
}

setInterval(fetchLatestGarbage, 5000);
window.onload = fetchLatestGarbage;