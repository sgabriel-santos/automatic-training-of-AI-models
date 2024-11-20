async function submitForm(event) {
    event.preventDefault();
    const form = document.getElementById('form');
    const formData = new FormData(form);

    formData.set('shuffle', formData.get('shuffle') ? 'true' : 'false');
    const selectMode = document.getElementById('select-dataset-configuration');
    formData.set('dataset_config_mode', selectMode.value)

    if(selectMode.value == 'manual-config'){
      // Criar um único array com todas as referências (File)
      const allReferences = Object.values(imagesPerClass)
      .flatMap(images => images.map(image => image.reference));

      // Adicionar todos os arquivos ao parâmetro "file_training_images"
      allReferences.forEach((file, index) => {
        formData.append("file_training_images", file); // Todos vão para o mesmo campo
      });
    }

    try {
      toggleFitButton(false)
      toggleLoaderConfigParameter(true)

      const response = await fetch('/configure_model', {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        toggleFitButton(true)
        toggleLoaderConfigParameter(false)
        return;
      }

      toggleLoaderConfigParameter(false)
      toggleFitButton(true)
      window.location.href = "/dataset";
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('Error submitting form');
    }
}

const changeDatasetConfigMode = () => {
  const selectedConfigurationModel = document.getElementById('select-dataset-configuration');
  selectedConfigurationModel.addEventListener('change', function() {
      document.querySelectorAll('.section-config-mode').forEach(el => el.style.display = 'none')
      document.querySelectorAll('.set-to-not-required').forEach(el => el.required = false)

      
      const currentSection = document.getElementById(selectedConfigurationModel.value)
      currentSection.style.display = selectedConfigurationModel.value == 'upload-dataset' ? 'flex' : 'block'
      
      const currentTrainMode = document.getElementById(`train-${selectedConfigurationModel.value}`)
      const currentvalidMode = document.getElementById(`valid-${selectedConfigurationModel.value}`)
      if(selectedConfigurationModel.value == 'manual-config'){
        document.getElementById('btn-create-new-class').style.display = 'inline-block'
      }else{
        currentTrainMode.required = true
        currentvalidMode.required = true
      }
  });
}

const configSourceCodeDialog = () => {
  const sourceCodeIcon = document.querySelector('.source-code-icon')
  const sourceCodeDialog = document.getElementById('codeDialog')

  sourceCodeIcon.addEventListener('click', async () => {
    sourceCodeDialog.showModal()
    // sourceCodeDialog.focus()
    const select = document.querySelector('select')
    const response = await sendRequestToAPI(`source_code_by_model_name?model_name=${select.value}`, 'GET')
    const sourceCode = await response.json()

    const panelCode = document.getElementById('python-code')
    panelCode.innerHTML = sourceCode

    const modelName = document.querySelector('.model-name') 
    modelName.innerHTML = select.options[select.selectedIndex].text
  })
}

const verifyTrainingModel = async () => {
  const response = await fetch('/is_training_model', {
    method: 'GET',
    headers: {'Content-Type': 'application/json'}
  });

  if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
  const data = await response.json();

  toggleFitButton(!data)
  toggleLoaderTraining(data)
}

document.addEventListener('DOMContentLoaded', async (event) => {
  changeDatasetConfigMode()
  configSourceCodeDialog()
  await verifyTrainingModel()


  const labels = document.querySelectorAll(".file-input")

    function onEnter(label){
        label.classList.add('active')
    }

    function onLeave(label){
        label.classList.remove('active')
    }

    labels.forEach(label => {
        label.addEventListener("dragenter", () => onEnter(label))
        label.addEventListener("drop", () => onLeave(label))
        label.addEventListener("dragend", () => onLeave(label))
        label.addEventListener("dragleave", () => onLeave(label))
    })

    const inputFiles = document.querySelectorAll('.input-file')
    const dropzone = document.querySelector('.drop-zone')

    inputFiles.forEach(input => {
        input.addEventListener("change", event => {
            if(input.hasAttribute('addToAlbumWithId')) {
                const files = event.target.files || event.dataTransfer.files;
                for (const file of files) {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                          console.log('Adicionando imagem no algum')
                          addImageInAlbum(e.target.result)
                          console.log('-> ', file)
                          auxImages.push({'base64': e.target.result, 'reference': file})
                          updateAlbumCounter()
                          input
                        };
                        reader.readAsDataURL(file);
                    }
                }
                clearInputImages()
            }
            else {
                const type = input.files[0].type
                const fileName = input.files[0].name
                const formats = input.getAttribute('accept')
                
                if(!formats.includes(type)) {
                  alert(`Formato ${type} não permitido. Necessário realizar a importação de um arquivo válido. Os formatos permitidos são: ${formats}`);
                    return;
                }

                const drop = input.parentElement.querySelector('.drop-zone')
                drop.querySelectorAll('p').forEach(el => drop.removeChild(el))
                const p = document.createElement('p')
                p.innerHTML = "Arquivo adicionado"
                drop.appendChild(p)

                const pName = document.createElement('p')
                pName.id = 'file-name'
                pName.innerHTML = fileName

                drop.appendChild(pName)
                input.parentElement.classList.add('ready')

                if(input.hasAttribute('showImage')){
                    const currentImg = document.querySelector("#cover")
                    if(currentImg) drop.removeChild(currentImg)

                    const img = document.createElement('img')
                    img.classList.add('imported-img')
                    img.id = "cover"
                    img.src = URL.createObjectURL(input.files[0])

                    drop.appendChild(img)
                }
            }
        })
    })
});

