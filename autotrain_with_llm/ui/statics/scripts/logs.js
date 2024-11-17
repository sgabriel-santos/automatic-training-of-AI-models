let interval;
let previous_log  = '#';
// Função para carregar os logs através de uma requisição AJAX
function loadLogs() {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/logs");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let code_block_el = document.getElementById("log-content")
            const current_log = xhr.responseText
            code_block_el.innerText = current_log;
            code_block_el.scrollTop = code_block_el.scrollHeight;

            if(current_log == previous_log) verifyStep()
            previous_log = current_log
        }
    };
    xhr.send();
}

const toggleTestButton = (isToShow) => {
    const btnTestModel = document.getElementById('btn-test-model')
    btnTestModel.disabled = !isToShow
}

const verifyStep = async () => {
    response = await sendRequestToAPI("/step", "GET")
    const step = await response.json()

    if(step == -1){
        alert('O modeo apresentou uma falha durante o treinamento')
        document.querySelector('.go-to-result-model-step').style.display = 'none'
        document.querySelector('.go-to-config-step').style.display = 'block'
    }
    
    if(step == 0){
        // usuário não inciou o treinamento de um modelo
        window.location.href = '/'
    }

    if(step == 2){
        // usuário não inciou o treinamento de um modelo
        window.location.href = '/dataset'
    }

    if(step == 3){
        // Recarregar os logs a cada 2 segundos
        interval = setInterval(() => loadLogs(), 2000);
    }

    if(step == 4){ 
        // Parando fluxo do log
        if(interval) clearInterval(interval)

        // habilitando botão de testar modelo
        toggleTestButton(true)

    }
}

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

// Carregar os logs quando a página é carregada
window.onload = async function () {
    await configParameters()
    await verifyStep()
    loadLogs()
};