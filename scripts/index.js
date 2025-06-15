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

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    const fileNameDiv = document.getElementById('selectedFileName');
    
    if (file) {
        fileNameDiv.textContent = `Selected: ${file.name}`;
        fileNameDiv.style.color = '#28a745';
    } else {
        fileNameDiv.textContent = '';
    }
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const fileInput = form.querySelector('input[type="file"]');
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Please select an image file first');
        return;
    }
    
    const formData = new FormData(form);
    
    try {
        submitButton.disabled = true;
        submitButton.textContent = 'Analyzing...';
        
        const response = await fetch('http://localhost:3000/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Upload result:', result);
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Show result alert
        const resultMessage = result.result.isAuthentic ? 
            `✅ Medicine appears to be authentic (${result.result.confidence.toFixed(1)}% confidence)` :
            `❌ Medicine appears to be counterfeit (${result.result.confidence.toFixed(1)}% confidence)`;
        
        alert(resultMessage);
        
        // Refresh the image list
        loadImages();
        
        // Reset the form
        form.reset();
        document.getElementById('selectedFileName').textContent = '';
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('Error uploading image: ' + error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Upload and Analyze';
    }
}

// Delete medicine image
async function deleteMedicine(id) {
    if (!confirm('Are you sure you want to delete this image?')) {
        return;
    }

    try {
        const response = await fetch(`http://localhost:3000/api/medicines/${id}`, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Delete result:', result);

        // Refresh the image list
        loadImages();
    } catch (error) {
        console.error('Error deleting image:', error);
        alert('Error deleting image: ' + error.message);
    }
}

// Load and display images
async function loadImages() {
    try {
        const response = await fetch('http://localhost:3000/api/medicines');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const medicines = await response.json();
        
        if (!Array.isArray(medicines)) {
            console.error('Invalid response format:', medicines);
            return;
        }
        
        const imageList = document.getElementById('imageList');
        imageList.innerHTML = '';
        
        if (medicines.length === 0) {
            imageList.innerHTML = '<p class="no-images">No images uploaded yet</p>';
            return;
        }
        
        medicines.forEach(medicine => {
            const card = document.createElement('div');
            card.className = 'image-card';
            
            const statusColor = medicine.analysisResult === 'authentic' ? '#28a745' : 
                              medicine.analysisResult === 'counterfeit' ? '#dc3545' : '#ffc107';
            
            const detailsList = Object.entries(medicine.verificationDetails || {})
                .map(([key, value]) => `
                    <li class="${value ? 'text-success' : 'text-danger'}">
                        ${key.replace(/([A-Z])/g, ' $1').trim()}: ${value ? '✅' : '❌'}
                    </li>
                `).join('');
            
            card.innerHTML = `
                <img src="http://localhost:3000/api/medicines/${medicine._id}" alt="${medicine.filename}">
                <div class="image-info">
                    <h3>${medicine.filename}</h3>
                    <p>Uploaded: ${new Date(medicine.uploadDate).toLocaleString()}</p>
                    <p style="color: ${statusColor}">
                        Status: ${medicine.analysisResult.toUpperCase()}
                    </p>
                    <p>Confidence: ${medicine.confidence.toFixed(1)}%</p>
                    <div class="verification-details">
                        <h4>Verification Details:</h4>
                        <ul>${detailsList}</ul>
                    </div>
                    <button class="delete-btn" onclick="deleteMedicine('${medicine._id}')">
                        Delete Image
                    </button>
                </div>
            `;
            
            imageList.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading images:', error);
        const imageList = document.getElementById('imageList');
        imageList.innerHTML = '<p class="error-message">Error loading images. Please try again later.</p>';
    }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    testBackendConnection();
    loadImages();
    
    // Add form submit handler
    const form = document.getElementById('uploadForm');
    form.addEventListener('submit', handleFormSubmit);
    
    // Add file input change handler
    const fileInput = document.getElementById('medicineImage');
    fileInput.addEventListener('change', handleFileSelect);
});
