class ChatInterface {
  constructor() {
    this.messageContainer = document.getElementById('messageContainer');
    this.messageInput = document.getElementById('messageInput');
    this.sendButton = document.getElementById('sendButton');
    this.attachmentInput = document.getElementById('attachment');
    this.pendingAttachments = new Map();
    this.draftAttachments = new Set();
    
    this.setupEventListeners();
    this.adjustTextareaHeight();
  }

  setupEventListeners() {
    this.sendButton.addEventListener('click', () => this.sendMessage());
    this.messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    this.messageInput.addEventListener('input', () => this.adjustTextareaHeight());
    this.attachmentInput.addEventListener('change', (e) => this.handleAttachments(e));
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async handleAttachments(event) {
    const files = Array.from(event.target.files);
    
    for (const file of files) {
      const attachmentId = Date.now() + Math.random().toString(36).substr(2, 9);
      this.pendingAttachments.set(attachmentId, {
        file,
        progress: 0
      });
      this.draftAttachments.add({
        id: attachmentId,
        file: file
      });
    }

    // Update draft preview
    this.updateDraftPreview();
    
    this.attachmentInput.value = '';
  }

  updateDraftPreview() {
    const previewContainer = document.getElementById('draftPreview');
    if (!previewContainer) return;

    previewContainer.innerHTML = '';
    
    for (const attachment of this.draftAttachments) {
      const file = attachment.file;
      const previewElement = document.createElement('div');
      previewElement.className = 'draft-attachment';
      previewElement.innerHTML = `
        <div class="attachment-info">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
          </svg>
          <div class="file-details">
            <div class="file-name">${file.name}</div>
            <div class="file-size">${this.formatFileSize(file.size)}</div>
          </div>
          <button class="remove-attachment" data-id="${attachment.id}">×</button>
        </div>
      `;

      previewContainer.appendChild(previewElement);
      
      // Add remove button listener
      const removeButton = previewElement.querySelector('.remove-attachment');
      removeButton.addEventListener('click', (e) => {
        const attachmentId = e.target.dataset.id;
        this.draftAttachments.delete(
          Array.from(this.draftAttachments).find(a => a.id === attachmentId)
        );
        this.pendingAttachments.delete(attachmentId);
        this.updateDraftPreview();
      });
    }
  }

  async processAttachments() {
    const processedAttachments = [];
    
    for (const [attachmentId, {file}] of this.pendingAttachments) {
      if (file.type.startsWith('image/')) {
        const dataUrl = await this.readFileAsDataURL(file);
        processedAttachments.push({
          type: 'image',
          file: file,
          dataUrl: dataUrl
        });
      } else {
        processedAttachments.push({
          type: 'file',
          file: file
        });
      }
    }
    
    return processedAttachments;
  }

  readFileAsDataURL(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.readAsDataURL(file);
    });
  }

  createMessageElement(text, attachments) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    
    if (text) {
      const contentDiv = document.createElement('div');
      contentDiv.className = 'message-content';
      contentDiv.innerHTML = text.replace(/\n/g, '<br>');
      messageDiv.appendChild(contentDiv);
    }
    
    if (attachments.length > 0) {
      const imageAttachments = attachments.filter(att => att.type === 'image');
      const fileAttachments = attachments.filter(att => att.type !== 'image');
      
      if (imageAttachments.length > 0) {
        const previewDiv = document.createElement('div');
        previewDiv.className = 'attachment-preview';
        
        imageAttachments.forEach((attachment, index) => {
          const thumbnailWrapper = document.createElement('div');
          thumbnailWrapper.className = 'thumbnail-wrapper';
          thumbnailWrapper.dataset.attachmentId = `img-${index}`;
          
          const img = document.createElement('img');
          img.src = attachment.dataUrl;
          img.alt = attachment.file.name;
          img.addEventListener('click', () => this.showFullscreenPreview(attachment.dataUrl));
          
          thumbnailWrapper.appendChild(img);
          previewDiv.appendChild(thumbnailWrapper);
          
          // Add hover effects
          const infoDiv = document.createElement('div');
          infoDiv.className = 'attachment-info';
          infoDiv.dataset.attachmentId = `img-${index}`;
          infoDiv.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <div class="file-details">
              <div class="file-name">${attachment.file.name}</div>
              <div class="file-size">${this.formatFileSize(attachment.file.size)}</div>
            </div>
          `;
          messageDiv.appendChild(infoDiv);

          // Add hover interactions
          this.setupHoverInteractions(thumbnailWrapper, infoDiv);
        });
        
        messageDiv.appendChild(previewDiv);
      }
      
      // Add non-image attachments
      fileAttachments.forEach(attachment => {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'attachment-info';
        infoDiv.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
          </svg>
          <div class="file-details">
            <div class="file-name">${attachment.file.name}</div>
            <div class="file-size">${this.formatFileSize(attachment.file.size)}</div>
          </div>
        `;
        messageDiv.appendChild(infoDiv);
      });
    }
    
    return messageDiv;
  }

  setupHoverInteractions(thumbnailWrapper, infoDiv) {
    thumbnailWrapper.addEventListener('mouseenter', () => {
      infoDiv.dataset.hover = 'true';
    });
    
    thumbnailWrapper.addEventListener('mouseleave', () => {
      infoDiv.dataset.hover = 'false';
    });
    
    infoDiv.addEventListener('mouseenter', () => {
      thumbnailWrapper.dataset.hover = 'true';
    });
    
    infoDiv.addEventListener('mouseleave', () => {
      thumbnailWrapper.dataset.hover = 'false';
    });
  }

  showFullscreenPreview(imageUrl) {
    let fullscreenPreview = document.querySelector('.fullscreen-preview');
    
    if (!fullscreenPreview) {
      fullscreenPreview = document.createElement('div');
      fullscreenPreview.className = 'fullscreen-preview';
      fullscreenPreview.innerHTML = '<img>';
      document.body.appendChild(fullscreenPreview);
      
      fullscreenPreview.addEventListener('click', () => {
        fullscreenPreview.classList.remove('active');
      });
    }
    
    const img = fullscreenPreview.querySelector('img');
    img.src = imageUrl;
    fullscreenPreview.classList.add('active');
  }

  async sendMessage() {
    const message = this.messageInput.value;
    const hasAttachments = this.pendingAttachments.size > 0;
    
    if (!message && !hasAttachments) return;
    
    const processedAttachments = await this.processAttachments();
    const messageElement = this.createMessageElement(message, processedAttachments);
    
    this.messageContainer.appendChild(messageElement);
    this.scrollToBottom();
    
    // Clear input and attachments
    this.messageInput.value = '';
    this.pendingAttachments.clear();
    this.draftAttachments.clear();
    this.adjustTextareaHeight();
    this.updateDraftPreview();
    
    // Simulate AI response
    setTimeout(() => {
      const responseDiv = document.createElement('div');
      responseDiv.className = 'message assistant';
      responseDiv.innerHTML = '<div class="message-content">I received your message and attachments. How can I help you further?</div>';
      this.messageContainer.appendChild(responseDiv);
      this.scrollToBottom();
    }, 1000);
  }

  adjustTextareaHeight() {
    this.messageInput.style.height = 'auto';
    this.messageInput.style.height = (this.messageInput.scrollHeight) + 'px';
  }

  scrollToBottom() {
    this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
  }
}

// Initialize the chat interface
const chat = new ChatInterface();