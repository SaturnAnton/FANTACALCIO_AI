// Simple test script to verify API connections
const axios = require('axios');

const API_URL = 'http://localhost:8000';
const TEST_USER = {
  email: 'test@example.com',
  password: 'password123'
};

// Test authentication endpoints
async function testAuth() {
  console.log('\n--- Testing Authentication Endpoints ---');
  try {
    // Test registration
    console.log('Testing registration...');
    const registerResponse = await axios.post(`${API_URL}/auth/register`, {
      name: 'Test User',
      email: TEST_USER.email,
      password: TEST_USER.password
    });
    console.log('✅ Registration successful:', registerResponse.status);
  } catch (error) {
    console.log('⚠️ Registration failed (may already exist):', error.response?.status || error.message);
  }

  try {
    // Test login
    console.log('Testing login...');
    const loginResponse = await axios.post(`${API_URL}/auth/login`, {
      email: TEST_USER.email,
      password: TEST_USER.password
    });
    console.log('✅ Login successful:', loginResponse.status);
    return loginResponse.data.access_token;
  } catch (error) {
    console.log('❌ Login failed:', error.response?.status || error.message);
    return null;
  }
}

// Test prediction endpoints
async function testPredictions(token) {
  console.log('\n--- Testing Prediction Endpoints ---');
  if (!token) {
    console.log('❌ Cannot test predictions: No authentication token');
    return;
  }

  const headers = { Authorization: `Bearer ${token}` };
  const userId = 1; // Assuming test user has ID 1

  try {
    // Test get predictions
    console.log('Testing get predictions...');
    const predictionsResponse = await axios.get(
      `${API_URL}/predictions/matchday/1?user_id=${userId}`,
      { headers }
    );
    console.log('✅ Get predictions successful:', predictionsResponse.status);
    console.log(`   Retrieved ${predictionsResponse.data.length} predictions`);
  } catch (error) {
    console.log('❌ Get predictions failed:', error.response?.status || error.message);
  }

  try {
    // Test formation optimization
    console.log('Testing formation optimization...');
    const optimizeResponse = await axios.post(
      `${API_URL}/predictions/optimize/formation/${userId}`,
      { formation: '4-3-3' },
      { headers }
    );
    console.log('✅ Formation optimization successful:', optimizeResponse.status);
  } catch (error) {
    console.log('❌ Formation optimization failed:', error.response?.status || error.message);
  }

  try {
    // Test transfer recommendations
    console.log('Testing transfer recommendations...');
    const transfersResponse = await axios.get(
      `${API_URL}/predictions/recommend/transfers/${userId}?budget=20&max_transfers=2`,
      { headers }
    );
    console.log('✅ Transfer recommendations successful:', transfersResponse.status);
  } catch (error) {
    console.log('❌ Transfer recommendations failed:', error.response?.status || error.message);
  }
}

// Test squad endpoints
async function testSquad(token) {
  console.log('\n--- Testing Squad Endpoints ---');
  if (!token) {
    console.log('❌ Cannot test squad: No authentication token');
    return;
  }

  const headers = { Authorization: `Bearer ${token}` };
  const userId = 1; // Assuming test user has ID 1

  try {
    // Test get squad
    console.log('Testing get squad...');
    const squadResponse = await axios.get(
      `${API_URL}/squad/${userId}`,
      { headers }
    );
    console.log('✅ Get squad successful:', squadResponse.status);
    console.log(`   Retrieved ${squadResponse.data.length} players`);
  } catch (error) {
    console.log('❌ Get squad failed:', error.response?.status || error.message);
  }
}

// Run all tests
async function runTests() {
  console.log('=== Starting API Connection Tests ===');
  console.log(`Testing against API at: ${API_URL}`);
  
  try {
    // Test authentication
    const token = await testAuth();
    
    // Test predictions
    await testPredictions(token);
    
    // Test squad
    await testSquad(token);
    
    console.log('\n=== API Connection Tests Completed ===');
  } catch (error) {
    console.error('\n❌ Test failed with error:', error.message);
  }
}

// Run the tests
runTests();