const BASE_URL = '/api/v1';

export async function apiClient(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok || data.success === false) {
      const errCode = data?.error?.code || `HTTP_${response.status}`;
      const errMsg = data?.error?.message || 'An error occurred while contacting CSE SmartRoom API.';
      const err = new Error(errMsg);
      err.code = errCode;
      err.status = response.status;
      throw err;
    }

    return data.data;
  } catch (error) {
    if (!error.code) {
      error.code = 'NETWORK_ERROR';
      error.message = 'Unable to connect to CSE SmartRoom backend server.';
    }
    throw error;
  }
}
