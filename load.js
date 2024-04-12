import http from 'k6/http';
import { check, sleep } from 'k6';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

export const options = {
  stages: [
    { duration: '1m', target: 1 },
    { duration: '5m', target: 1 },
    { duration: '5s', target: 1 },
  ],
  thresholds: {
    'http_req_duration': ['p(99)<500'],
  },
};

const NAMESPACE = 'yourNamespace'; // Replace with your actual namespace
const BASE_URL = `https://rmarin.mids255.com`; // Replace with your actual base URL

const texts = [
  "Hello, I have a small wound in my hand that itches, what can I do?",
  "How can I clean it?",
  "What do I need to have in mind before clean it?",
  "Thank you bye bye"
];

function postConversation(conversationId, text) {
  const payload = JSON.stringify({ query: text });
  const response = http.post(`${BASE_URL}/conversations/${conversationId}`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  check(response, {
    'is conversation response 200': r => r.status === 200
  });
}

export default function () {
  // Generate a unique session ID
  const conversationId = uuidv4();

  // Post each text to the conversation endpoint
  texts.forEach(text => {
    postConversation(conversationId, text);
    sleep(1); // Sleep between requests to simulate real user interaction; adjust as necessary
  });
}