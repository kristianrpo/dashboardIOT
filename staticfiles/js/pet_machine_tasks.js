document.addEventListener('DOMContentLoaded', () => {
  const $ = id => document.getElementById(id);
  const show = element => element.style.display = 'block';
  const hide = element => element.style.display = 'none';

  const scheduleTypeField = $('id_schedule_type');
  const fields = {
      dayOfWeek: $('div_day_of_week'),
      date: $('div_date'),
      hour: $('div_hour'),
      minute: $('div_minute'),
  };

  const toggleVisibility = () => {
      const type = scheduleTypeField.value;
      Object.values(fields).forEach(hide);
      if (type === 'Diario') {
          show(fields.hour); show(fields.minute);
      } else if (type === 'Semanal') {
          show(fields.dayOfWeek); show(fields.hour); show(fields.minute);
      } else if (type === 'Una vez') {
          show(fields.date); show(fields.hour); show(fields.minute);
      }
  };

  toggleVisibility();
  scheduleTypeField.addEventListener('change', toggleVisibility);

  const addTaskBtn = $("add-task-btn");
  const taskForm = $("task-form");

  const formatNumber = number => number < 10 ? `0${number}` : number;

  addTaskBtn.addEventListener("click", () => {
      const machineId = $("machine-id").value;
      if (!machineId) return alert("Por favor, ingrese el ID de la máquina.");

      const tempForm = new FormData();
      const fields = taskForm.querySelectorAll("input, select, textarea");

      fields.forEach(element => {
        if (element.name) {
          if (element.tagName === 'SELECT') {
            Array.from(element.selectedOptions).forEach(option => {
              tempForm.append(element.name, option.value);
            });
          } else if (element.type === 'checkbox' || element.type === 'radio') {
              if (element.checked) tempForm.append(element.name, element.value);
          } else {
              tempForm.append(element.name, element.value);
          }
        }
      });

      tempForm.append("machine_id", machineId);
      const get = name => tempForm.get(name);

      const scheduleType = get("schedule_type");
      const validations = {
        'Una vez': ['date', 'hour', 'minute'],
        'Semanal': ['day_of_week', 'hour', 'minute'],
        'Diario': ['hour', 'minute'],
      };

      for (let field of (validations[scheduleType] || [])) {
        if (!get(field)) return alert(`Debe completar el campo: ${field}`);
      }

      const endpointAdd = taskForm.dataset.addScheduleEndpoint;
      const endpointGet = `${taskForm.dataset.getTasksEndpoint}?machine_id=${machineId}`;
      const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch(endpointAdd, {
        method: "POST",
        headers: { "X-CSRFToken": csrf },
        body: tempForm
      })
      .then(res => res.ok ? res.json() : Promise.reject("Error al agregar tarea"))
      .then(() => fetch(endpointGet, { headers: { "X-CSRFToken": csrf } }))
      .then(res => res.ok ? res.json() : Promise.reject("Error al obtener tareas"))
      .then(data => {
        const container = $("tasks-list");
        container.innerHTML = "";
        data.forEach(task => {
          const type = task.schedule_type;
          const time = `${formatNumber(task.hour)}:${formatNumber(task.minute)}`;
          let label = "", text = "";

          if (type === "Una vez") {
            label = "info"; text = `Ejecución: ${task.date} - ${time}`;
          } else if (type === "Semanal") {
            label = "warning"; text = `Ejecución: Todos los ${task.day_of_week} - ${time}`;
          } else if (type === "Diario") {
            label = "success"; text = `Ejecución: Todos los Días - ${time}`;
          }
          container.innerHTML += `
            <div class="alert alert-secondary d-flex justify-content-between align-items-center mb-2 flex-wrap mt-2">
                <span class="badge bg-${label}">${type}</span>
                <span class="badge bg-danger mt-2">${text}</span>
            </div>`;
        });
        alert("Tarea programada agregada correctamente.");
      })
      .catch(err => {
        console.error("❌", err);
        alert("Hubo un error al procesar la solicitud.");
      });
  });
});