const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  async _request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers
        }
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: `HTTP error ${response.status}: ${response.statusText}` };
        }
        throw new Error(errorData.message || `Request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API error on ${endpoint}:`, error);
      throw error;
    }
  }

  async checkHealth() {
    return this._request('/api/health');
  }

  async sendChatMessage(message, conversationId = null, orders = []) {
    return this._request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        orders: orders || []
      })
    });
  }

  async getRecommendations(query, category = null, maxPrice = null, topK = 4) {
    return this._request('/api/recommendations', {
      method: 'POST',
      body: JSON.stringify({
        query,
        category,
        max_price: maxPrice,
        top_k: topK
      })
    });
  }

  async queryKnowledge(query, topK = 3) {
    return this._request('/api/knowledge/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k: topK
      })
    });
  }

  async getProducts(filters = {}) {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.brand) params.append('brand', filters.brand);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.search) params.append('search', filters.search);

    const queryStr = params.toString() ? `?${params.toString()}` : '';
    return this._request(`/api/products${queryStr}`);
  }

  async getProductById(productId) {
    return this._request(`/api/products/${productId}`);
  }
}

export const api = new ApiService();
