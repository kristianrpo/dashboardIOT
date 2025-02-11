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
        occupancyRateOils = ((data.oils_distance) * 100)/totalHeightGarbage;
        
        ocuppancyRatesGarbage = {
            "raae": occupancyRateRAAE,
            "caps": occupancyRateCaps,
            "luminaires": occupancyRateLuminaires,
            "batteries": occupancyRateBatteries,
            "medicines": occupancyRateMedicines,
            "oils": occupancyRateOils
        }

        for (const [key, value] of Object.entries(ocuppancyRatesGarbage)) {
            if (value <= 25 ) {
                document.getElementById(`fill-${key}`).style.backgroundColor = `red`;
            }
            if (value <= 50 && value > 25) {
                document.getElementById(`fill-${key}`).style.backgroundColor = `yellow`;
            }
            if (value > 50) {
                document.getElementById(`fill-${key}`).style.backgroundColor = `green`;
            }
            document.getElementById(`occupancy-rate-${key}`).innerHTML = value.toFixed(2) + "%";
            document.getElementById(`fill-${key}`).style.clipPath = `inset(${value}% 0 0 0)`;
        }
        
    } catch (error) {
        console.error("Error al obtener los datos:", error);
    }
}

setInterval(fetchLatestGarbage, 5000);
window.onload = fetchLatestGarbage;