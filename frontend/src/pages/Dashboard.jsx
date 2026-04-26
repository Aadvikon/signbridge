import React from 'react';
import VideoUpload from '../components/VideoUpload';
import Avatar from '../components/Avatar';
import SignDisplay from '../components/SignDisplay';
import useSignBridge from '../hooks/useSignBridge';

const Dashboard = () => {
  const { uploadVideo, signs, currentSign, isProcessing, error } = useSignBridge();

  const handleVideoProcessed = (detectedSigns) => {
    // The hook will handle updating signs and currentSign
    console.log('Video processed with signs:', detectedSigns);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-blue-400">SignBridge</h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Dashboard
              </a>
              <a href="#" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Videos
              </a>
              <a href="#" className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Settings
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Side - Video Upload */}
            <div className="bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-100">Upload Video</h2>
              <VideoUpload onVideoProcessed={handleVideoProcessed} />
            </div>

            {/* Right Side - 3D Avatar */}
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-100">3D Avatar</h2>
                <div className="h-96">
                  <Avatar currentSign={currentSign} />
                </div>
              </div>

              {/* Sign Display */}
              <SignDisplay
                currentSign={currentSign}
                signsHistory={signs}
                isProcessing={isProcessing}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;