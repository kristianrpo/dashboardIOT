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
      .then(() => {
        refreshTasks(machineId, taskForm.dataset.getTasksEndpoint, csrf);
        alert("Tarea programada agregada correctamente.");
      })
      .catch(err => {
        console.error("❌", err);
        alert("Hubo un error al procesar la solicitud.");
      });
  });
});


function refreshTasks(machineId, endpointGet, csrfToken) {
  const $ = id => document.getElementById(id);
  const formatNumber = number => number < 10 ? `0${number}` : number;

  fetch(`${endpointGet}?machine_id=${machineId}`, {
    headers: { "X-CSRFToken": csrfToken }
  })
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
          <span class="badge bg-dark mt-2 w-50 text-wrap">${text}</span>
          <button class="btn btn-danger mt-2" onclick="deleteTask(${task.id})">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
              <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
              <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
            </svg>
          </button>
        </div>`;
    });
  })
  .catch(err => {
    console.error("❌", err);
    alert("Error al actualizar la lista de tareas.");
  });
}

function deleteTask(taskId) {
  const machineId = document.getElementById("machine-id").value;
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
  const endpointDelete = `/api/pets/${taskId}/delete_task/`;
  const endpointGet = document.getElementById("task-form").dataset.getTasksEndpoint;

  if (!confirm("¿Estás seguro de que deseas eliminar esta tarea?")) return;

  fetch(endpointDelete, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": csrf
    }
  })
  .then(res => res.ok ? res.json() : Promise.reject("Error al eliminar tarea"))
  .then(data => {
    if (data.is_success) {
      refreshTasks(machineId, endpointGet, csrf);
      alert(data.message);
    } else {
      alert("Error: " + data.message);
    }
  })
  .catch(err => {
    console.error("❌", err);
    alert("Error en la petición: " + err);
  });
}