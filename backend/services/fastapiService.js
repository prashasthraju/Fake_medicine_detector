const axios = require('axios');
require('dotenv').config();

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

async function verifyMedicineWithFastAPI(imageBuffer) {
    try {
        // Mock response for now
        return {
            isAuthentic: Math.random() > 0.5,
            confidence: Math.random() * 100,
            details: {
                colorMatch: Math.random() > 0.3,
                textureMatch: Math.random() > 0.3,
                shapeMatch: Math.random() > 0.3,
                printQuality: Math.random() > 0.3
            }
        };
    } catch (error) {
        console.error('Error calling FastAPI:', error);
        throw new Error('Failed to verify medicine');
    }
}

module.exports = {
    verifyMedicineWithFastAPI
}; 