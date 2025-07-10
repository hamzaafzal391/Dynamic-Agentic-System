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
import { uploadFile, getDatasets } from '@/lib/api'
import type { Persona, Dataset } from '@/types'
import { Dialog } from '@headlessui/react'

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
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(false)
  const [viewDataset, setViewDataset] = useState<Dataset | null>(null)
  const [showModal, setShowModal] = useState(false)

  // Load datasets on component mount and when datasets change
  const loadDatasets = async () => {
    try {
      setIsLoadingDatasets(true)
      const response = await getDatasets()
      if (response.success) {
        onDatasetsChange(response.datasets)
      }
    } catch (error) {
      console.error('Failed to load datasets:', error)
    } finally {
      setIsLoadingDatasets(false)
    }
  }

  useEffect(() => {
    loadDatasets()
  }, [])

  const handleFileUpload = async (file: File) => {
    try {
      const response = await uploadFile(file)
      if (response.success) {
        console.log('File uploaded successfully:', response)
        // Refresh datasets after successful upload
        await loadDatasets()
      } else {
        throw new Error(response.error || 'Upload failed')
      }
    } catch (error) {
      console.error('Upload failed:', error)
      throw error // Re-throw to let FileUpload component handle the error
    }
  }

  const handleViewDataset = (dataset: Dataset) => {
    setViewDataset(dataset)
    setShowModal(true)
  }

  return (
    <div className="h-full flex flex-col p-2 sm:p-4 space-y-4 min-w-0">
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
            className={`flex-1 flex items-center justify-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-white/20 text-white shadow-lg'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            }`}
          >
            <tab.icon className="h-3 w-3 sm:h-4 sm:w-4" />
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar min-w-0">
        {activeTab === 'personas' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3 sm:space-y-4"
          >
            <h3 className="text-base sm:text-lg font-semibold text-white mb-3 sm:mb-4">Select Persona</h3>
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
                  <CardContent className="p-3 sm:p-4">
                    <div className="flex items-center space-x-2 sm:space-x-3">
                      <div className="text-xl sm:text-2xl">{persona.icon}</div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-white text-sm sm:text-base truncate">{persona.name}</h4>
                        <p className="text-xs sm:text-sm text-gray-400 line-clamp-2">{persona.description}</p>
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
            className="space-y-3 sm:space-y-4"
          >
            <h3 className="text-base sm:text-lg font-semibold text-white mb-3 sm:mb-4">Upload Files</h3>
            <FileUpload onFileUpload={handleFileUpload} />
          </motion.div>
        )}

        {activeTab === 'datasets' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3 sm:space-y-4"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-base sm:text-lg font-semibold text-white">Datasets</h3>
              <Button 
                size="sm" 
                variant="ghost" 
                className="text-gray-400"
                onClick={loadDatasets}
                disabled={isLoadingDatasets}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-2">
              {isLoadingDatasets && (
                <div className="text-center py-4 text-gray-400">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mx-auto"></div>
                  <p className="text-sm mt-2">Loading datasets...</p>
                </div>
              )}
              
              {!isLoadingDatasets && datasets.map((dataset) => (
                <Card key={dataset.name} className="bg-black/20">
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white text-sm truncate">{dataset.name}</p>
                        <p className="text-xs text-gray-400">
                          {dataset.rows || 0} rows • {dataset.columns?.length || 0} columns
                        </p>
                      </div>
                      <Button size="sm" variant="ghost" className="text-gray-400 ml-2" onClick={() => handleViewDataset(dataset)}>
                        View
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {!isLoadingDatasets && datasets.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <Database className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No datasets available</p>
                  <p className="text-xs">Upload files to get started</p>
                </div>
              )}
            </div>
            {/* Dataset Modal */}
            <Dialog open={showModal} onClose={() => setShowModal(false)} className="fixed z-50 inset-0 overflow-y-auto">
              <div className="flex items-center justify-center min-h-screen px-4">
                <div className="fixed inset-0 bg-black/60" aria-hidden="true" />
                <Dialog.Panel className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-auto p-6 z-10">
                  <Dialog.Title className="text-lg font-bold mb-2">Dataset Details</Dialog.Title>
                  {viewDataset && (
                    <div className="space-y-2">
                      <div><span className="font-semibold">Name:</span> {viewDataset.name}</div>
                      <div><span className="font-semibold">Type:</span> {viewDataset.file_type || 'csv'}</div>
                      <div><span className="font-semibold">Rows:</span> {viewDataset.rows || 0}</div>
                      <div><span className="font-semibold">Columns:</span> {viewDataset.columns?.join(', ') || 'No columns'}</div>
                      {viewDataset.file_type === 'pdf' && (
                        <div className="text-xs text-gray-500">PDF preview not implemented. (You can add a preview here.)</div>
                      )}
                      {viewDataset.file_type !== 'pdf' && (
                        <div className="text-xs text-gray-500">CSV preview not implemented. (You can add a preview here.)</div>
                      )}
                    </div>
                  )}
                  <div className="mt-4 flex justify-end">
                    <Button onClick={() => setShowModal(false)} variant="outline">Close</Button>
                  </div>
                </Dialog.Panel>
              </div>
            </Dialog>
          </motion.div>
        )}

        {activeTab === 'settings' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3 sm:space-y-4"
          >
            <h3 className="text-base sm:text-lg font-semibold text-white mb-3 sm:mb-4">Settings</h3>
            <Card className="bg-black/20">
              <CardContent className="p-4">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-white mb-2">API Configuration</h4>
                    <p className="text-sm text-gray-400">
                      Backend URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-white mb-2">System Status</h4>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-400">Connected</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
} 