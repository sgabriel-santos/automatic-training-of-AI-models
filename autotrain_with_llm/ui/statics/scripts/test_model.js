function download_model(){
    toggleTestModelButton(false)
    toggleDownloadButton(false)

    toggleLoaderDownloadModel(true)
    fetch('/download_model', {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob(); // Converter a resposta para um blob
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'model.keras'; // Nome do arquivo para download
        document.body.appendChild(a); // Link adicionado ao corpo do documento
        a.click(); // Simular o clique no link
        a.remove(); // Remover o link após o clique
        toggleLoaderDownloadModel(false)
        toggleTestModelButton(true)
        toggleDownloadButton(true)
        setTimeout(() => alert(`Download do modelo inciado com sucesso!!`), 10)
    })
    .catch(error => {
        toggleLoaderDownloadModel(false)
        toggleTestModelButton(true)
        toggleDownloadButton(true)
        setTimeout(() => alert(`Houve um erro no download do arquivo!!`), 10)
        console.error('Houve um erro no download do arquivo:', error);
    });
}

function toggleLoaderTestModel(isToShow){
    const loaderTestModel = document.getElementById('loader-test-model');
    loaderTestModel.style.display = isToShow? 'block': 'none'
}

function toggleLoaderDownloadModel(isToShow){
    const loaderDownloadModel = document.getElementById('loader-download-model');
    loaderDownloadModel.style.display = isToShow? 'block': 'none'
}

function toggleTestModelButton(isEnable){
    const loaderTestModel = document.getElementById('test-model');
    loaderTestModel.disabled = !isEnable
}

function toggleDownloadButton(isEnable){
    const downloadButton = document.getElementById('download-model');
    downloadButton.disabled = !isEnable
}

function teste_model(){
    toggleTestModelButton(false)
    toggleDownloadButton(false)
    const fileInput = document.getElementById('formFile');
    const file = fileInput.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('image', file);

        toggleLoaderTestModel(true)
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            toggleLoaderTestModel(false)
            toggleTestModelButton(true)
            toggleDownloadButton(true)
            setTimeout(() => alert(`Prediction: ${data.predicted_class}`), 10)
        })
        .catch((error) => {
            toggleLoaderTestModel(false)
            toggleTestModelButton(true)
            toggleDownloadButton(true)
            setTimeout(() => alert('Um erro ocorreu ao buscar informações de predição do modelo'), 10)
            console.error('Error:', error);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('formFile');
    const testButton = document.getElementById('test-model');
    const downloadModelButton = document.getElementById('download-model')

    downloadModelButton.addEventListener('click', download_model);
    fileInput.addEventListener('change', () => testButton.disabled = !fileInput.files.length);
    testButton.addEventListener('click', teste_model);
  });