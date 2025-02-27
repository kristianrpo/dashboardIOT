async function fetchLatestGarbage(totalHeightGarbage) {
    try {
        const response = await fetch('/api/garbage/get/');
        const data = await response.json();
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
                document.getElementById(`fill-${key}`).setAttribute("stroke", "red");
            }
            if (value <= 50 && value > 25) {
                document.getElementById(`fill-${key}`).setAttribute("stroke", "yellow");
            }
            if (value > 50) {
                document.getElementById(`fill-${key}`).setAttribute("stroke", "green");
            }
            document.getElementById(`fill-${key}`).setAttribute("stroke-width", "5");
            document.getElementById(`fill-${key}`).setAttribute("stroke-dashoffset", (251.2 * (1 - (value / 100))).toFixed(2));
            document.getElementById(`occupancy-rate-${key}`).innerHTML = value.toFixed(2) + "%";
        }
        
    } catch (error) {
        console.error("Error al obtener los datos:", error);
    }
}

setInterval(() => fetchLatestGarbage(totalHeightGarbage), 5000);
window.onload = fetchLatestGarbage(totalHeightGarbage);