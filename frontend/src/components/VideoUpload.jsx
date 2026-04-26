import React, { useState, useCallback } from 'react';
import axios from 'axios';

const VideoUpload = ({ onVideoProcessed }) => {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    // Validate file type
    const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime'];
    if (!allowedTypes.includes(file.type)) {
      setUploadStatus({ type: 'error', message: 'Please select a valid video file (MP4, AVI, MOV)' });
      return;
    }

    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      setUploadStatus({ type: 'error', message: 'File size must be less than 100MB' });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/api/video/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });

      setUploadStatus({
        type: 'success',
        message: `Video uploaded successfully! Processing...`
      });

      // Automatically process the video
      const { video_id } = response.data;
      const processResponse = await axios.post('http://localhost:8000/api/video/process', {
        video_id: video_id
      });

      if (processResponse.data.signs && onVideoProcessed) {
        onVideoProcessed(processResponse.data.signs);
      }

      setUploadStatus({
        type: 'success',
        message: `Video processed! Detected ${processResponse.data.signs?.length || 0} signs.`
      });

    } catch (error) {
      console.error('Upload/Process error:', error);
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Upload failed. Please try again.'
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="w-full">
      {/* Upload Area */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-400/10'
            : 'border-gray-600 hover:border-gray-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="video-upload"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept=".mp4,.avi,.mov,.mkv,.webm"
          onChange={handleFileSelect}
          disabled={isUploading}
        />

        <div className="space-y-4">
          <div className="text-4xl text-gray-400">
            {isUploading ? '⏳' : '📹'}
          </div>

          <div>
            <p className="text-lg font-medium text-gray-200">
              {isUploading ? 'Uploading...' : 'Drop your video here'}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              or <label htmlFor="video-upload" className="text-blue-400 hover:text-blue-300 cursor-pointer underline">browse files</label>
            </p>
          </div>

          <div className="text-xs text-gray-500">
            Supported formats: MP4, AVI, MOV, MKV, WebM (max 100MB)
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="mt-4">
          <div className="bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-400 mt-2">{uploadProgress}% uploaded</p>
        </div>
      )}

      {/* Status Message */}
      {uploadStatus && (
        <div className={`mt-4 p-3 rounded-lg ${
          uploadStatus.type === 'success'
            ? 'bg-green-900/50 border border-green-500 text-green-200'
            : 'bg-red-900/50 border border-red-500 text-red-200'
        }`}>
          <p className="text-sm">{uploadStatus.message}</p>
        </div>
      )}
    </div>
  );
};

export default VideoUpload;