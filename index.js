const apikey = "42528730-1981fbc0fa54794e310cd6219"; 
const formel = document.querySelector("form");
const searchInputel = document.getElementById("search-input");
const searchResultel = document.querySelector(".search-results");
const showMoreButton = document.getElementById("show-more-button");

let inputdata = "";
let page = 1; 
let randomPage = 1; 

async function fetchRandomImages() {
    const url = `https://pixabay.com/api/?key=${apikey}&image_type=photo&pretty=true&per_page=10&page=${randomPage}`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        const results = data.hits; 

        if (results && results.length > 0) {
            searchResultel.innerHTML = "";
            displayImages(results);
            showMoreButton.style.display = "block"; 
        } else {
            console.log('No results found.');
            showMoreButton.style.display = "none"; 
        }
    } catch (error) {
        console.error('Error fetching random images:', error);
    }
}

async function fetchImages() {
    if (!inputdata.trim()) {
        fetchRandomImages(); 
        return; 
    }

    const url = `https://pixabay.com/api/?key=${apikey}&q=${encodeURIComponent(inputdata)}&image_type=photo&pretty=true&page=${page}`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        
        const data = await response.json();
        const results = data.hits; 

        if (results && results.length > 0) {
            if (page === 1) {
                searchResultel.innerHTML = ""; 
            }
            displayImages(results);
            showMoreButton.style.display = "block"; 
        } else {
            console.log('No results found.');
            showMoreButton.style.display = "none"; 
        }
    } catch (error) {
        console.error('Error fetching images:', error);
    }
}

function displayImages(results) {
    results.forEach((result) => {
        const imagewrap = document.createElement("div");
        imagewrap.classList.add("search-result");

        const image = document.createElement("img");
        image.src = result.webformatURL;
        image.alt = result.tags;

        const imagelink = document.createElement("a");
        imagelink.href = result.pageURL;
        imagelink.target = "_blank";
        imagelink.textContent = "View on Pixabay";

        const infoContainer = document.createElement("div");
        infoContainer.classList.add("image-info");
        
        const authorName = document.createElement("p");
        authorName.classList.add("author");
        authorName.textContent = `Author: ${result.user}`;
        
        const likes = document.createElement("p");
        likes.classList.add("likes");
        likes.textContent = `Likes: ${result.likes}`;
        
        const tags = document.createElement("p");
        tags.classList.add("tags");
        tags.textContent = `Tags: ${result.tags}`;

        infoContainer.appendChild(authorName);
        infoContainer.appendChild(likes);
        infoContainer.appendChild(tags);

        imagewrap.appendChild(image);
        imagewrap.appendChild(imagelink);
        imagewrap.appendChild(infoContainer);
        searchResultel.appendChild(imagewrap);
    });
}

formel.addEventListener("submit", (event) => {
    event.preventDefault();
    inputdata = searchInputel.value; 
    page = 1;
    searchResultel.innerHTML = "";
    fetchImages();
});

showMoreButton.addEventListener('click', () => {
    page++; 
    fetchImages();
});

fetchRandomImages();
