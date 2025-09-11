# Technology Risk Register - Frontend

React + TypeScript frontend for the Technology Risk Register application.

## Features

- **Modern React Stack**: Vite + TypeScript + Material-UI
- **API Integration**: React Query for efficient data fetching and state management
- **Responsive Design**: Mobile-friendly interface with Material-UI components
- **Dashboard**: Real-time risk metrics and visualizations
- **Risk Management**: Complete CRUD operations for technology risks
- **Filtering & Search**: Advanced filtering and search capabilities

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Quick Start

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API endpoint
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:3000

4. **Build for production**
   ```bash
   npm run build
   ```

### Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with ESLint
- `npm run type-check` - Run TypeScript type checking

## Architecture

### Project Structure

```
src/
├── components/          # Reusable UI components
├── hooks/              # Custom React hooks for API calls
├── layouts/            # Layout components
├── pages/              # Page components (Dashboard, RiskList, etc.)
├── services/           # API service layer
├── types/              # TypeScript type definitions
└── theme.ts            # Material-UI theme configuration
```

### Key Technologies

- **React 19** with TypeScript
- **Material-UI v6** for UI components
- **React Query (TanStack Query)** for server state management
- **React Router** for client-side routing
- **Vite** for build tooling

### API Integration

The frontend communicates with the FastAPI backend via:
- RESTful API endpoints
- Optimistic updates with React Query
- Error handling and loading states
- Automatic retries and caching

## Deployment

### Local Development with Backend

1. Start the backend server:
   ```bash
   cd ../
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start the frontend:
   ```bash
   npm run dev
   ```

### Production Build

The frontend builds to static files that can be served by any web server:

```bash
npm run build
# Files will be in ./dist/
```

### GCP Deployment

For serverless deployment alongside the backend:
- Frontend builds to static files
- Can be served by the FastAPI backend or separate CDN
- Configure CORS settings for production domain

## API Proxy

During development, the Vite dev server proxies API requests to `http://localhost:8000` to avoid CORS issues. This is configured in `vite.config.ts`.

## Contributing

1. Follow the existing code style
2. Use TypeScript strictly
3. Write components with proper prop types
4. Test API integration thoroughly
5. Ensure responsive design works on mobile
