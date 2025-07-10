'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  Upload, 
  Database, 
  Settings, 
  Plus,
  DollarSign,
  Scale,
  MessageSquare
} from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { FileUpload } from './FileUpload'
import { uploadFile } from '@/lib/api'
import type { Persona, Dataset } from '@/types'

interface LeftPanelProps {
  selectedPersona: Persona | null
  onPersonaSelect: (persona: Persona) => void
  datasets: Dataset[]
  onDatasetsChange: (datasets: Dataset[]) => void
}

const defaultPersonas: Persona[] = [
  {
    id: 'financial',
    name: 'Financial Analyst',
    description: 'Specialized in stock analysis, market trends, and financial calculations',
    type: 'financial',
    icon: '💰',
    color: 'from-green-500 to-emerald-600'
  },
  {
    id: 'legal',
    name: 'Legal Assistant',
    description: 'Expert in legal document analysis and compliance',
    type: 'legal',
    icon: '⚖️',
    color: 'from-blue-500 to-indigo-600'
  },
  {
    id: 'general',
    name: 'General Assistant',
    description: 'Versatile AI for general queries and calculations',
    type: 'general',
    icon: '🤖',
    color: 'from-purple-500 to-pink-600'
  }
]

export function LeftPanel({ 
  selectedPersona, 
  onPersonaSelect, 
  datasets, 
  onDatasetsChange 
}: LeftPanelProps) {
  const [activeTab, setActiveTab] = useState<'personas' | 'upload' | 'datasets' | 'settings'>('personas')

  const handleFileUpload = async (file: File) => {
    try {
      const response = await uploadFile(file)
      if (response.success) {
        // Refresh datasets after upload
        // This would typically fetch updated datasets from the backend
        console.log('File uploaded successfully:', response)
      }
    } catch (error) {
      console.error('Upload failed:', error)
    }
  }

  return (
    <div className="h-full flex flex-col p-4 space-y-4">
      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-black/20 rounded-lg p-1">
        {[
          { id: 'personas', icon: Users, label: 'Personas' },
          { id: 'upload', icon: Upload, label: 'Upload' },
          { id: 'datasets', icon: Database, label: 'Data' },
          { id: 'settings', icon: Settings, label: 'Settings' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-white/20 text-white shadow-lg'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {activeTab === 'personas' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Select Persona</h3>
            {defaultPersonas.map((persona) => (
              <motion.div
                key={persona.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card 
                  className={`cursor-pointer transition-all ${
                    selectedPersona?.id === persona.id
                      ? 'ring-2 ring-blue-400 bg-white/10'
                      : 'bg-black/20 hover:bg-white/5'
                  }`}
                  onClick={() => onPersonaSelect(persona)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{persona.icon}</div>
                      <div className="flex-1">
                        <h4 className="font-medium text-white">{persona.name}</h4>
                        <p className="text-sm text-gray-400">{persona.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}

        {activeTab === 'upload' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Upload Files</h3>
            <FileUpload onFileUpload={handleFileUpload} />
          </motion.div>
        )}

        {activeTab === 'datasets' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Datasets</h3>
              <Button size="sm" variant="ghost" className="text-gray-400">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-2">
              {datasets.map((dataset) => (
                <Card key={dataset.name} className="bg-black/20">
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-white">{dataset.name}</p>
                        <p className="text-xs text-gray-400">
                          {dataset.rows} rows • {dataset.columns.length} columns
                        </p>
                      </div>
                      <Button size="sm" variant="ghost" className="text-gray-400">
                        View
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {datasets.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <Database className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No datasets available</p>
                  <p className="text-sm">Upload files to get started</p>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {activeTab === 'settings' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Settings</h3>
            <Card className="bg-black/20">
              <CardContent className="p-4 space-y-4">
                <div>
                  <h4 className="font-medium text-white mb-2">API Configuration</h4>
                  <p className="text-sm text-gray-400">
                    Configure your OpenAI and other API keys
                  </p>
                </div>
                <Button variant="outline" className="w-full">
                  Configure APIs
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
} 