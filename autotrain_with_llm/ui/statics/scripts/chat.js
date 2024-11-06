const chatBody = document.querySelector(".chat-body")
const messageInput = document.querySelector(".message-input")
const sendMessageButton = document.querySelector("#send-message")
const chatbotToggler = document.querySelector("#chatbot-toggler")
const closeChatbot = document.querySelector("#close-chatbot")

const initialInputHeight = messageInput.scrollHeight;
let messageHistory = []

const userData = {
    message: null
}

let state_machine = 0 // Usuário ainda não iniciou conversa com o chat
// 1 -> Usuário iniciou conversa. Porém, ainda não configurou sua chave
// 2 -> Usuário iniciou conversa e sua chave foi configurada com sucesso

const sendRequestToAPI = async (endpoint, method) => {
    const requestOptions = {
        method: method,
        headers: { "Content-Type": "application/json" },
    }

    const response = await fetch(endpoint, requestOptions)
    return response
}

const createMessageElement = (content, ...classes) => {
    const div = document.createElement("div")
    div.classList.add("message", ...classes)
    div.innerHTML = content;
    return div
}

const generateBotResponse = async (incomingMessageDiv) => {
    let responseText;
    try {
        if(state_machine != 1){
            const response = await sendRequestToAPI(`/send_message?text=${JSON.stringify(userData.message)}`, "GET")
            if (!response.ok) responseText = await generateBotResponseByErrorAndUpdateStateMachine(response)
            else responseText = await response.json()

        }else {
            const response = await sendRequestToAPI(`/register_groq_api_key?api_key=${JSON.stringify(userData.message)}`, "POST")
            if (!response.ok) {
                const error = await response.json();
                console.log(error.detail)
                console.log(response.status)
                responseText = `
                    ⚠️ Enfrentamos um problema ao atualizar o seu Token de acesso.

                    Por favor, tente novamente mais tarde.
                `
            }else {
                responseText = `
                    Seu Token foi salvo com sucesso 🙌. 
                    Podemos dar continuidade a nossa conversa... Qual sua dúvida?
                `
                state_machine = 2
            }
        }
    }
    catch {
        console.log('Excessão gerada!!')
        responseText = `
            ⚠️ Problema de Conexão com o Serviço do LLM
            
            No momento, estamos enfrentando dificuldades para conectar ao serviço do LLM. Por favor, tente novamente mais tarde.
        `
    }
    
    const messageElement = incomingMessageDiv.querySelector(".message-text")
    addMessageInLocalStorage('bot-message', responseText)
    messageElement.innerText = responseText
    incomingMessageDiv.classList.remove("thinking")
    chatBody.scrollTo({top: chatBody.scrollHeight, behavior: "smooth"})
}

const handleHistoryMessage = () => {
    let history = localStorage.getItem('messageHistory')
    if(history != undefined) messageHistory = JSON.parse(history)

    messageHistory.forEach(element => {
        const messageContent = `<div class="message-text"></div>`
        const outgoingMessageDiv = createMessageElement(messageContent, element.type)
        outgoingMessageDiv.querySelector(".message-text").innerText = element.message;
        chatBody.appendChild(outgoingMessageDiv);
        chatBody.scrollTo({top: chatBody.scrollHeight, behavior: "smooth"})
    });
}

