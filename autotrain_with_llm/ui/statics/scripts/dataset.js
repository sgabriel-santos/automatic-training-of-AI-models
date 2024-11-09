let imageList;
let url;
let classes = [];

document.addEventListener('DOMContentLoaded', async () => {
    let response = await sendRequestToAPI("/images", "GET")
    objCategoryImages = await response.json()

    let urlEndpoint = await sendRequestToAPI("api/image-url", "GET")
    url = await urlEndpoint.json()
    let isFirst = true

    Object.keys(objCategoryImages).forEach(category => {
        let imageCategories = objCategoryImages[category]
        let currentClass = category.replace(' ', '_')
        classes.push(currentClass)

        let tabButtons = document.querySelector('.tab-buttons')
        let newButton = document.createElement('button')
        if(isFirst) newButton.classList.add('tab-btn', 'active')
        else newButton.classList.add('tab-btn')
        isFirst = false
        newButton.setAttribute('content-id', currentClass)
        newButton.textContent = category

        tabButtons.appendChild(newButton)

        let tabContents = document.querySelector('.tab-contents')
        let newContent = document.createElement('div')
        newContent.classList.add('content')
        newContent.id = currentClass

        newContent.innerHTML = `
            <span>${imageCategories.length} imagens encontradas</span>
            <div class="gallery-container"></div>     
        `

        tabContents.appendChild(newContent)

        imageCategories.forEach(fileName => {
            let galleryContainer = document.querySelector(`#${currentClass} .gallery-container`)
            let a = document.createElement('a')
            a.href = "#chick-hicks"
            a.classList.add("gallery-items")
            a.innerHTML = `<img src="${url._url}${fileName}" alt="${fileName}"></img>`
        
            galleryContainer.appendChild(a) 
        })
    });

    const currentActiveTab = document.querySelector('.tab-btn.active');
    tabClicked(currentActiveTab); 
    
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(t => t.addEventListener('click', () => tabClicked(t)));
})

const tabClicked = (tab) => {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    const contents = document.querySelectorAll('.content');
    contents.forEach(content => content.classList.remove('show'));

    const contentId = tab.getAttribute('content-id');
    const content = document.getElementById(contentId);

    content.classList.add('show');
}