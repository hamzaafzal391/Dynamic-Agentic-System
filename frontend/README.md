# Dynamic Agentic System - Frontend

A modern, aesthetic frontend for the Dynamic Agentic System built with Next.js, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Modern UI/UX**: Beautiful gradient backgrounds, glass morphism effects, and smooth animations
- 🧠 **Multi-Agent Interface**: Support for Financial, Legal, and General AI personas
- 📁 **File Upload**: Drag & drop PDF and CSV file uploads with progress tracking
- 💬 **Real-time Chat**: Interactive chat interface with suggested queries
- 🔍 **Processing Trace**: Visual flow of query processing with step-by-step debugging
- 📊 **System Monitoring**: Real-time system stats and activity tracking
- 🌟 **3D Effects**: Particle field background for enhanced visual appeal
- 📱 **Responsive Design**: Works seamlessly across desktop and mobile devices

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom animations
- **UI Components**: Radix UI primitives with custom styling
- **Animations**: Framer Motion
- **3D Graphics**: Three.js with React Three Fiber
- **Icons**: Lucide React
- **State Management**: React hooks and Zustand
- **HTTP Client**: Axios
- **Real-time**: WebSocket support

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running (see main README)

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment variables:
```bash
cp .env.example .env.local
```

4. Update `.env.local` with your backend URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

5. Start the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main page
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── 3d/               # 3D components
│   ├── Header.tsx        # Application header
│   ├── LeftPanel.tsx     # Persona and file management
│   ├── ChatPanel.tsx     # Chat interface
│   ├── RightPanel.tsx    # Metadata and trace
│   └── FileUpload.tsx    # File upload component
├── lib/                  # Utility functions
│   ├── api.ts           # API client
│   └── utils.ts         # Helper functions
├── types/               # TypeScript type definitions
└── public/              # Static assets
```

## Key Components

### Left Panel
- **Persona Selection**: Choose between Financial, Legal, and General AI assistants
- **File Upload**: Drag & drop interface for PDFs and CSVs
- **Dataset Management**: View and manage uploaded datasets
- **Settings**: API configuration and system settings

### Center Panel (Chat)
- **Message Interface**: Real-time chat with AI personas
- **Suggested Queries**: AI-generated follow-up questions
- **Processing Indicators**: Visual feedback during query processing
- **Response Display**: Formatted responses with metadata

### Right Panel
- **Processing Trace**: Step-by-step visualization of query processing
- **Active Persona**: Information about the currently selected AI assistant
- **System Stats**: Real-time metrics and performance data
- **Recent Activity**: Timeline of system events

## Customization

### Styling
The application uses a custom Tailwind configuration with:
- Gradient backgrounds and text effects
- Glass morphism components
- Custom animations and transitions
- Dark theme with purple/blue accent colors

### Adding New Personas
1. Update the `defaultPersonas` array in `LeftPanel.tsx`
2. Add corresponding backend support
3. Update type definitions in `types/index.ts`

### 3D Effects
The particle field background can be customized in `components/3d/ParticleField.tsx`:
- Particle count and size
- Colors and animation speed
- 3D positioning and rotation

## API Integration

The frontend communicates with the backend through:
- REST API endpoints for queries and file uploads
- WebSocket connection for real-time updates
- Standard HTTP methods for CRUD operations

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Style

- TypeScript strict mode enabled
- ESLint configuration for code quality
- Prettier for code formatting
- Component-based architecture

## Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Other Platforms
1. Build the application: `npm run build`
2. Start the production server: `npm run start`
3. Configure your hosting platform accordingly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Dynamic Agentic System and follows the same license terms. 