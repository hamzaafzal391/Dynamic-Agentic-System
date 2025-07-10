'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LeftPanel } from '@/components/LeftPanel'
import { ChatPanel } from '@/components/ChatPanel'
import { RightPanel } from '@/components/RightPanel'
import { Header } from '@/components/Header'
import type { Persona, Dataset, ChatMessage, ProcessingTrace } from '@/types'

export default function Home() {
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null)
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [processingTrace, setProcessingTrace] = useState<ProcessingTrace | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showLeftPanel, setShowLeftPanel] = useState(true)
  const [showRightPanel, setShowRightPanel] = useState(true)

  // Add welcome message
  useEffect(() => {
    setMessages([
      {
        id: '1',
        type: 'assistant',
        content: 'Welcome to the Dynamic Agentic System! I can help you with financial analysis, legal documents, general queries, and more. What would you like to explore today?',
        timestamp: new Date(),
      }
    ])
  }, [])

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900" />
      
      {/* Main Content */}
      <div className="relative z-10 flex flex-col h-screen">
        {/* Header */}
        <Header 
          onToggleLeftPanel={() => setShowLeftPanel(!showLeftPanel)}
          onToggleRightPanel={() => setShowRightPanel(!showRightPanel)}
          showLeftPanel={showLeftPanel}
          showRightPanel={showRightPanel}
        />
        
        {/* Main Layout */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel - KB Sources and Persona Management */}
          {showLeftPanel && (
            <motion.div
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="w-64 lg:w-80 xl:w-96 bg-black/20 backdrop-blur-xl border-r border-white/10 flex-shrink-0"
            >
              <LeftPanel
                selectedPersona={selectedPersona}
                onPersonaSelect={setSelectedPersona}
                datasets={datasets}
                onDatasetsChange={setDatasets}
              />
            </motion.div>
          )}
          
          {/* Center Panel - Chat + Answer + Suggested Queries */}
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex-1 flex flex-col min-w-0"
          >
            <ChatPanel
              messages={messages}
              onMessagesChange={setMessages}
              selectedPersona={selectedPersona}
              isProcessing={isProcessing}
              setIsProcessing={setIsProcessing}
              onProcessingTrace={setProcessingTrace}
            />
          </motion.div>
          
          {/* Right Panel - Metadata and Source */}
          {showRightPanel && (
            <motion.div
              initial={{ x: 300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 300, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="w-64 lg:w-80 xl:w-96 bg-black/20 backdrop-blur-xl border-l border-white/10 flex-shrink-0"
            >
              <RightPanel
                processingTrace={processingTrace}
                selectedPersona={selectedPersona}
              />
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
} 