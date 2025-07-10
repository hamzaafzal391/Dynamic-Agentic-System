'use client'

import { motion } from 'framer-motion'
import { 
  Activity, 
  Clock, 
  FileText, 
  Database, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Zap
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import type { ProcessingTrace, Persona } from '@/types'

interface RightPanelProps {
  processingTrace: ProcessingTrace | null
  selectedPersona: Persona | null
}

export function RightPanel({ processingTrace, selectedPersona }: RightPanelProps) {
  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-400" />
      case 'processing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-400" />
      default:
        return <div className="h-4 w-4 rounded-full border-2 border-gray-400" />
    }
  }

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-400 bg-green-400/10'
      case 'processing':
        return 'border-blue-400 bg-blue-400/10'
      case 'error':
        return 'border-red-400 bg-red-400/10'
      default:
        return 'border-gray-400 bg-gray-400/10'
    }
  }

  return (
    <div className="h-full flex flex-col p-4 space-y-4">
      {/* Processing Trace */}
      {processingTrace && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          <Card className="bg-black/20 border-white/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Processing Trace</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm text-gray-300 mb-3">
                <p className="font-medium">Query:</p>
                <p className="text-gray-400 italic">"{processingTrace.query}"</p>
              </div>
              
              <div className="space-y-2">
                {processingTrace.steps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`flex items-center space-x-3 p-2 rounded-lg border ${getStepColor(step.status)}`}
                  >
                    {getStepIcon(step.status)}
                    <div className="flex-1">
                      <p className="text-sm font-medium text-white">{step.name}</p>
                      {step.duration && (
                        <p className="text-xs text-gray-400">{step.duration}ms</p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
              
              {processingTrace.totalDuration > 0 && (
                <div className="pt-3 border-t border-white/10">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-300">Total Time:</span>
                    <span className="text-white font-medium">
                      {processingTrace.totalDuration}ms
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Selected Persona Info */}
      {selectedPersona && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-black/20 border-white/10">
            <CardHeader className="pb-3">
              <CardTitle className="text-white flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>Active Persona</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{selectedPersona.icon}</div>
                <div>
                  <h4 className="font-medium text-white">{selectedPersona.name}</h4>
                  <p className="text-sm text-gray-400">{selectedPersona.description}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* System Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="bg-black/20 border-white/10">
          <CardHeader className="pb-3">
            <CardTitle className="text-white flex items-center space-x-2">
              <Database className="h-5 w-5" />
              <span>System Stats</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Documents Indexed</span>
              <span className="text-white font-medium">12</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Datasets Available</span>
              <span className="text-white font-medium">3</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Active Agents</span>
              <span className="text-white font-medium">3</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Avg Response Time</span>
              <span className="text-white font-medium">2.3s</span>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card className="bg-black/20 border-white/10">
          <CardHeader className="pb-3">
            <CardTitle className="text-white flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Recent Activity</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { action: 'Document uploaded', time: '2 min ago', type: 'upload' },
              { action: 'Query processed', time: '5 min ago', type: 'query' },
              { action: 'Dataset indexed', time: '10 min ago', type: 'index' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-gray-300">{activity.action}</span>
                <span className="text-gray-400">{activity.time}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
} 