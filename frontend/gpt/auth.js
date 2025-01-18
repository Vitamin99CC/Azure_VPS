class AuthManager {
  constructor() {
    this.loginForm = document.getElementById('loginForm');
    this.username = document.getElementById('username');
    this.password = document.getElementById('password');
    this.errorMessage = document.getElementById('errorMessage');
    this.loginContainer = document.getElementById('loginContainer');
    this.chatInterface = document.getElementById('chatInterface');
    
    this.setupEventListeners();
    this.checkAuthentication();
  }

  setupEventListeners() {
    this.loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleLogin();
    });
  }

  checkAuthentication() {
    const token = localStorage.getItem('chatAuthToken');
    if (token) {
      this.showChat();
    }
  }

  async handleLogin() {
    const username = this.username.value.trim();
    const password = this.password.value;

    if (!username || !password) {
      this.showError('Please enter both username and password');
      return;
    }

    try {
      // Simulate API call with artificial delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simple authentication simulation
      // In a real app, this would be a backend API call
      if (username === 'demo' && password === 'password') {
        const token = 'simulated-jwt-token-' + Date.now();
        localStorage.setItem('chatAuthToken', token);
        this.showChat();
      } else {
        this.showError('Invalid username or password');
      }
    } catch (error) {
      this.showError('Login failed. Please try again.');
    }
  }

  showError(message) {
    this.errorMessage.textContent = message;
    setTimeout(() => {
      this.errorMessage.textContent = '';
    }, 3000);
  }

  showChat() {
    this.loginContainer.classList.add('hidden');
    this.chatInterface.classList.remove('hidden');
    // Initialize chat after successful login
    if (!window.chat) {
      window.chat = new ChatInterface();
    }
  }
}

// Initialize authentication
const auth = new AuthManager();