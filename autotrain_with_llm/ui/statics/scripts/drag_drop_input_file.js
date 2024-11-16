document.addEventListener('DOMContentLoaded', () => {
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

    console.log('Inputs -> ', inputFiles)
    inputFiles.forEach(input => {
        input.addEventListener("change", event => {
            const type = input.files[0].type
            const fileName = input.files[0].name
            const formats = input.getAttribute('accept').split(',')
            
            if(!formats.includes(type)) {
                alert("Formato não permitido. Necessário realizar a importação de um arquivo válido");
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

            if(type.includes('image')){
                const currentImg = document.querySelector("#cover")
                if(currentImg) dropzone.removeChild(currentImg)

                const img = document.createElement('img')
                img.classList.add('imported-img')
                img.id = "cover"
                img.src = URL.createObjectURL(input.files[0])

                dropzone.appendChild(img)
            }
        })
    })
})