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

    inputFiles.forEach(input => {
        input.addEventListener("change", event => {
            if(input.hasAttribute('addToAlbumWithId')) {
                const files = event.target.files || event.dataTransfer.files;
                const album = document.getElementById(input.getAttribute('addToAlbumWithId'));
                for (const file of files) {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            
                            const albumItem = document.createElement('div');
                            albumItem.className = 'album-item';
    
                            const img = document.createElement('img');
                            img.src = e.target.result;
    
                            const deleteIcon = document.createElement('div');
                            deleteIcon.className = 'delete-icon';
                            deleteIcon.innerHTML = '&times;';
                            deleteIcon.onclick = () => album.removeChild(albumItem);
    
                            albumItem.appendChild(img);
                            albumItem.appendChild(deleteIcon);
                            album.appendChild(albumItem);
                        };
                        reader.readAsDataURL(file);
                    }
                }
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
                    testFunction(img.src)

                    drop.appendChild(img)
                }
            }
        })
    })
})