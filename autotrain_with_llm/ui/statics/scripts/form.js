async function submitForm(event) {
    event.preventDefault();
    const form = document.getElementById('form');
    const formData = new FormData(form);

    formData.set('shuffle', formData.get('shuffle') ? 'true' : 'false');
    const selectMode = document.getElementById('select-dataset-configuration');
    const isAbsolutePath = selectMode.value == 'absolute-path-section'? true: false;
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

const changeDatasetConfigMode = () => {
  const selectedConfigurationModel = document.getElementById('select-dataset-configuration');
  selectedConfigurationModel.addEventListener('change', function() {
      document.querySelectorAll('.section-config-mode').forEach(el => el.style.display = 'none')
      document.querySelectorAll('.set-to-not-required').forEach(el => el.required = false)

      
      const currentSection = document.getElementById(selectedConfigurationModel.value)
      currentSection.style.display = 'block'
      
      const currentTrainMode = document.getElementById(`train-${selectedConfigurationModel.value}`)
      const currentvalidMode = document.getElementById(`valid-${selectedConfigurationModel.value}`)
      currentTrainMode.required = true
      currentvalidMode.required = true
  });
}

const configSourceCodeDialog = () => {
  const sourceCodeIcon = document.querySelector('.source-code-icon')
  const sourceCodeDialog = document.querySelector('.source-code-dialog')

  sourceCodeIcon.addEventListener('click', async () => {
    sourceCodeDialog.showModal()
    const select = document.querySelector('select')
    const response = await sendRequestToAPI(`source_code_by_model_name?model_name=${select.value}`, 'GET')
    const sourceCode = await response.json()

    const panelCode = document.getElementById('python-code')
    panelCode.innerHTML = sourceCode

    hljs.highlightBlock(panelCode);
    hljs.highlightAll();

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