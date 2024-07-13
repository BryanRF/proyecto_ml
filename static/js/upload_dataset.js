document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("uploadForm");
  const uploadStatus = document.getElementById("uploadStatus");
  const uploadButton = document.getElementById("uploadButton");
  const spinner = uploadButton.querySelector(".spinner-border");
  const timeCounter = document.getElementById("timeCounter");
  const timer = document.getElementById("timer");

  let startTime = 0;
  let endTime = 0;
  let timerInterval;

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append("name", document.getElementById("datasetName").value);
    formData.append("file", document.getElementById("datasetFile").files[0]);
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    uploadStatus.innerHTML = "";
    uploadButton.disabled = true; // Disable the button during upload
    spinner.classList.remove("d-none"); // Show spinner

    startTime = new Date().getTime();
    timerInterval = setInterval(updateTimer, 1000);

    fetch("/api/train_dataset/", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": csrfToken // Añadir el token CSRF al encabezado
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Error en la subida del dataset");
        }
        return response.json();
      })
      .then((data) => {
        clearInterval(timerInterval);
        endTime = new Date().getTime();
        updateTimer(); // Final update

        uploadStatus.innerHTML +=
          '<div class="alert alert-success">Dataset subido y entrenado con éxito</div>';

        Swal.fire({
          icon: 'success',
          title: 'Éxito',
          text: 'Dataset subido y entrenado correctamente.'
        });
        fetch(`/api/generate_report/?dataset_id=${data.creacion}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Error al descargar el reporte");
          }
          return response.blob();
        })
        .then((blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = `report_${data.creacion}.pdf`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
        })
        .catch((error) => {
          console.error('Error al descargar el reporte:', error);
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Hubo un problema al descargar el reporte.'
          });
        });
      })
      .catch((error) => {
        clearInterval(timerInterval);
        updateTimer(); // Final update

        uploadStatus.innerHTML += `<div class="alert alert-danger">Error: ${error.message}</div>`;

        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Hubo un problema al subir el dataset.'
        });
      })
      .finally(() => {
        uploadButton.disabled = false; // Re-enable the button after upload
        spinner.classList.add("d-none"); // Hide spinner
      });
  });

  function updateTimer() {
    const currentTime = new Date().getTime();
    const elapsedTime = currentTime - startTime;
    const minutes = Math.floor(elapsedTime / (1000 * 60));
    const seconds = Math.floor((elapsedTime % (1000 * 60)) / 1000);
    timer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    timeCounter.style.display = "block";
  }
});