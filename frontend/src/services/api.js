const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  async _request(endpoint, options = {}, timeoutMs = 4000) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          ...defaultHeaders,
          ...options.headers
        }
      });

      clearTimeout(timeoutId);

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
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        console.warn(`Request to ${endpoint} timed out after ${timeoutMs}ms`);
        throw new Error(`Request timed out after ${timeoutMs / 1000}s`);
      }
      console.error(`API error on ${endpoint}:`, error);
      throw error;
    }
  }

  async checkHealth() {
    return this._request('/api/health', {}, 3000);
  }

  async sendChatMessage(message, conversationId = null, orders = []) {
    return this._request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        orders: orders || []
      })
    }, 5000);
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
    }, 4000);
  }

  async queryKnowledge(query, topK = 3) {
    return this._request('/api/knowledge/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k: topK
      })
    }, 4000);
  }

  async getProducts(filters = {}) {
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.brand) params.append('brand', filters.brand);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.search) params.append('search', filters.search);

    const queryStr = params.toString() ? `?${params.toString()}` : '';
    return this._request(`/api/products${queryStr}`, {}, 3500);
  }

  async getProductById(productId) {
    return this._request(`/api/products/${productId}`, {}, 3500);
  }
}

export const api = new ApiService();
