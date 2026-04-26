import React from 'react';

const SignDisplay = ({ currentSign, confidence, signsHistory, isProcessing }) => {
  return (
    <div className="w-full bg-gray-800 rounded-lg p-4 space-y-4">
      {/* Current Sign Display */}
      <div className="text-center">
        {currentSign ? (
          <div className="animate-in slide-in-from-bottom-4 duration-500">
            <div className="text-4xl font-bold text-white mb-2">
              {currentSign.replace(/_/g, ' ')}
            </div>
            {confidence && (
              <div className="text-lg text-green-400">
                {Math.round(confidence * 100)}% confidence
              </div>
            )}
          </div>
        ) : isProcessing ? (
          <div className="text-xl text-gray-400">
            Processing video...
          </div>
        ) : (
          <div className="text-xl text-gray-400">
            Upload a video to begin
          </div>
        )}
      </div>

      {/* Signs Timeline */}
      {signsHistory && signsHistory.length > 0 && (
        <div className="border-t border-gray-600 pt-4">
          <h3 className="text-lg font-semibold text-white mb-3">Detected Signs</h3>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
            {signsHistory.map((sign, index) => (
              <div
                key={index}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-all duration-300 ${
                  index === signsHistory.length - 1
                    ? 'bg-blue-600 text-white animate-pulse'
                    : 'bg-gray-700 text-gray-300'
                }`}
              >
                {sign.sign.replace(/_/g, ' ')}
                {sign.confidence && (
                  <span className="ml-1 text-xs opacity-75">
                    ({Math.round(sign.confidence * 100)}%)
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
        </div>
      )}
    </div>
  );
};

export default SignDisplay;