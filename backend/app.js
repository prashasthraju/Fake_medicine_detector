const express = require('express');
const cors = require('cors');
const multer = require('multer');
const mongoose = require('mongoose');
const Medicine = require('./models/Medicine');
require('dotenv').config();

const app = express();
const port = 3000;

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/medicine_detector')
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('MongoDB connection error:', err));

// Enable CORS for all routes
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Configure multer for memory storage
const upload = multer({
    storage: multer.memoryStorage(),
    fileFilter: function (req, file, cb) {
        // Accept images only
        if (!file.originalname.match(/\.(jpg|jpeg|png|gif)$/)) {
            return cb(new Error('Only image files are allowed!'), false);
        }
        cb(null, true);
    }
});

// Serve static files from the root directory
app.use(express.static('../'));

// Basic test route
app.get('/api/test', (req, res) => {
    res.json({ message: 'Backend is connected!' });
});

// Handle image upload
app.post('/api/upload', upload.single('medicineImage'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        // Create new medicine document
        const medicine = new Medicine({
            image: {
                data: req.file.buffer,
                contentType: req.file.mimetype
            },
            filename: req.file.originalname
        });

        // Save to MongoDB
        await medicine.save();

        res.json({
            message: 'File uploaded successfully',
            file: {
                id: medicine._id,
                filename: medicine.filename,
                uploadDate: medicine.uploadDate
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get all medicines
app.get('/api/medicines', async (req, res) => {
    try {
        const medicines = await Medicine.find({}, 'filename uploadDate analysisResult confidence');
        res.json(medicines);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get specific medicine image
app.get('/api/medicines/:id', async (req, res) => {
    try {
        const medicine = await Medicine.findById(req.params.id);
        if (!medicine) {
            return res.status(404).json({ error: 'Medicine not found' });
        }
        res.set('Content-Type', medicine.image.contentType);
        res.send(medicine.image.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
