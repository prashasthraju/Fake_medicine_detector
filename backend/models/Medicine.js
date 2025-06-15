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
        enum: ['authentic', 'counterfeit', 'pending'],
        default: 'pending'
    },
    confidence: {
        type: Number,
        default: 0
    },
    verificationDetails: {
        colorMatch: Boolean,
        textureMatch: Boolean,
        shapeMatch: Boolean,
        printQuality: Boolean
    }
});

module.exports = mongoose.model('Medicine', medicineSchema); 