// Handle outgoing user messages
const handleOutgoingMessage = (e, message) => {
    e.preventDefault()
    userData.message = messageInput.value.trim()
    addMessageInLocalStorage('user-message', userData.message)
    messageInput.value = "";
    messageInput.dispatchEvent(new Event("input"));

    // Create and display user message
    let messageContent = `<div class="message-text"></div>`
    const outgoingMessageDiv = createMessageElement(messageContent, "user-message")
    outgoingMessageDiv.querySelector(".message-text").innerText = userData.message;
    chatBody.appendChild(outgoingMessageDiv);
    chatBody.scrollTo({top: chatBody.scrollHeight, behavior: "smooth"})

    messageContent = `<svg class="bot-avatar" xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 1024 1024">
        <path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9zM351.7 448.2c0-29.5 23.9-53.5 53.5-53.5s53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5-53.5-23.9-53.5-53.5zm157.9 267.1c-67.8 0-123.8-47.5-132.3-109h264.6c-8.6 61.5-64.5 109-132.3 109zm110-213.7c-29.5 0-53.5-23.9-53.5-53.5s23.9-53.5 53.5-53.5 53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5zM867.2 644.5V453.1h26.5c19.4 0 35.1 15.7 35.1 35.1v121.1c0 19.4-15.7 35.1-35.1 35.1h-26.5zM95.2 609.4V488.2c0-19.4 15.7-35.1 35.1-35.1h26.5v191.3h-26.5c-19.4 0-35.1-15.7-35.1-35.1zM561.5 149.6c0 23.4-15.6 43.3-36.9 49.7v44.9h-30v-44.9c-21.4-6.5-36.9-26.3-36.9-49.7 0-28.6 23.3-51.9 51.9-51.9s51.9 23.3 51.9 51.9z"></path>
    </svg>
    <div class="message-text">
        <div class="thinking-indicator">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        </div>
    </div>`
    const incomingMessageDiv = createMessageElement(messageContent, "bot-message", "thinking")
    chatBody.appendChild(incomingMessageDiv);
    chatBody.scrollTo({top: chatBody.scrollHeight, behavior: "smooth"})
    generateBotResponse(incomingMessageDiv)
}

document.addEventListener("DOMContentLoaded", handleHistoryMessage)

// Handle Enter key press for sending messages
messageInput.addEventListener("keydown", (e) => {
    const userMessage = e.target.value.trim();
    if(e.key === "Enter" && userMessage && !e.shiftKey && window.innerWidth > 768) {
        handleOutgoingMessage(e)
    }
})

const addMessageInLocalStorage = (type, message) => {
    messageHistory.push({'type': type, 'message': message})
    localStorage.setItem('messageHistory', JSON.stringify(messageHistory))
}

// Adjust input field height dynimaclly
messageInput.addEventListener("input", () => {
    messageInput.style.height = `${initialInputHeight}px`;
    messageInput.style.height = `${messageInput.scrollHeight}px`;
    document.querySelector(".chat-form").style.borderRadius = messageInput.scrollHeight > initialInputHeight ? "15px": "32px";
})

sendMessageButton.addEventListener("click", (e) => handleOutgoingMessage(e))
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
closeChatbot.addEventListener("click", () => document.body.classList.remove("show-chatbot"));

// Utils Messages
const generateBotResponseByErrorAndUpdateStateMachine = async (response) => {
    if(response.status == 424){
        responseText = `
            ⚠️ Atenção: Chave Groq Necessária!

            Para utilizar o assistente, você precisa configurar uma chave de acesso.

            1. Acesse o link para gerar sua chave: https://console.groq.com/keys
            
            Nota: A chave deve começar com "gsk_".
            
            2. Copie e cole a chave como resposta nesta conversa.
            
            Este processo é rápido e gratuito 😁.
        `;
        state_machine = 1;
    }
    else if(response.status == 401){
        responseText = `
            ⚠️ Token de Acesso Inválido

            Parece que a chave Groq configurada não é válida. Para corrigir isso, siga os passos abaixo para configurar um token válido e continuar a conversa:

            1. Acesse o link para gerar uma nova chave: https://console.groq.com/keys

            Nota: A chave gerada deve começar com o prefixo "gsk_".
            
            2. Copie e cole a nova chave como resposta nesta conversa.

            Este processo é simples e gratuito 😁.
        `
        state_machine = 1;
    }
    else if(response.status == 503){
        responseText = `
            ⚠️ Problema de Conexão com o Serviço do LLM
            
            No momento, estamos enfrentando dificuldades para conectar ao serviço do LLM. Por favor, tente novamente mais tarde.
        `
        state_machine = 0;
    }
    else{
        const error = await response.json();
        console.log(error.detail)
        console.log(response.status)
        responseText = `
            ⚠️ Problema de Conexão com o Serviço do LLM
            
            No momento, estamos enfrentando dificuldades para conectar ao serviço do LLM. Por favor, tente novamente mais tarde.
        `
        state_machine = 0;
    }
    return responseText
}