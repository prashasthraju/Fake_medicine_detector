const mongoose = require('mongoose');

const medicineSchema = new mongoose.Schema({
    image: {
        data: Buffer,
        contentType: String
    },
    filename: String,
    uploadDate: {
        type: Date,
        default: Date.now
    },
    analysisResult: {
        type: String,
        default: 'pending'
    },
    confidence: {
        type: Number,
        default: 0
    }
});

module.exports = mongoose.model('Medicine', medicineSchema); 