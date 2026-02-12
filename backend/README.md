# Sentinel AI - Backend API Server

Node.js backend API server for the Sentinel AI DDoS detection system for 5G networks.

## Overview

The backend provides a RESTful API and WebSocket connections for the React frontend, orchestrating communication between the frontend, ML detection engine, and SDN controller.

## Features

- **RESTful API** - Endpoints for packet capture, blocking, and system status
- **WebSocket** - Real-time updates to the frontend dashboard
- **Socket.IO** - Bi-directional event-based communication
- **Express 5** - Modern Express.js framework
- **Jest Testing** - Unit, integration, and performance tests
- **Winston Logging** - Structured logging

## Project Structure

```
backend/
│
├── src/                          # Source code
│   ├── index.js                  # Main application entry point
│   ├── controllers/              # Route controllers
│   │   ├── detectionController.js
│   │   └── ipDetectionController.js
│   │
│   ├── middleware/               # Custom middleware
│   │   ├── attack-detector.js    # Attack detection logic
│   │   └── performanceMiddleware.js
│   │
│   ├── routes/                   # Express routes
│   │   ├── detectionRoutes.js
│   │   └── ipDetectionRoutes.js
│   │
│   ├── services/                 # Business logic services
│   │   ├── abuseIPDBService.js   # AbuseIPDB integration
│   │   ├── mlService.js          # ML service integration
│   │   └── packetCapture.js      # Packet capture service
│   │
│   ├── tests/                    # Test files
│   │   ├── setup.js              # Test setup
│   │   ├── unit/                 # Unit tests
│   │   ├── integration/          # Integration tests
│   │   └── performance/          # Performance tests
│   │
│   └── utils/                    # Utility functions
│       └── validator.js          # Input validation
│
├── package.json                  # Dependencies and scripts
├── jest.config.js               # Jest configuration
└── .gitignore                   # Git ignore rules
```

## Tech Stack

- **Runtime**: Node.js
- **Framework**: Express 5
- **WebSocket**: Socket.IO
- **HTTP Client**: Axios
- **Validation**: Joi
- **Logging**: Winston
- **Testing**: Jest + Supertest

## Prerequisites

- Node.js (v16 or higher)
- npm (v8 or higher)

## Installation

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Install Dependencies
```bash
npm install
```

## Available Scripts

### Start Server
```bash
npm start
```
Starts the server on port 3000

### Development Mode
```bash
npm run dev
```
Starts the server with nodemon for auto-reload

### Run Tests
```bash
npm test
```
Runs all tests

### Unit Tests
```bash
npm run test:unit
```
Runs unit tests only

### Integration Tests
```bash
npm run test:integration
```
Runs integration tests only

### Performance Tests
```bash
npm run test:performance
```
Runs performance tests only

### Watch Tests
```bash
npm run test:watch
```
Runs tests in watch mode

## API Endpoints

### Health Check
- `GET /api/health` - Check backend health status

### Capture Control
- `POST /api/start-capture` - Start packet capture
- `POST /api/stop-capture` - Stop packet capture

### Packet Stream
- `POST /api/live-packet` - Receive live packet data

### Block Management
- `GET /api/blocked-ips` - Get list of blocked IPs
- `POST /api/emit-blocked-ip` - Block an IP
- `POST /api/unblock` - Unblock an IP

### Model Status
- `GET /api/model-status` - Get ML model status

### AI Explanation
- `POST /api/explain-detection` - Get AI explanation for detection

## WebSocket Events

### Client → Server
- `capture_started` - Capture started notification
- `capture_stopped` - Capture stopped notification

### Server → Client
- `connect` - Client connected
- `new_packet` - New packet received
- `capture-started` - Capture started
- `capture-stopped` - Capture stopped
- `ip_blocked` - IP blocked
- `update_blocked_ips` - Updated blocked IPs list
- `unblocked_ip` - IP unblocked
- `initial_blocked_ips` - Initial blocked IPs on connection
- `detection-result` - Detection result

## Configuration

### Environment Variables

The backend connects to the ML Flask API automatically. Ensure the ML service is running on port 5001:

```
FLASK_URL=http://localhost:5001
```

### Port Configuration

The backend runs on port 3000 by default. To change:

```javascript
const PORT = process.env.PORT || 3000;
```

## Key Components

### Index.js
Main application entry point that:
- Initializes Express server
- Sets up Socket.IO
- Configures middleware
- Registers routes
- Manages WebSocket events

### Controllers
- `detectionController.js` - Handles detection-related requests
- `ipDetectionController.js` - Handles IP detection and blocking

### Services
- `mlService.js` - Communicates with ML detection engine
- `abuseIPDBService.js` - Checks IPs against AbuseIPDB
- `packetCapture.js` - Manages packet capture operations

## Integration with ML Engine

The backend communicates with the ML Flask API (model/) for:
- Packet classification
- Attack detection
- AI explanations
- Model status updates

## Integration with Frontend

The backend provides:
- REST API endpoints for frontend requests
- WebSocket events for real-time updates
- Connection status management

## Testing

The backend includes comprehensive test coverage:

### Unit Tests
- Health check endpoints
- Controller logic
- Utility functions

### Integration Tests
- API endpoint integration
- Service integration
- End-to-end workflows

### Performance Tests
- Response time benchmarks
- Load testing
- Stress testing

## Troubleshooting

### Common Issues

**❌ "Cannot connect to ML service"**
- Ensure Flask server is running on port 5001
- Check network connectivity
- Verify CORS settings

**❌ "WebSocket connection failed"**
- Check if backend is running
- Verify Socket.IO client configuration
- Check firewall settings

**❌ "Port already in use"**
```bash
lsof -i :3000
kill <PID>
```

### Development Tips

1. **Auto-reload**: Use `npm run dev` for development
2. **Logging**: Winston logs are saved to logs/app.log
3. **Debug Mode**: Set `DEBUG=backend:*` for debug logs
4. **Testing**: Run specific tests with pattern matching

## Performance Considerations

- Connection pooling for API requests
- Efficient WebSocket event handling
- Rate limiting on API endpoints
- Response compression
- Request validation

## Security

- CORS configuration for frontend
- Input validation with Joi
- Secure WebSocket connections
- Rate limiting
- Request size limits

## Contributing

When contributing to the backend:
1. Follow existing code patterns
2. Add tests for new features
3. Update documentation
4. Ensure linting passes
5. Test integration with frontend

## License

This project is part of the Sentinel AI research initiative. Refer to the main project LICENSE for usage terms.

