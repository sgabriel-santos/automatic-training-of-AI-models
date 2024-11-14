let interval;
let previous_log  = '';
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

    if(step == 0){
        // usuário não inciou o treinamento de um modelo
        window.location.href = '/'
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

// Carregar os logs quando a página é carregada
window.onload = async function () {
    await verifyStep()
    loadLogs()
};