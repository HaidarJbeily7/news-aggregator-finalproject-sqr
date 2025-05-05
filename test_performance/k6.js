import http from 'k6/http'
import { check, sleep } from 'k6'

export let options = {
  stages: [
    { duration: '1m', target: 2 },  // Ramp up slowly to 2 users
    { duration: '2m', target: 4 },  // Stay at 3 users for 2 minutes
    { duration: '1m', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests should be less than 200ms
    http_req_failed: ['rate<0.01'],   // Less than 1% of requests should fail
  },
  rps: 2,  // Limit requests per second
}

const BASE_URL = 'http://app:8000'

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
