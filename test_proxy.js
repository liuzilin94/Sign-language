// Test script to verify proxy works
const http = require('http');

const options = {
  hostname: 'localhost',
  port: 3000,  // Frontend dev server
  path: '/api/words/1',  // Should be proxied to backend
  method: 'GET'
};

const req = http.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    console.log('Response:', data.substring(0, 500));
  });
});

req.on('error', (e) => {
  console.error('Error:', e.message);
});

req.end();
