// Test backend connection
async function testBackendConnection() {
    const statusDiv = document.getElementById('connection-status');
    try {
        const response = await fetch('http://localhost:3000/api/test');
        const data = await response.json();
        console.log('Backend response:', data);
        statusDiv.style.backgroundColor = '#d4edda';
        statusDiv.style.color = '#155724';
        statusDiv.textContent = '✅ Backend connected successfully!';
    } catch (error) {
        console.error('Error connecting to backend:', error);
        statusDiv.style.backgroundColor = '#f8d7da';
        statusDiv.style.color = '#721c24';
        statusDiv.textContent = '❌ Error connecting to backend. Make sure the server is running.';
    }
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    try {
        const response = await fetch('http://localhost:3000/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('Upload result:', result);
        
        // Refresh the image list
        loadImages();
        
        // Reset the form
        form.reset();
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('Error uploading image. Please try again.');
    }
}

// Load and display images
async function loadImages() {
    try {
        const response = await fetch('http://localhost:3000/api/medicines');
        const medicines = await response.json();
        
        const imageList = document.getElementById('imageList');
        imageList.innerHTML = '';
        
        medicines.forEach(medicine => {
            const card = document.createElement('div');
            card.className = 'image-card';
            
            card.innerHTML = `
                <img src="http://localhost:3000/api/medicines/${medicine._id}" alt="${medicine.filename}">
                <div class="image-info">
                    <h3>${medicine.filename}</h3>
                    <p>Uploaded: ${new Date(medicine.uploadDate).toLocaleString()}</p>
                    <p>Status: ${medicine.analysisResult}</p>
                    <p>Confidence: ${medicine.confidence}%</p>
                </div>
            `;
            
            imageList.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading images:', error);
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    testBackendConnection();
    loadImages();
    
    // Add form submit handler
    const form = document.getElementById('uploadForm');
    form.addEventListener('submit', handleFormSubmit);
});
