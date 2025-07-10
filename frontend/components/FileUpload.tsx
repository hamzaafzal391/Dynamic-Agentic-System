'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'
import { formatFileSize, getFileIcon, isValidFileType } from '@/lib/utils'
import type { FileUpload } from '@/types'

interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>
  acceptedTypes?: string[]
  maxSize?: number
}

export function FileUpload({ onFileUpload, acceptedTypes = ['application/pdf', 'text/csv'], maxSize = 10 * 1024 * 1024 }: FileUploadProps) {
  const [uploads, setUploads] = useState<FileUpload[]>([])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      const upload: FileUpload = {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading',
        progress: 0
      }

      setUploads(prev => [...prev, upload])

      try {
        // Simulate upload progress
        const interval = setInterval(() => {
          setUploads(prev => prev.map(u => 
            u.id === upload.id 
              ? { ...u, progress: Math.min(u.progress + 10, 90) }
              : u
          ))
        }, 100)

        await onFileUpload(file)
        
        clearInterval(interval)
        setUploads(prev => prev.map(u => 
          u.id === upload.id 
            ? { ...u, status: 'completed', progress: 100 }
            : u
        ))
      } catch (error) {
        setUploads(prev => prev.map(u => 
          u.id === upload.id 
            ? { ...u, status: 'error', error: error instanceof Error ? error.message : 'Upload failed' }
            : u
        ))
      }
    }
  }, [onFileUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxSize,
    multiple: true
  })

  const removeUpload = (id: string) => {
    setUploads(prev => prev.filter(u => u.id !== id))
  }

  return (
    <div className="space-y-4">
      <Card className={`transition-all duration-200 ${isDragActive ? 'ring-2 ring-primary scale-105' : ''}`}>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive 
                ? 'border-primary bg-primary/5' 
                : 'border-gray-300 hover:border-primary/50'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium mb-2">
              {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-sm text-gray-500 mb-4">
              or click to select files
            </p>
            <div className="text-xs text-gray-400 space-y-1">
              <p>Accepted: PDF, CSV files</p>
              <p>Max size: {formatFileSize(maxSize)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {uploads.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Uploads</h3>
          {uploads.map((upload) => (
            <div
              key={upload.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg">{getFileIcon(upload.type)}</span>
                <div>
                  <p className="text-sm font-medium">{upload.name}</p>
                  <p className="text-xs text-gray-500">{formatFileSize(upload.size)}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {upload.status === 'uploading' && (
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${upload.progress}%` }}
                    />
                  </div>
                )}
                
                {upload.status === 'completed' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                
                {upload.status === 'error' && (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeUpload(upload.id)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 