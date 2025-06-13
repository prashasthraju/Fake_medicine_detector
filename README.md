# Fake Medicine Detector

A web application that helps detect counterfeit medicines using image analysis and machine learning. This project provides a user-friendly interface for uploading medicine images and getting instant analysis results.

## Features

- 📸 Image upload and analysis
- 🔍 Real-time medicine verification
- 📊 Confidence scoring system
- 📱 Responsive design
- 🔒 Secure MongoDB storage
- 🚀 Fast and efficient processing

## Tech Stack

- **Frontend:**
  - HTML5
  - CSS3
  - JavaScript (ES6+)
  - Modern UI/UX design

- **Backend:**
  - Node.js
  - Express.js
  - MongoDB
  - Multer (for file handling)

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v14 or higher)
- MongoDB (v4.4 or higher)
- npm (Node Package Manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Fake_medicine_detector.git
cd Fake_medicine_detector
```

2. Install dependencies:
```bash
npm install
```

3. Set up MongoDB:
   - Make sure MongoDB is running on your system
   - The application will connect to `mongodb://localhost:27017/medicine_detector`

4. Start the server:
```bash
node backend/app.js
```

5. Open the application:
   - Navigate to `http://localhost:3000` in your web browser

## Project Structure

```
Fake_medicine_detector/
├── backend/
│   ├── models/
│   │   └── Medicine.js
│   └── app.js
├── scripts/
│   └── index.js
├── styles/
│   └── index.css
├── index.html
├── package.json
└── README.md
```

## API Endpoints

- `GET /api/test` - Test backend connection
- `POST /api/upload` - Upload medicine image
- `GET /api/medicines` - Get all uploaded medicines
- `GET /api/medicines/:id` - Get specific medicine image

## Usage

1. Open the application in your web browser
2. Click "Choose Medicine Image" to select an image
3. Click "Upload and Analyze" to process the image
4. View the analysis results and confidence score
5. Browse previously uploaded images in the gallery

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security

- All uploaded images are stored securely in MongoDB
- File type validation ensures only image files are processed
- CORS is enabled for secure cross-origin requests

## Future Enhancements

- [ ] Implement machine learning model for better detection
- [ ] Add user authentication
- [ ] Support for batch image processing
- [ ] Detailed analysis reports
- [ ] Mobile application version

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for their invaluable tools and libraries

## Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)
Project Link: [https://github.com/yourusername/Fake_medicine_detector](https://github.com/yourusername/Fake_medicine_detector) 