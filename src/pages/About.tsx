import React from 'react'
import { Shield, CheckCircle, AlertTriangle, Clock } from 'lucide-react'

const About = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-16 h-16 medical-gradient rounded-full mb-4">
          <Shield className="h-8 w-8 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">About MediCheck</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Your trusted partner in ensuring medication safety through advanced AI-powered verification.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
          <div className="w-12 h-12 medical-gradient rounded-lg flex items-center justify-center mb-4">
            <CheckCircle className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Accurate Verification</h3>
          <p className="text-gray-600">
            Our advanced AI technology provides highly accurate verification of medication authenticity,
            helping you make informed decisions about your health.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
          <div className="w-12 h-12 medical-gradient rounded-lg flex items-center justify-center mb-4">
            <AlertTriangle className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Fake Detection</h3>
          <p className="text-gray-600">
            Quickly identify counterfeit medications through our comprehensive analysis of packaging,
            labeling, and physical characteristics.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-100">
          <div className="w-12 h-12 medical-gradient rounded-lg flex items-center justify-center mb-4">
            <Clock className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Instant Results</h3>
          <p className="text-gray-600">
            Get immediate verification results with our fast and efficient processing system,
            saving you time and providing peace of mind.
          </p>
        </div>
      </div>

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

export default About 