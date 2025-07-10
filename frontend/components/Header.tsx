'use client'

import { motion } from 'framer-motion'
import { Brain, Zap, Settings, Github, PanelLeft, PanelRight } from 'lucide-react'
import { Button } from './ui/button'

interface HeaderProps {
  onToggleLeftPanel?: () => void
  onToggleRightPanel?: () => void
  showLeftPanel?: boolean
  showRightPanel?: boolean
}

export function Header({ 
  onToggleLeftPanel, 
  onToggleRightPanel, 
  showLeftPanel = true, 
  showRightPanel = true 
}: HeaderProps) {
  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-black/30 backdrop-blur-xl border-b border-white/10 px-4 sm:px-6 py-3 sm:py-4"
    >
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex items-center space-x-2 sm:space-x-3"
        >
          <div className="relative">
            <Brain className="h-6 w-6 sm:h-8 sm:w-8 text-blue-400" />
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute inset-0 border-2 border-blue-400/30 rounded-full"
            />
          </div>
          <div className="hidden sm:block">
            <h1 className="text-lg sm:text-xl font-bold gradient-text">
              Dynamic Agentic System
            </h1>
            <p className="text-xs text-gray-400">
              Multi-Agent AI Platform
            </p>
          </div>
          <div className="sm:hidden">
            <h1 className="text-sm font-bold gradient-text">DAS</h1>
          </div>
        </motion.div>

        {/* Status Indicators and Controls */}
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex items-center space-x-2 sm:space-x-4"
        >
          {/* Panel Toggle Buttons - Mobile */}
          <div className="flex items-center space-x-1 sm:hidden">
            {onToggleLeftPanel && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={onToggleLeftPanel}
                className="text-gray-300 hover:text-white p-1"
              >
                <PanelLeft className="h-4 w-4" />
              </Button>
            )}
            {onToggleRightPanel && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={onToggleRightPanel}
                className="text-gray-300 hover:text-white p-1"
              >
                <PanelRight className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* System Status */}
          <div className="hidden sm:flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-gray-300">System Online</span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-1 sm:space-x-2">
            <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white p-1 sm:p-2">
              <Zap className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white p-1 sm:p-2">
              <Settings className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white p-1 sm:p-2">
              <Github className="h-4 w-4" />
            </Button>
          </div>
        </motion.div>
      </div>
    </motion.header>
  )
} 