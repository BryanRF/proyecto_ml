// classify_image.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('classifyForm');
    const datasetSelect = document.getElementById('datasetSelect');
    const imageFile = document.getElementById('imageFile');
    const resultContainer = document.getElementById('resultContainer');
    const predictedClass = document.getElementById('predictedClass');
    const confidence = document.getElementById('confidence');
    const previewImage = document.getElementById('previewImage');

    // Cargar los datasets disponibles
    fetch('/api/datasets/')
        .then(response => response.json())
        .then(data => {
            datasetSelect.innerHTML = '<option value="">Seleccione un dataset</option>';
            data.results.forEach(dataset => {
                const option = document.createElement('option');
                option.value = dataset.id;
                option.textContent = dataset.name;
                datasetSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error al cargar datasets:', error));

    // Mostrar vista previa de la imagen
    imageFile.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
            }
            reader.readAsDataURL(file);
        }
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData();
        formData.append('dataset_id', datasetSelect.value);
        formData.append('image', imageFile.files[0]);

        fetch('/api/classify_image/', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la clasificación de la imagen');
            }
            return response.json();
        })
        .then(data => {
            resultContainer.style.display = 'block';
            predictedClass.textContent = data.predicted_class;
            confidence.textContent = (data.confidence * 100).toFixed(2) + '%';
        })
        .catch(error => {
            resultContainer.style.display = 'block';
            predictedClass.textContent = 'Error';
            confidence.textContent = error.message;
        });
    });
});