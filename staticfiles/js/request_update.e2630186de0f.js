document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("update-form");
    const endpoint = form.dataset.endpoint;
    
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const data = {
            type: document.getElementById("machine-type").value,
            id: parseInt(document.getElementById("machine-id").value),
            portion_size: parseInt(document.getElementById("portion-size").value),
            automatic_start_date: document.getElementById("initial-schedule").value,
            automatic_end_date: document.getElementById("final-schedule").value,
        };

        fetch(endpoint, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) throw new Error("Error al contactar el dispensador.");
            return response.json();
        })
        .then(data => {
            if (data.is_success) {
                alert("✅ " + data.message);
            } else {
                alert("❌ Error: " + data.message);
            }
        })
        .catch(err => {
            alert("❌ Error: " + error.message);
        });
    });
});
