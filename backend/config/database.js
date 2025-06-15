const mongoose = require('mongoose');
require('dotenv').config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/medicine_detector';

const mongooseOptions = {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
};

let isConnected = false;

async function connectWithRetry() {
    if (isConnected) {
        return;
    }

    try {
        await mongoose.connect(MONGODB_URI, mongooseOptions);
        isConnected = true;
        console.log('Successfully connected to MongoDB.');
    } catch (error) {
        console.error('MongoDB connection error:', error);
        console.log('Retrying connection in 5 seconds...');
        setTimeout(connectWithRetry, 5000);
    }
}

// Handle MongoDB connection events
mongoose.connection.on('error', (err) => {
    console.error('MongoDB connection error:', err);
    isConnected = false;
});

mongoose.connection.on('disconnected', () => {
    console.log('MongoDB disconnected. Attempting to reconnect...');
    isConnected = false;
    connectWithRetry();
});

mongoose.connection.on('connected', () => {
    isConnected = true;
    console.log('MongoDB connected successfully');
});

module.exports = {
    connectWithRetry,
    mongoose,
    isConnected: () => isConnected
}; 