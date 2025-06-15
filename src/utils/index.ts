// DOM Elements
const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const resultsSection = document.getElementById('resultsSection');
const resultImage = document.getElementById('resultImage');
const resultTitle = document.getElementById('resultTitle');
const resultStatus = document.getElementById('resultStatus');
const verificationList = document.getElementById('verificationList');
const imageGrid = document.getElementById('imageGrid');
const optionButtons = document.querySelectorAll('.option-btn');

// State
let selectedOption = 'packaging';

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadImages();
    setupDragAndDrop();
    setupOptionButtons();
});

// Setup drag and drop functionality
function setupDragAndDrop() {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropArea.classList.add('dragover');
    }

    function unhighlight(e) {
        dropArea.classList.remove('dragover');
    }

    dropArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);
}

// Setup option buttons
function setupOptionButtons() {
    optionButtons.forEach(button => {
        button.addEventListener('click', () => {
            optionButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            selectedOption = button.dataset.option;
        });
    });
}

// Handle file selection
function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

// Handle dropped files
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

// Process files
function handleFiles(files) {
    if (files.length === 0) return;
    
    const file = files[0];
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
    }

    uploadFile(file);
}

// Upload file to server
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('medicineImage', file);
    formData.append('type', selectedOption);

    try {
        const response = await fetch('http://localhost:3000/api/medicines/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();
        showResults(data);
        loadImages();
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to upload image. Please try again.');
    }
}

// Show analysis results
function showResults(data) {
    resultsSection.style.display = 'block';
    resultImage.src = `http://localhost:3000/api/medicines/image/${data._id}`;
    resultTitle.textContent = data.name || 'Unknown Medicine';
    
    const statusSpan = resultStatus.querySelector('span');
    statusSpan.textContent = data.isAuthentic ? 'Authentic' : 'Counterfeit';
    statusSpan.className = data.isAuthentic ? 'text-success' : 'text-danger';

    // Clear and populate verification list
    verificationList.innerHTML = '';
    if (data.verificationPoints) {
        data.verificationPoints.forEach(point => {
            const li = document.createElement('li');
            li.textContent = point;
            verificationList.appendChild(li);
        });
    }

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Load uploaded images
async function loadImages() {
    try {
        const response = await fetch('http://localhost:3000/api/medicines');
        if (!response.ok) {
            throw new Error('Failed to fetch images');
        }

        const medicines = await response.json();
        displayImages(medicines);
    } catch (error) {
        console.error('Error:', error);
        imageGrid.innerHTML = '<p class="error-message">Failed to load images. Please try again later.</p>';
    }
}

// Display images in grid
function displayImages(medicines) {
    if (medicines.length === 0) {
        imageGrid.innerHTML = '<p class="no-images">No images uploaded yet</p>';
        return;
    }

    imageGrid.innerHTML = medicines.map(medicine => `
        <div class="image-card">
            <img src="http://localhost:3000/api/medicines/image/${medicine._id}" alt="${medicine.name || 'Medicine'}">
            <div class="image-info">
                <h3>${medicine.name || 'Unknown Medicine'}</h3>
                <p>Status: <span class="${medicine.isAuthentic ? 'text-success' : 'text-danger'}">
                    ${medicine.isAuthentic ? 'Authentic' : 'Counterfeit'}
                </span></p>
                <button class="delete-btn" onclick="deleteMedicine('${medicine._id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Delete medicine
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
            const error = await response.json();
            throw new Error(error.message || 'Failed to delete image');
        }

        loadImages();
    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'Failed to delete image. Please try again.');
    }
}
