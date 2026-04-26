import { useState, useCallback } from 'react';
import axios from 'axios';

const useSignBridge = () => {
  const [signs, setSigns] = useState([]);
  const [currentSign, setCurrentSign] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const uploadVideo = useCallback(async (file) => {
    setIsProcessing(true);
    setError(null);
    setSigns([]);
    setCurrentSign(null);

    try {
      // First upload the video
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await axios.post('http://localhost:8000/api/video/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { video_id } = uploadResponse.data;

      // Then process the video
      const processResponse = await axios.post('http://localhost:8000/api/video/process', {
        video_id: video_id
      });

      // Handle streaming response or polling for results
      if (processResponse.data.signs) {
        // If signs are returned immediately
        const detectedSigns = processResponse.data.signs;
        setSigns(detectedSigns);

        // Animate through signs with delays
        detectedSigns.forEach((signData, index) => {
          setTimeout(() => {
            setCurrentSign(signData.sign);
          }, index * 2000); // 2 second delay between signs
        });

        // Clear current sign after all animations
        setTimeout(() => {
          setCurrentSign(null);
        }, detectedSigns.length * 2000 + 1000);
      }

    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      console.error('SignBridge error:', err);
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setSigns([]);
    setCurrentSign(null);
    setIsProcessing(false);
    setError(null);
  }, []);

  return {
    uploadVideo,
    signs,
    currentSign,
    isProcessing,
    error,
    reset
  };
};

export default useSignBridge;