// backend/middleware/performanceMiddleware.js
const { performance } = require('perf_hooks');

/**
 * Performance monitoring middleware
 * Measures response time and logs slow/fast requests
 */
const performanceMiddleware = (req, res, next) => {
  const start = performance.now();

  // Override res.json to measure response time
  const originalJson = res.json.bind(res);
  res.json = (data) => {
    const duration = performance.now() - start;

    // Add performance headers
    res.set({
      'X-Response-Time': `${duration.toFixed(2)}ms`,
      'X-Performance-Target': 'sub-second',
      'X-Timestamp': new Date().toISOString()
    });

    // Log based on duration
    if (duration > 500) {
      console.warn(`⚠️  Slow request: ${req.method} ${req.path} - ${duration.toFixed(0)}ms`);
    } else if (duration < 200) {
      console.log(`⚡ Fast request: ${req.method} ${req.path} - ${duration.toFixed(0)}ms`);
    } else {
      console.log(`ℹ️  Request: ${req.method} ${req.path} - ${duration.toFixed(0)}ms`);
    }

    // Return response
    return originalJson(data);
  };

  next();
};

// ✅ Export the function directly
module.exports = performanceMiddleware;
