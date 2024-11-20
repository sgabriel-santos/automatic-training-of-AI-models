# Automatic Training of AI Models

**🚀 Sua ferramenta No Code para análise e treinamento de modelos de classificação de imagens com suporte inteligente!**

Esta aplicação foi criada para simplificar o treinamento e análise de modelos de visão computacional. Com uma interface intuitiva e um assistente virtual integrado, ela é ideal para profissionais e entusiastas de machine learning que desejam focar nos resultados sem a complexidade da configuração técnica.

---

## ✨ **Funcionalidades Principais**

- **📂 Upload e configuração de datasets** em diferentes formatos, com suporte para configuração manual ou automática.
- **⚙️ Treinamento automatizado de modelos de classificação de imagens** como InceptionV3, Xception e outros.
- **📊 Relatórios detalhados com métricas e gráficos** que ajudam a visualizar o desempenho do modelo treinado.
- **🤖 Assistente Virtual Inteligente** para responder perguntas relacionadas ao treinamento e desempenho do modelo.
- **📥 Download do modelo treinado** para utilização em outros projetos.

---

## 📋 **Pré-requisitos**

O único pré-requisito para rodar a ferramenta é ter o **Python 3.10 ou superior** instalado na sua máquina.

---

## 🔧 **Instalação**

Você pode instalar a ferramenta de duas formas: através do pacote `llm_image_classifier` ou clonando este repositório.

### 1️⃣ Instalando como um pacote Python:
Use o comando abaixo para instalar o pacote diretamente:
```bash
pip install llm_image_classifier
```

### 2️⃣ Clonando Repositório:
Se preferir, faça o clone do projeto:
```bash
git clone https://github.com/sgabriel-santos/automatic-training-of-AI-models.git
cd automatic-training-of-AI-models
```

### ▶️ Como Executar
Após instalar o pacote ou clonar o repositório, basta executar o seguinte comando para iniciar a aplicação:
```bash
uvicorn llm_image_classifier.main:app
```
Assim que o servidor for iniciado, acesse a aplicação no navegador pelo link: http://localhost:8000/

## 🛠️ Como Utilizar a Ferramenta

### 1. **Configuração do Dataset**
- Faça upload de datasets em formato ZIP ou configure manualmente.
- Adicione classes e organize os dados diretamente na interface.

### 2. **Treinamento do Modelo**
- Selecione o modelo (e.g., InceptionV3).
- Configure hiperparâmetros como número de épocas, batch size e seed.
- Acompanhe o progresso em tempo real.

### 3. **Análise de Resultados**
- Visualize métricas de desempenho, matrizes de confusão e gráficos de acurácia e perda.
- Baixe o modelo treinado para reutilizar em outros projetos.

### 4. **Suporte com o Assistente Virtual**
- Faça perguntas diretamente ao assistente sobre o treinamento e os resultados obtidos.

## 🤝 Contribuições

Contribuições são sempre bem-vindas! Se você encontrou um bug ou gostaria de sugerir melhorias, siga os passos abaixo:

1. Faça um **fork** deste repositório.
2. Crie um **branch** para suas alterações.
3. Envie um **Pull Request**.


## 📄 Licença

Este projeto está sob a licença (MIT) - veja o arquivo [LICENSE.md](https://github.com/sgabriel-santos/automatic-training-of-AI-models/edit/main/LICENSE) para detalhes.