const addImageInAlbum = (imageBase64) => {
  const album = document.getElementById('image-grid');
  const albumItem = document.createElement('div');
  albumItem.className = 'album-item';

  const img = document.createElement('img');
  img.src = imageBase64;

  const deleteIcon = document.createElement('div');
  deleteIcon.className = 'delete-icon';
  deleteIcon.innerHTML = '&times;';
  deleteIcon.onclick = removeImageFromAlbum

  albumItem.appendChild(img);
  albumItem.appendChild(deleteIcon);
  album.appendChild(albumItem);
}

const removeImageFromAlbum = (event) => {
  const albumItem = event.target.parentElement; // Obter o elemento pai (album-item)
  const children = Array.from(albumItem.parentElement.children); // Converter os filhos para um array
  const indexToRemove = children.indexOf(albumItem); 

  if (indexToRemove >= 0 && indexToRemove < auxImages.length) {
    auxImages.splice(indexToRemove, 1);
    updateAlbumCounter()
  }

  const album = document.getElementById('image-grid');
  album.removeChild(albumItem)
}

const updateAlbumCounter = () => {
  let textCounter = 'Nenhuma imagem adicionada'
  if(auxImages.length) textCounter = `${auxImages.length} Imagens adicionadas`
  document.getElementById('image-count').innerHTML = textCounter
}


const saveClass = () => {
  console.log('Salvando classe')
  console.log('Nome anterior da classe: ', previousClassName)
  console.log('Novo nome: ', document.querySelector('.inp-class-name').value)
}

const imageCatogoryTemplate = (category, imagePath, amountImages) => {
  return `
      <div class="image-card" onclick="openDialog('${category}')">
          <div class="image-wrapper">
              <img src="${imagePath}" alt="Imagem de exemplo da categoria ${category}">
              <span class="badge">${amountImages}</span>
          </div>
          <div class="caption">${category}</div>
      </div>
  `
}

const imageDialogTemplate = (imagePath) => {
  const image = document.createElement('img')
  image.src = imagePath
  image.loading = 'lazy'
  return image
}

let imagesPerClass = {
}

let previousClassName;
let auxImages;

function handleFormSubmit(event) {
  event.preventDefault(); // Evita o envio padrão do formulário
  closeDialog(true); // Chama a função para fechar o diálogo
}

function openDialog(className='') {
  document.querySelector('.invalid-feedback').style.display = 'none'
  document.querySelector('.inp-class-name').value = className
  document.getElementById('btn-delete-class').style.display = className? 'inline': 'none'

  auxImages = []
  if(className in imagesPerClass) auxImages = [...imagesPerClass[className]]
  previousClassName = className

  const album = document.querySelector('.image-grid')
  album.innerHTML = ""

  auxImages.forEach(image => addImageInAlbum(image.base64))
  document.getElementById('image-count').textContent = `${auxImages.length} Imagens adicionadas`; // Define a contagem de imagens
  document.getElementById('image-dialog').showModal();
}

// Função para fechar o diálogo
const closeDialog = (isToSave = false) => {
  document.querySelector('.training-dataset').innerHTML = ""
  
  if(isToSave && auxImages.length < 2){
    document.querySelector('.invalid-feedback').style.display = 'block'
    return
  }
  
  if(isToSave) {
    let currentClassName = document.querySelector('.inp-class-name').value
    delete imagesPerClass[previousClassName]

    auxImages.forEach(async (image, index) => {
      const fileName = image['reference'].name.split('/').at(-1);
      const fileType = image['reference'].type;
    
      // Carregar o conteúdo binário do arquivo original
      const fileContent = await image['reference'].arrayBuffer();
    
      // Criar um novo arquivo com o nome alterado
      const fileWithNewName = new File([fileContent], `${currentClassName}/${fileName}`, { type: fileType });
    
      // Substituir o arquivo na lista
      auxImages[index].reference = fileWithNewName;
    });

    imagesPerClass[currentClassName] = [...auxImages]

    console.log(imagesPerClass)

  }
  
  Object.keys(imagesPerClass).forEach(category => {
    let amountImages = imagesPerClass[category].length
    let firstImage = imagesPerClass[category][0]['base64']
    const newDiv = document.createElement('div')
    newDiv.classList.add('training')
    newDiv.innerHTML = imageCatogoryTemplate(category, `${firstImage}`, amountImages)
    document.querySelector('.training-dataset').appendChild(newDiv)
  })
  document.getElementById('image-dialog').close();
}

const clearInputImages = () => {
  document.getElementById('upload-images').value = ""
}

const deleteClass = () => {
  delete imagesPerClass[previousClassName]
  closeDialog(false)
}

function toggleFitButton(isEnable){
  const btnTrain= document.getElementById('btn-config-model');
  btnTrain.disabled = !isEnable
}

function toggleLoaderConfigParameter(isToShow){
  let loaderConfigParameters = document.querySelector('#loader-config-parameters')
  loaderConfigParameters.style.display = isToShow? 'block': 'none'
}

function toggleLoaderTraining(isToShow){
  let loaderModelTrain = document.querySelector('#loader-model-train')
  loaderModelTrain.style.display = isToShow? 'block': 'none'
}