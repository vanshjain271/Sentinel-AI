import React from 'react';
import { Brain, AlertTriangle, Shield, X } from 'lucide-react';

interface AIExplanationProps {
  explanation: {
    prediction: string;
    confidence: number;
    top_factors?: Array<{
      feature: string;
      impact: number;
      value?: number;
    }>;
    risk_factors?: string[];
    decision_basis?: string;
    model_confidence?: string;
  };
  onClose?: () => void;
}

export default function AIExplanation({ explanation, onClose }: AIExplanationProps) {
  // Ensure we have safe defaults
  const safeExplanation = {
    prediction: explanation?.prediction || 'normal',
    confidence: explanation?.confidence || 0.5,
    top_factors: explanation?.top_factors || [],
    risk_factors: explanation?.risk_factors || [],
    decision_basis: explanation?.decision_basis || 'No explanation available',
    model_confidence: explanation?.model_confidence || `${(explanation?.confidence || 0.5) * 100}%`
  };

  const isDDoS = safeExplanation.prediction.toLowerCase() === 'ddos';

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 border border-purple-900/50 shadow-2xl">
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-900/30 rounded-lg">
            <Brain className="w-8 h-8 text-purple-400" />
          </div>
          <div>
            <h3 className="text-2xl font-bold">AI Detection Analysis</h3>
            <p className="text-gray-400 text-sm">Understanding why this was flagged</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Prediction Card */}
        <div className={`p-5 rounded-xl ${isDDoS ? 'bg-gradient-to-br from-red-900/30 to-red-800/20' : 'bg-gradient-to-br from-green-900/30 to-green-800/20'}`}>
          <div className="flex items-center justify-between mb-3">
            <span className="font-bold text-lg">Verdict</span>
            <span className={`px-3 py-1 rounded-full text-sm font-bold ${isDDoS ? 'bg-red-600' : 'bg-green-600'}`}>
              {safeExplanation.prediction.toUpperCase()}
            </span>
          </div>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Confidence</span>
                <span className="font-mono">{safeExplanation.model_confidence}</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${isDDoS ? 'bg-red-500' : 'bg-green-500'}`}
                  style={{ width: `${safeExplanation.confidence * 100}%` }}
                />
              </div>
            </div>
            <p className="text-sm text-gray-300">{safeExplanation.decision_basis}</p>
          </div>
        </div>

        {/* Risk Factors */}
        <div className="p-5 rounded-xl bg-gradient-to-br from-yellow-900/20 to-yellow-800/10">
          <h4 className="font-bold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            Risk Factors
          </h4>
          <ul className="space-y-2">
            {safeExplanation.risk_factors.length > 0 ? (
              safeExplanation.risk_factors.map((factor, idx) => (
                <li key={idx} className="flex items-start gap-2 p-2 bg-yellow-900/10 rounded">
                  <div className="w-2 h-2 rounded-full bg-yellow-500 mt-2 flex-shrink-0" />
                  <span className="text-sm">{factor}</span>
                </li>
              ))
            ) : (
              <li className="text-gray-400 text-sm p-2">No significant risk factors detected</li>
            )}
          </ul>
        </div>

        {/* Model Info */}
        <div className="p-5 rounded-xl bg-gradient-to-br from-blue-900/20 to-blue-800/10">
          <h4 className="font-bold mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-400" />
            Model Insights
          </h4>
          <p className="text-sm text-gray-300 mb-4">
            This analysis uses an ensemble of machine learning models trained on 5G network traffic patterns.
          </p>
          <div className="text-xs text-gray-400">
            <div className="flex justify-between py-1 border-b border-gray-800">
              <span>Analysis Type</span>
              <span>Real-time ML</span>
            </div>
            <div className="flex justify-between py-1 border-b border-gray-800">
              <span>Features Analyzed</span>
              <span>{safeExplanation.top_factors.length}</span>
            </div>
            <div className="flex justify-between py-1">
              <span>Detection Method</span>
              <span>Behavioral Analysis</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Contributing Features */}
      {safeExplanation.top_factors.length > 0 && (
        <div className="mt-8">
          <h4 className="font-bold mb-4 text-lg">Top Contributing Features</h4>
          <div className="space-y-3">
            {safeExplanation.top_factors.map((factor, idx) => (
              <div key={idx} className="bg-gray-800/50 p-4 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="font-mono text-sm">{factor.feature}</span>
                    {factor.value !== undefined && (
                      <span className="text-xs text-gray-400 ml-2">
                        (value: {typeof factor.value === 'number' ? factor.value.toFixed(3) : 'N/A'})
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-40 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${factor.impact > 0 ? 'bg-red-500' : 'bg-blue-500'}`}
                        style={{ width: `${Math.min(Math.abs(factor.impact) * 100, 100)}%` }}
                      />
                    </div>
                    <span className={`font-mono text-sm ${factor.impact > 0 ? 'text-red-400' : 'text-blue-400'}`}>
                      {factor.impact > 0 ? '+' : ''}{typeof factor.impact === 'number' ? factor.impact.toFixed(3) : '0.000'}
                    </span>
                  </div>
                </div>
                <div className="text-xs text-gray-400">
                  {factor.impact > 0.5 ? 'Strong indicator of attack' : 
                   factor.impact > 0.2 ? 'Moderate indicator' : 
                   'Weak indicator'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}