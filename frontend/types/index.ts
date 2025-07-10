export interface Persona {
  id: string
  name: string
  description: string
  type: 'financial' | 'legal' | 'general'
  icon: string
  color: string
}

export interface Dataset {
  name: string
  file_path: string
  rows: number
  columns: string[]
  file_type?: string // Add this line for PDF/CSV distinction
  file_size?: number
  data_types: Record<string, string>
}

export interface QueryRequest {
  query: string
  persona_type: string
  context?: string
}

export interface QueryResponse {
  success: boolean
  response: string
  suggested_queries: string[]
  documents: Document[]
  math_results: Record<string, any>
  sql_results: Record<string, any>
  error?: string
  processing_time?: string
}

export interface Document {
  id: string
  content: string
  metadata: Record<string, any>
  score?: number
}

export interface UploadResponse {
  success: boolean
  message: string
  file_id?: string
  file_path?: string
  error?: string
}

export interface SystemStatus {
  status: string
  services: Record<string, boolean>
  timestamp: string
}

export interface FileUpload {
  id: string
  name: string
  size: number
  type: string
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  error?: string
}

export interface LLMProvider {
  id: string
  name: string
  apiKey: string
  baseUrl?: string
  isActive: boolean
}

export interface ProcessingStep {
  id: string
  name: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  duration?: number
  result?: any
  error?: string
}

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: Record<string, any>
}

export interface ProcessingTrace {
  query: string
  steps: ProcessingStep[]
  totalDuration: number
  finalResult: any
} 