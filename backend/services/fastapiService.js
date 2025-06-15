const axios = require('axios');
require('dotenv').config();

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

async function verifyMedicineWithFastAPI(imageBuffer) {
    try {
        // Convert buffer to form data
        const formData = new FormData();
        formData.append('file', new Blob([imageBuffer]), 'medicine.jpg');

        // Call the ML model API
        const response = await axios.post(`${FASTAPI_URL}/predict`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        // Transform the response to match our expected format
        return {
            isAuthentic: !response.data.is_fake,
            confidence: response.data.confidence * 100,
            details: response.data.model_details
        };
    } catch (error) {
        console.error('Error calling FastAPI:', error);
        throw new Error('Failed to verify medicine');
    }
}

module.exports = {
    verifyMedicineWithFastAPI
}; 