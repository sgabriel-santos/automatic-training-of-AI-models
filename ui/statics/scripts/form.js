async function submitForm(event) {
    event.preventDefault();
    const form = document.getElementById('form');
    const formData = new FormData(form);

    formData.append('name_model', 'image_classification');
    formData.set('shuffle', formData.get('shuffle') ? 'true' : 'false');

    try {
      const response = await fetch('/fit_model', {
          method: 'POST',
          body: formData
      });

      if (!response.ok) {
          const error = await response.json();
          alert(`Error: ${error.detail}`);
          return;
      }
      
      let btnFitModel = document.querySelector('#btn-fit-model')
      btnFitModel.disabled = true

      let loaderModelTrain = document.querySelector('#loader-model-train')
      loaderModelTrain.style.display = 'block'
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('Error submitting form');
    }
}


document.addEventListener('DOMContentLoaded', async (event) => {
  const response = await fetch('/is_training_model', {
    method: 'GET',
    headers: {'Content-Type': 'application/json'}
  });

  if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
  const data = await response.json();

  let btnFitModel = document.querySelector('#btn-fit-model')
  btnFitModel.disabled = data? true: false

  let loaderModelTrain = document.querySelector('#loader-model-train')
  loaderModelTrain.style.display = data? 'block': 'none'
});