import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '1m', target: 2 },  // Ramp up slowly to 2 users
    { duration: '1m', target: 8 },  // Stay at 8 users for 1 minute
    { duration: '30s', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests should be less than 200ms
    http_req_failed: ['rate<0.1'],   // Less than 0.1% of requests should fail
  },
  rps: 2,  // Limit requests per second
}

const BASE_URL = 'https://backend-floral-field-9372.fly.dev'

// Add a random delay between requests
function randomDelay() {
  return Math.random() * 2 + 1; // Random delay between 1-3 seconds
}

export default function () {
  const response = http.get(`${BASE_URL}/`)
  check(response, {
    'search response time < 200ms': (r) => r.timings.duration < 200,
    'search status is 200': (r) => r.status === 200,
  })
  // Add another random delay
  sleep(randomDelay())
}
