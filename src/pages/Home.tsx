import React, { useState, useCallback, useRef } from 'react'
import { Upload, AlertCircle, CheckCircle, Loader2, X, Shield, CheckCircle2, AlertTriangle, Clock, Camera } from 'lucide-react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

interface UploadedImage {
  id: string
  file: File
  preview: string
}

interface AnalysisResult {
  id: string
  imageId: string
  isAuthentic: boolean
  confidence: number
  details: string
}

const Home = () => {
  const { user } = useAuth()
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([])
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({})
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files)
      handleFiles(files)
    }
  }

  const handleFiles = (files: File[]) => {
    const newImages = files.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      preview: URL.createObjectURL(file)
    }))

    setUploadedImages(prev => [...prev, ...newImages])
  }

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setShowCamera(true)
    } catch (err) {
      console.error('Error accessing camera:', err)
      alert('Could not access camera. Please make sure you have granted camera permissions.')
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      stream.getTracks().forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
    setShowCamera(false)
  }

  const captureImage = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas')
      canvas.width = videoRef.current.videoWidth
      canvas.height = videoRef.current.videoHeight
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0)
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], `camera-capture-${Date.now()}.jpg`, { type: 'image/jpeg' })
            handleFiles([file])
            stopCamera()
          }
        }, 'image/jpeg')
      }
    }
  }

  const analyzeImage = async (imageId: string) => {
    const image = uploadedImages.find(img => img.id === imageId)
    if (!image) return

    setIsAnalyzing(true)
    setUploadProgress(prev => ({ ...prev, [imageId]: 0 }))

    const formData = new FormData()
    formData.append('image', image.file)

    try {
      const response = await axios.post('http://localhost:3000/api/verify', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0
          setUploadProgress(prev => ({ ...prev, [imageId]: progress }))
        },
      })

      setAnalysisResults(prev => [
        ...prev,
        {
          id: Math.random().toString(36).substr(2, 9),
          imageId,
          isAuthentic: response.data.isAuthentic,
          confidence: response.data.confidence,
          details: response.data.details,
        },
      ])
    } catch (error) {
      console.error('Error analyzing image:', error)
      alert('Error analyzing image. Please try again.')
    } finally {
      setIsAnalyzing(false)
      setUploadProgress(prev => ({ ...prev, [imageId]: 100 }))
    }
  }

  const removeImage = (imageId: string) => {
    setUploadedImages(prev => prev.filter(img => img.id !== imageId))
    setAnalysisResults(prev => prev.filter(result => result.imageId !== imageId))
    setUploadProgress(prev => {
      const newProgress = { ...prev }
      delete newProgress[imageId]
      return newProgress
    })
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">Fake Medicine Detector</h1>
        
        {/* Upload Section */}
        <div className="mb-8">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center ${
              isDragging ? 'border-primary bg-primary/10' : 'border-gray-300'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/*"
              multiple
              className="hidden"
            />
            <div className="space-y-6">
              <div className="flex justify-center">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-8 py-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-3 text-lg font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
                >
                  <Upload className="w-6 h-6" />
                  Upload Medicine Images
                </button>
              </div>
              <div className="flex justify-center gap-4">
                <button
                  onClick={showCamera ? stopCamera : startCamera}
                  className="px-6 py-3 bg-secondary text-white rounded-lg hover:bg-secondary/90 transition-colors flex items-center gap-2 shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all"
                >
                  <Camera className="w-5 h-5" />
                  {showCamera ? 'Stop Camera' : 'Use Camera'}
                </button>
              </div>
              <p className="text-gray-600">
                or drag and drop your medicine images here
              </p>
            </div>
          </div>
        </div>

        {/* Camera View */}
        {showCamera && (
          <div className="mt-8">
            <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
              />
              <button
                onClick={captureImage}
                className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-6 py-3 bg-primary text-white rounded-full hover:bg-primary/90 transition-colors"
              >
                Capture
              </button>
            </div>
          </div>
        )}

        {/* Uploaded Images */}
        {uploadedImages.length > 0 && (
          <div className="mt-8 space-y-4">
            <h2 className="text-2xl font-semibold">Uploaded Images</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {uploadedImages.map((image) => (
                <div key={image.id} className="relative group">
                  <div className="aspect-square rounded-lg overflow-hidden bg-gray-100">
                    <img
                      src={image.preview}
                      alt="Uploaded medicine"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <button
                    onClick={() => removeImage(image.id)}
                    className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  {uploadProgress[image.id] !== undefined && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200">
                      <div
                        className="h-full bg-primary transition-all duration-300"
                        style={{ width: `${uploadProgress[image.id]}%` }}
                      />
                    </div>
                  )}
                  {!analysisResults.find(result => result.imageId === image.id) && (
                    <button
                      onClick={() => analyzeImage(image.id)}
                      disabled={isAnalyzing}
                      className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                    >
                      {isAnalyzing ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        'Analyze'
                      )}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisResults.length > 0 && (
          <div className="mt-8 space-y-4">
            <h2 className="text-2xl font-semibold">Analysis Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysisResults.map((result) => {
                const image = uploadedImages.find(img => img.id === result.imageId)
                if (!image) return null

                return (
                  <div
                    key={result.id}
                    className={`p-4 rounded-lg ${
                      result.isAuthentic
                        ? 'bg-green-50 border border-green-200'
                        : 'bg-red-50 border border-red-200'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        {result.isAuthentic ? (
                          <CheckCircle className="w-8 h-8 text-green-500" />
                        ) : (
                          <AlertCircle className="w-8 h-8 text-red-500" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">
                          {result.isAuthentic ? 'Authentic Medicine' : 'Fake Medicine'}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Confidence: {result.confidence}%
                        </p>
                        <p className="text-sm text-gray-600 mt-2">{result.details}</p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Mission Statement */}
      <div className="bg-white rounded-lg shadow-sm p-8 border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Our Mission</h2>
        <p className="text-gray-600 mb-6">
          At MediCheck, we are committed to combating the global issue of counterfeit medications.
          Our mission is to provide accessible, reliable, and user-friendly tools that help individuals
          and healthcare providers verify the authenticity of medications.
        </p>
        <p className="text-gray-600">
          Through the power of artificial intelligence and machine learning, we aim to create a safer
          healthcare environment by reducing the risks associated with counterfeit medications and
          protecting public health.
        </p>
      </div>
    </div>
  )
}

export default Home 