const express = require('express');
const router = express.Router();
const upload = require('../middleware/upload');
const Medicine = require('../models/Medicine');
const { verifyMedicineWithFastAPI } = require('../services/fastapiService');
const { isConnected } = require('../config/database');

// Basic test route
router.get('/test', (req, res) => {
    res.json({ message: 'Backend is connected!' });
});

// Handle image upload and verification
router.post('/upload', upload.single('medicineImage'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        // Check MongoDB connection
        if (!isConnected()) {
            throw new Error('Database connection not ready');
        }

        // Get verification result from FastAPI
        const verificationResult = await verifyMedicineWithFastAPI(req.file.buffer);

        // Create new medicine document
        const medicine = new Medicine({
            image: {
                data: req.file.buffer,
                contentType: req.file.mimetype
            },
            filename: req.file.originalname,
            analysisResult: verificationResult.isAuthentic ? 'authentic' : 'counterfeit',
            confidence: verificationResult.confidence,
            verificationDetails: verificationResult.details
        });

        // Save to MongoDB
        await medicine.save();

        res.json({
            message: 'File uploaded and analyzed successfully',
            result: {
                id: medicine._id,
                filename: medicine.filename,
                uploadDate: medicine.uploadDate,
                isAuthentic: verificationResult.isAuthentic,
                confidence: verificationResult.confidence,
                details: verificationResult.details
            }
        });
    } catch (error) {
        console.error('Upload error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get all medicines
router.get('/medicines', async (req, res) => {
    try {
        // Check MongoDB connection
        if (!isConnected()) {
            throw new Error('Database connection not ready');
        }

        const medicines = await Medicine.find({}, 'filename uploadDate analysisResult confidence verificationDetails');
        res.json(medicines || []); // Ensure we always return an array
    } catch (error) {
        console.error('Error fetching medicines:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get specific medicine image
router.get('/medicines/:id', async (req, res) => {
    try {
        // Check MongoDB connection
        if (!isConnected()) {
            throw new Error('Database connection not ready');
        }

        const medicine = await Medicine.findById(req.params.id);
        if (!medicine) {
            return res.status(404).json({ error: 'Medicine not found' });
        }
        res.set('Content-Type', medicine.image.contentType);
        res.send(medicine.image.data);
    } catch (error) {
        console.error('Error fetching medicine image:', error);
        res.status(500).json({ error: error.message });
    }
});

// Delete medicine
router.delete('/medicines/:id', async (req, res) => {
    try {
        // Check MongoDB connection
        if (!isConnected()) {
            throw new Error('Database connection not ready');
        }

        const medicine = await Medicine.findByIdAndDelete(req.params.id);
        if (!medicine) {
            return res.status(404).json({ error: 'Medicine not found' });
        }
        res.json({ message: 'Medicine deleted successfully' });
    } catch (error) {
        console.error('Error deleting medicine:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 