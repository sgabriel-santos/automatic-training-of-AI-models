async function submitForm(event) {
    event.preventDefault();
    const form = document.getElementById('form');
    const formData = new FormData(form);

    formData.set('shuffle', formData.get('shuffle') ? 'true' : 'false');
    const checkbox = document.getElementById('useAbsolutePathCheckbox');
    const isAbsolutePath = checkbox.checked
    formData.set('is_absolute_path', isAbsolutePath)

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
      window.location.href = "/dataset";
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('Error submitting form');
    }
}

document.addEventListener('DOMContentLoaded', async (event) => {
  // Função para alternar entre input de caminho absoluto e upload de arquivo
  const checkbox = document.getElementById('useAbsolutePathCheckbox');
  const absolutePathSection = document.getElementById('absolutePathSection');
  const fileUploadSection = document.getElementById('fileUploadSection');
  
  const trainDataset = document.getElementById('trainDataset');
  const valDataset = document.getElementById('valDataset');
  const trainDatasetPath = document.getElementById('trainDatasetPath');
  const valDatasetPath = document.getElementById('valDatasetPath');

  checkbox.addEventListener('change', function() {
      if (checkbox.checked) {
        absolutePathSection.style.display = 'block';
        fileUploadSection.style.display = 'none';
        trainDataset.required = false;
        valDataset.required = false;

        trainDatasetPath.required = true;
        valDatasetPath.required = true;

      } else {
        absolutePathSection.style.display = 'none';
        fileUploadSection.style.display = 'block';
        trainDatasetPath.required = false;
        valDatasetPath.required = false;

        trainDataset.required = true;
        valDataset.required = true;
      }
  });



  const response = await fetch('/is_training_model', {
    method: 'GET',
    headers: {'Content-Type': 'application/json'}
  });

  if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
  const data = await response.json();

  toggleFitButton(!data)
  toggleLoaderTraining(data)
});


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