document.querySelectorAll('.product').forEach(product => {
    product.addEventListener('click', function() {
        const productTitle = this.querySelector('h2').innerText;
        const productDescription = this.querySelector('p').innerText;

        document.getElementById('selected-product-title').innerText = productTitle;
        document.getElementById('selected-product-description').innerText = productDescription;

        document.getElementById('image-generator').classList.remove('hidden');

        // Add code here to load suggestions based on the selected product
        loadSuggestions(product.id);
    });
});

function generateImage() {
    const prompt = document.getElementById('prompt-input').value;

    if (prompt) {
        // Implement the AI image generation API call here
        alert(`Generating image for prompt: "${prompt}"`);

        // Placeholder: Set the generated image
        document.getElementById('output-image').src = 'images/generated-placeholder.jpg';
    } else {
        alert('Please enter a prompt to generate an image.');
    }
}

function loadSuggestions(productId) {
    // Implement logic to load suggestions based on the selected product type
    alert(`Loading suggestions for ${productId}`);
    // Example: Set some placeholder images for suggestions
    const suggestions = document.getElementById('suggestions');
    suggestions.innerHTML = `<img src="images/suggestion1.jpg" alt="Suggestion 1">
                             <img src="images/suggestion2.jpg" alt="Suggestion 2">
                             <img src="images/suggestion3.jpg" alt="Suggestion 3">`;
}
