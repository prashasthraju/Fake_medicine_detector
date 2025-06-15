const express = require('express');
const cors = require('cors');
const { connectWithRetry } = require('./config/database');
const medicineRoutes = require('./routes/medicineRoutes');
const path = require('path');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());

// Parse JSON bodies
app.use(express.json());

// Serve static files from the root directory, but only for non-API routes
app.use((req, res, next) => {
    if (!req.path.startsWith('/api')) {
        express.static(path.join(__dirname, '..'))(req, res, next);
    } else {
        next();
    }
});

// Use medicine routes
app.use('/api', medicineRoutes);

// Initial database connection
connectWithRetry();

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
