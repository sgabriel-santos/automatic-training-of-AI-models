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
    const fileInput = document.querySelector('.input-file');
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
            clearInput();
            buildResponse(data)
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


const clearInput = () => {
    const input = document.querySelector('input')
    input.value = ""

    const drop = input.parentElement.querySelector('.drop-zone')
    drop.querySelectorAll('p').forEach(el => drop.removeChild(el))
    let p = document.createElement('p')
    p.innerHTML = "Arraste o arquivo aqui."
    drop.appendChild(p)

    p = document.createElement('p')
    p.innerHTML = "ou"
    drop.appendChild(p)

    p = document.createElement('p')
    p.innerHTML = "Escolher arquivo"
    p.classList.add('choose-file')
    drop.appendChild(p)

    p = document.createElement('p')
    p.innerHTML = 'Formato JPG, PNG'
    p.classList.add('format-available')
    drop.appendChild(p)

    input.parentElement.classList.remove('ready')
    drop.removeChild(drop.querySelector('img.imported-img'))
}

// Função para converter porcentagem para largura
const percentageToWidth = (percentage) => parseFloat(percentage.replace('%', ''));

const buildResponse = (data) => {
    // Elemento onde as barras serão adicionadas
    const barsContainer = document.getElementById('bars');
    barsContainer.innerHTML = ''

    const compatibility = document.createElement('div')
    compatibility.classList.add('title');
    compatibility.textContent = 'Compatibilidade'

    barsContainer.appendChild(compatibility)

    // Montar o layout dinamicamente
    Object.entries(data.class_probabilities).forEach(([className, probability]) => {

        // Criar o contêiner da barra
        const barContainer = document.createElement('div');
        barContainer.classList.add('bar-container');

        // Rótulo da classe
        const label = document.createElement('div');
        label.classList.add('label');
        label.textContent = className;

        // Barra de progresso
        const bar = document.createElement('div');
        bar.classList.add('bar');

        const barFill = document.createElement('div');
        barFill.classList.add('bar-fill');
        barFill.style.width = `${percentageToWidth(probability)}%`;

        // Adicionar preenchimento à barra
        bar.appendChild(barFill);

        // Porcentagem
        const percentage = document.createElement('div');
        percentage.classList.add('percentage');
        percentage.textContent = probability;

        // Montar o layout
        
        barContainer.appendChild(label);
        barContainer.appendChild(bar);
        barContainer.appendChild(percentage);

        // Adicionar ao contêiner principal
        barsContainer.appendChild(barContainer);
    });
}

const verifyStep = async () => {
    response = await sendRequestToAPI("/step", "GET")
    const step = await response.json()

    if(step != 4) window.location.href = '/'
}


document.addEventListener('DOMContentLoaded', async function() {
    await verifyStep()
    const fileInput = document.querySelector('.input-file');
    const testButton = document.getElementById('test-model');
    const downloadModelButton = document.getElementById('download-model')

    downloadModelButton.addEventListener('click', download_model);
    fileInput.addEventListener('change', () => testButton.disabled = !fileInput.files.length);
    testButton.addEventListener('click', teste_model);
  });