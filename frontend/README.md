# Sentinel AI - Frontend Dashboard

A modern React-based web dashboard for real-time monitoring and management of the Sentinel AI DDoS detection system for 5G networks.

## Overview

The frontend dashboard provides an intuitive interface for monitoring network traffic, detecting DDoS attacks, managing 5G network slices, and visualizing security metrics in real-time.

## Features

- **Real-time Monitoring**: Live network traffic visualization with interactive charts
- **DDoS Detection Alerts**: Instant notifications for detected threats
- **5G Network Slice Management**: Control and monitor eMBB, URLLC, and mMTC slices
- **Interactive Dashboard**: Comprehensive metrics and visualizations
- **Responsive Design**: Optimized for desktop and tablet devices
- **Dark/Light Theme**: Built-in theme support for better user experience

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Package Manager**: npm

## Project Structure

```
frontend/
│
├── src/
│   ├── components/              # React Components
│   │   ├── AIExplanation.tsx    # AI explanation panel
│   │   ├── BlockedIPs.tsx       # Blocked IPs display
│   │   ├── ConnectionStatus.tsx # Connection status indicator
│   │   ├── ControlButton.tsx    # Capture control button
│   │   ├── Footer.tsx           # Footer component
│   │   ├── Header.tsx           # Header with title
│   │   ├── LivePacketTable.tsx  # Live packets table
│   │   ├── StatsPanel.tsx       # Statistics panel
│   │   └── TrafficChart.tsx     # Traffic visualization chart
│   │
│   ├── services/
│   │   └── api.ts               # API communication layer
│   │
│   ├── types/
│   │   └── index.ts             # TypeScript type definitions
│   │
│   ├── App.tsx                  # Main application component
│   ├── main.tsx                 # Application entry point
│   ├── index.css                # Global styles
│   └── vite-env.d.ts            # Vite environment types
│
├── public/
│   └── vite.svg                 # Application icon
│
├── package.json                 # Dependencies and scripts
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
├── tsconfig.app.json           # App-specific TypeScript config
├── tsconfig.node.json          # Node-specific TypeScript config
├── eslint.config.js            # ESLint configuration
└── postcss.config.js           # PostCSS configuration
```

## Prerequisites

- Node.js (v16 or higher)
- npm (v8 or higher)

## Installation

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

## Available Scripts

### Development Server
```bash
npm run dev
```
Starts the development server on `http://localhost:5173`

### Build for Production
```bash
npm run build
```
Creates an optimized production build in the `dist` folder

### Preview Production Build
```bash
npm run preview
```
Previews the production build locally

### Linting
```bash
npm run lint
```
Runs ESLint to check code quality

## Configuration

### Environment Variables

The frontend connects to the backend API automatically. Ensure the backend is running on port 3000, or configure the API base URL in `src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:3000/api';
```

### Styling Configuration

Tailwind CSS is configured in `tailwind.config.js` with custom colors and themes optimized for the security dashboard.

## Key Components

### App.tsx
Main application component that handles:
- State management for network data
- Real-time data fetching
- UI rendering and component composition
- Theme management

### API Service (`src/services/api.ts`)
Handles all backend communication:
- DDoS detection requests
- Network slice management
- Real-time monitoring data
- Error handling and retry logic

## Dashboard Features

### Real-time Monitoring
- Live traffic graphs showing network activity
- Real-time DDoS detection alerts
- Connection status indicators
- Automatic data refresh

### Network Slice Management
- eMBB (Enhanced Mobile Broadband) slice controls
- URLLC (Ultra-Reliable Low Latency Communications) monitoring
- mMTC (Massive Machine Type Communications) statistics
- Slice performance metrics

### Detection Interface
- Manual detection input for specific IP addresses
- Automatic monitoring toggle
- Historical detection results
- Threat severity indicators

## Development

### Adding New Components
1. Create component files in appropriate directories
2. Use TypeScript for type safety
3. Follow React best practices with hooks
4. Style with Tailwind CSS classes
5. Test component functionality

### Styling Guidelines
- Use Tailwind CSS utility classes
- Maintain consistent color scheme
- Ensure responsive design
- Follow accessibility best practices

### API Integration
- Use the `api.ts` service for all backend calls
- Handle loading states appropriately
- Implement error handling
- Use TypeScript interfaces for data types

## Performance Optimization

- Code splitting with React.lazy()
- Memoization with React.memo() and useMemo()
- Efficient re-rendering with proper dependency arrays
- Optimized bundle size with Vite

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Common Issues

**❌ "Cannot connect to backend"**
- Ensure backend server is running on port 3000
- Check network connectivity
- Verify CORS settings on backend

**❌ "Build errors"**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**❌ "TypeScript errors"**
- Check type definitions in `src/vite-env.d.ts`
- Ensure proper import paths
- Verify TypeScript configuration

### Development Tips

1. **Hot Reload**: Changes are reflected instantly during development
2. **ESLint**: Run `npm run lint` to check code quality
3. **Type Checking**: TypeScript provides compile-time error checking
4. **Browser DevTools**: Use React DevTools for component debugging

## Contributing

When contributing to the frontend:
1. Follow the existing code style and patterns
2. Add TypeScript types for new features
3. Test responsive design on different screen sizes
4. Update documentation for new features
5. Ensure backward compatibility

## License

This project is part of the Sentinel AI research initiative. Refer to the main project LICENSE for usage terms.
