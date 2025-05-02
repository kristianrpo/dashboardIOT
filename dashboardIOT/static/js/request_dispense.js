document.querySelectorAll('.dispense-form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const endpoint = form.dataset.endpoint;
        const id = form.dataset.id;

        fetch(`${endpoint}?id=${id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error al contactar el dispensador.");
                }
                return response.text();
            })
            .then(data => {
                const response = JSON.parse(data);
                if (response.is_success) {
                    alert("✅"+ response.message);
                } else {
                    alert("❌ Error: " + response.message);
                }
            })
            .catch(error => {
                alert("❌ Error: " + error.message);
            });
    });
});