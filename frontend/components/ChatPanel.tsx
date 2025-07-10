'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent } from './ui/card'
import { processQuery } from '@/lib/api'
import type { ChatMessage, Persona, ProcessingTrace } from '@/types'

interface ChatPanelProps {
  messages: ChatMessage[]
  onMessagesChange: React.Dispatch<React.SetStateAction<ChatMessage[]>>
  selectedPersona: Persona | null
  isProcessing: boolean
  setIsProcessing: (processing: boolean) => void
  onProcessingTrace: (trace: ProcessingTrace | null) => void
}

export function ChatPanel({
  messages,
  onMessagesChange,
  selectedPersona,
  isProcessing,
  setIsProcessing,
  onProcessingTrace
}: ChatPanelProps) {
  const [inputValue, setInputValue] = useState('')
  const [suggestedQueries, setSuggestedQueries] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !selectedPersona || isProcessing) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    onMessagesChange((prev: ChatMessage[]) => [...prev, userMessage])
    setInputValue('')
    setIsProcessing(true)

    try {
      console.log('[DEBUG] Frontend: Starting query processing')
      console.log('[DEBUG] Frontend: Query:', inputValue)
      console.log('[DEBUG] Frontend: Persona type:', selectedPersona.type)

      // Simulate processing trace
      const trace: ProcessingTrace = {
        query: inputValue,
        steps: [
          { id: '1', name: 'Query Analysis', status: 'processing' },
          { id: '2', name: 'Document Retrieval', status: 'pending' },
          { id: '3', name: 'Agent Processing', status: 'pending' },
          { id: '4', name: 'Response Generation', status: 'pending' }
        ],
        totalDuration: 0,
        finalResult: null
      }
      onProcessingTrace(trace)

      // Simulate step progression
      setTimeout(() => {
        trace.steps[0].status = 'completed'
        trace.steps[0].duration = 500
        trace.steps[1].status = 'processing'
        onProcessingTrace({ ...trace })
      }, 500)

      setTimeout(() => {
        trace.steps[1].status = 'completed'
        trace.steps[1].duration = 800
        trace.steps[2].status = 'processing'
        onProcessingTrace({ ...trace })
      }, 1300)

      setTimeout(() => {
        trace.steps[2].status = 'completed'
        trace.steps[2].duration = 1200
        trace.steps[3].status = 'processing'
        onProcessingTrace({ ...trace })
      }, 2500)

      console.log('[DEBUG] Frontend: Calling processQuery API')
      const response = await processQuery({
        query: inputValue,
        persona_type: selectedPersona.type
      })
      console.log('[DEBUG] Frontend: Received API response:', response)
      console.log('[DEBUG] Frontend: Response success:', response.success)
      console.log('[DEBUG] Frontend: Response content length:', response.response?.length)
      console.log('[DEBUG] Frontend: Response error:', response.error)

      setTimeout(() => {
        trace.steps[3].status = 'completed'
        trace.steps[3].duration = 1000
        trace.totalDuration = 3500
        trace.finalResult = response
        onProcessingTrace({ ...trace })

        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: response.response,
          timestamp: new Date(),
          metadata: {
            persona: selectedPersona.name,
            suggestedQueries: response.suggested_queries,
            processingTime: response.processing_time
          }
        }

        console.log('[DEBUG] Frontend: Creating assistant message:', assistantMessage)
        onMessagesChange((prev: ChatMessage[]) => [...prev, assistantMessage])
        setSuggestedQueries(response.suggested_queries || [])
        setIsProcessing(false)
        console.log('[DEBUG] Frontend: Query processing completed successfully')
      }, 3500)

    } catch (error: any) {
      console.error('[DEBUG] Frontend: Error processing query:', error)
      console.error('[DEBUG] Frontend: Error details:', {
        message: error?.message,
        stack: error?.stack,
        response: error?.response?.data
      })
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your query. Please try again.',
        timestamp: new Date()
      }
      onMessagesChange((prev: ChatMessage[]) => [...prev, errorMessage])
      setIsProcessing(false)
      onProcessingTrace(null)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestedQuery = (query: string) => {
    setInputValue(query)
  }

  return (
    <div className="h-full flex flex-col">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-blue-500' 
                    : selectedPersona?.color 
                      ? `bg-gradient-to-r ${selectedPersona.color}`
                      : 'bg-purple-500'
                }`}>
                  {message.type === 'user' ? (
                    <User className="h-4 w-4 text-white" />
                  ) : (
                    <Bot className="h-4 w-4 text-white" />
                  )}
                </div>
                
                <Card className={`${message.type === 'user' ? 'bg-blue-500/20 border-blue-500/30' : 'bg-black/20 border-white/10'}`}>
                  <CardContent className="p-3">
                    <div className="text-sm text-white whitespace-pre-wrap">
                      {message.content}
                    </div>
                    {message.metadata?.suggestedQueries && (
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <p className="text-xs text-gray-400 mb-2">Suggested follow-ups:</p>
                        <div className="flex flex-wrap gap-1">
                          {message.metadata.suggestedQueries.slice(0, 3).map((query: string, index: number) => (
                            <button
                              key={index}
                              onClick={() => handleSuggestedQuery(query)}
                              className="text-xs bg-white/10 hover:bg-white/20 text-white px-2 py-1 rounded transition-colors"
                            >
                              {query}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isProcessing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="flex items-start space-x-3 max-w-[80%]">
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-r ${selectedPersona?.color || 'from-purple-500 to-pink-600'}`}>
                <Bot className="h-4 w-4 text-white" />
              </div>
              <Card className="bg-black/20 border-white/10">
                <CardContent className="p-3">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
                    <span className="text-sm text-gray-300">Processing your query...</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/10">
        <div className="flex space-x-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={selectedPersona ? `Ask ${selectedPersona.name} anything...` : "Select a persona to start chatting..."}
            disabled={!selectedPersona || isProcessing}
            className="flex-1 bg-black/20 border-white/10 text-white placeholder:text-gray-400"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || !selectedPersona || isProcessing}
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
          >
            {isProcessing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Suggested Queries */}
        {suggestedQueries.length > 0 && !isProcessing && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-3 flex flex-wrap gap-2"
          >
            <Sparkles className="h-4 w-4 text-yellow-400 mt-1" />
            {suggestedQueries.slice(0, 3).map((query, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedQuery(query)}
                className="text-xs bg-white/10 hover:bg-white/20 text-white px-3 py-1 rounded-full transition-colors"
              >
                {query}
              </button>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  )
} 