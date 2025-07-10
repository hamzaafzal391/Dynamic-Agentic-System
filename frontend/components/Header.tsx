'use client'

import { motion } from 'framer-motion'
import { Brain, Zap, Settings, Github } from 'lucide-react'
import { Button } from './ui/button'

export function Header() {
  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-black/30 backdrop-blur-xl border-b border-white/10 px-6 py-4"
    >
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex items-center space-x-3"
        >
          <div className="relative">
            <Brain className="h-8 w-8 text-blue-400" />
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute inset-0 border-2 border-blue-400/30 rounded-full"
            />
          </div>
          <div>
            <h1 className="text-xl font-bold gradient-text">
              Dynamic Agentic System
            </h1>
            <p className="text-xs text-gray-400">
              Multi-Agent AI Platform
            </p>
          </div>
        </motion.div>

        {/* Status Indicators */}
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex items-center space-x-4"
        >
          {/* System Status */}
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-gray-300">System Online</span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
              <Zap className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
              <Settings className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
              <Github className="h-4 w-4" />
            </Button>
          </div>
        </motion.div>
      </div>
    </motion.header>
  )
} 