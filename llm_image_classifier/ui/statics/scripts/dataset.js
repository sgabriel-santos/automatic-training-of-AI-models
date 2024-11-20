let imageList;
let url;
let classes = [];
let objCategoryImages;

let trainingDataset;
let validationDataset;

document.addEventListener('DOMContentLoaded', async () => {
    await configParameters()
    await configDataset()
    await fitModel()
    await previousState()
})

const configParameters = async () => {
    let modelConfig = await sendRequestToAPI("/model_config", "GET")
    modelConfig = await modelConfig.json()

    const model_name = document.querySelector(".model_name_value")
    const epoch = document.querySelector(".epoch_value")
    const seed = document.querySelector(".seed_value")
    const batch_size = document.querySelector(".batch_size_value")
    const shuffle = document.querySelector(".shuffle_value")


    model_name.textContent = modelConfig['model_name'] || ''
    epoch.textContent = modelConfig['epochs'] || ''
    seed.textContent = modelConfig['seed'] || ''
    batch_size.textContent = modelConfig['batch_size'] || ''
    shuffle.textContent = modelConfig['shuffle'] || ''
}

const imageCatogoryTemplate = (category, imagePath, amountImages) => {
    return `
        <div class="image-card" onclick="openDialog(this)">
            <div class="image-wrapper">
                <img src="${imagePath}" alt="Imagem de exemplo da categoria ${category}">
                <span class="badge">${amountImages}</span>
            </div>
            <div class="caption">${category}</div>
        </div>
    `
}

const configDataset = async () => {
    let response = await sendRequestToAPI("/images", "GET")
    objCategoryImages = await response.json()

    let urlEndpoint = await sendRequestToAPI("api/image-url", "GET")
    url = await urlEndpoint.json()

    trainingDataset = objCategoryImages['train']
    validationDataset = objCategoryImages['valid']

    Object.keys(trainingDataset).forEach(category => {
        let amountImages = trainingDataset[category].length
        let firstImage = trainingDataset[category][0]
        const newDiv = document.createElement('div')
        newDiv.classList.add('training')
        console.log('Training -> ', `${url.train._url}${firstImage}`)
        console.log(url.train._url)
        console.log(firstImage)
        newDiv.innerHTML = imageCatogoryTemplate(category, `${url.train._url}${firstImage}`, amountImages)
        document.querySelector('.training-dataset').appendChild(newDiv)
    })

    Object.keys(validationDataset).forEach(category => {
        let amountImages = validationDataset[category].length
        let firstImage = validationDataset[category][0]

        const newDiv = document.createElement('div')
        newDiv.classList.add('validation')
        console.log('Valid -> ', `${url.valid._url}${firstImage}`)
        console.log(url.valid._url)
        console.log(firstImage)
        newDiv.innerHTML = imageCatogoryTemplate(category, `${url.valid._url}${firstImage}`, amountImages)
        document.querySelector('.validation-dataset').appendChild(newDiv)
    })
}

const fitModel = async () => {
    const btnFitModel = document.getElementById('btn-fit-model')
    btnFitModel.addEventListener("click", async () => {
        let response = await sendRequestToAPI("/fit_model", "POST")

        if (!response.ok) {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
            return;
        }

        window.location.href = "/logs_screen"
    })
}

const previousState = async () => {
    const previouState = document.getElementById('btn-previous')
    previouState.addEventListener('click', () => window.location.href = '/form')
}

const imageDialogTemplate = (imagePath) => {
    const image = document.createElement('img')
    image.src = imagePath
    image.loading = 'lazy'
    return image
}

function openDialog(cardElement) {
    const parent = cardElement.parentElement
    const datasetMode = parent.classList[0]
    const title = cardElement.querySelector('.caption').textContent; // Obtém o nome da classe do card
    const imageCount = cardElement.querySelector('.badge').textContent; // Obtém a contagem de imagens

    const album = document.querySelector('.image-grid')
    album.innerHTML = ""
    if(datasetMode == 'training'){
        const images = trainingDataset[title]
        images.forEach(imagePath => album.appendChild(imageDialogTemplate(`${url.train._url}${imagePath}`)))
    }else{
        const images = validationDataset[title]
        images.forEach(imagePath => album.appendChild(imageDialogTemplate(`${url.valid._url}${imagePath}`)))
    }

    document.getElementById('dialog-title').textContent = title; // Define o título do diálogo
    document.getElementById('image-count').textContent = `${imageCount} Imagens encontradas`; // Define a contagem de imagens
    document.getElementById('image-dialog').showModal();
}

// Função para fechar o diálogo
const closeDialog = () => document.getElementById('image-dialog').close();