// static/js/app.js - Enhanced version with AI content preview and better YouTube integration

class SocialMediaApp {
    constructor() {
        this.currentSection = 'upload';
        this.connectedPlatforms = new Set();
        this.scheduledPosts = [];
        this.aiContent = null;
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupUpload();
        this.setupPlatformCards();
        this.setupAccountManagement();
        this.loadInitialData();
    }

    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.showSection(section);
            });
        });
    }

    setupUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const videoInput = document.getElementById('videoInput');
        const uploadForm = document.getElementById('uploadForm');
        const generateContentCheckbox = document.getElementById('generateContent');

        // Drag and drop functionality
        uploadArea.addEventListener('click', () => videoInput.click());
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.handleFileSelection(files);
        });

        videoInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files);
        });

        // Generate content preview when checkbox is checked
        generateContentCheckbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.generateContentPreview();
            } else {
                this.clearContentPreview();
            }
        });

        // Form submission
        uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUpload();
        });

        // Platform selection
        this.setupPlatformSelection();
    }

    setupPlatformSelection() {
        const platformCards = document.querySelectorAll('.platform-card');
        platformCards.forEach(card => {
            card.addEventListener('click', () => {
                const checkbox = card.querySelector('.platform-checkbox');
                const isSelected = checkbox.checked;
                
                checkbox.checked = !isSelected;
                card.classList.toggle('selected', !isSelected);
                
                // Update content preview if AI generation is enabled
                if (document.getElementById('generateContent').checked) {
                    this.generateContentPreview();
                }
            });
        });
    }

    handleFileSelection(files) {
        const uploadContent = document.querySelector('.upload-content');
        
        if (files.length > 0) {
            const file = files[0];
            
            // Validate file
            if (!this.validateVideoFile(file)) {
                this.showToast('Please select a valid video file (MP4, MOV, AVI)', 'error');
                return;
            }

            // Update UI
            uploadContent.innerHTML = `
                <i class="fas fa-video"></i>
                <h3>${file.name}</h3>
                <p>Size: ${this.formatFileSize(file.size)}</p>
                <small>Ready for upload</small>
            `;
            
            // Auto-generate title if empty
            const titleInput = document.getElementById('videoTitle');
            if (!titleInput.value) {
                titleInput.value = file.name.replace(/\.[^/.]+$/, "");
            }
        }
    }

    async generateContentPreview() {
        const title = document.getElementById('videoTitle').value;
        const category = document.getElementById('videoCategory').value;
        const selectedPlatforms = this.getSelectedPlatforms();

        if (!title.trim()) {
            this.showToast('Please enter a video title first', 'warning');
            return;
        }

        if (selectedPlatforms.length === 0) {
            this.showToast('Please select at least one platform', 'warning');
            return;
        }

        this.showLoading('Generating AI content...');

        try {
            const response = await fetch('/api/generate-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    category: category,
                    platforms: selectedPlatforms
                })
            });

            const result = await response.json();

            if (result.success) {
                this.aiContent = result.content;
                this.displayContentPreview(result.content);
                this.showToast('AI content generated successfully!', 'success');
            } else {
                throw new Error(result.error || 'Failed to generate content');
            }
        } catch (error) {
            console.error('Content generation error:', error);
            this.showToast('Failed to generate AI content: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayContentPreview(content) {
        // Remove existing preview
        this.clearContentPreview();

        // Create preview section
        const uploadCard = document.querySelector('.upload-card');
        const previewSection = document.createElement('div');
        previewSection.className = 'ai-content-preview';
        previewSection.innerHTML = `
            <div class="preview-header">
                <h3><i class="fas fa-magic"></i> AI Generated Content Preview</h3>
                <div class="viral-score">
                    <span class="score-label">Viral Score:</span>
                    <span class="score-value">${content.viral_score || 75}/100</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${content.viral_score || 75}%"></div>
                    </div>
                </div>
            </div>

            <div class="preview-content">
                <div class="preview-section">
                    <label>Generated Description:</label>
                    <div class="description-preview">${content.description || 'No description generated'}</div>
                </div>

                <div class="preview-section">
                    <label>Hashtags:</label>
                    <div class="hashtags-preview">
                        ${(content.hashtags || []).map(tag => 
                            `<span class="hashtag-chip">#${tag}</span>`
                        ).join('')}
                    </div>
                </div>

                ${content.platform_specific ? this.renderPlatformSpecific(content.platform_specific) : ''}

                <div class="preview-actions">
                    <button type="button" class="btn btn-secondary" onclick="app.editAIContent()">
                        <i class="fas fa-edit"></i> Edit Content
                    </button>
                    <button type="button" class="btn btn-primary" onclick="app.regenerateContent()">
                        <i class="fas fa-refresh"></i> Regenerate
                    </button>
                </div>
            </div>
        `;

        uploadCard.appendChild(previewSection);
    }

    renderPlatformSpecific(platformSpecific) {
        let html = '<div class="platform-specific-content">';
        
        Object.keys(platformSpecific).forEach(platform => {
            const content = platformSpecific[platform];
            html += `
                <div class="platform-content" data-platform="${platform}">
                    <h4><i class="fab fa-${platform}"></i> ${platform.charAt(0).toUpperCase() + platform.slice(1)}</h4>
                    <div class="platform-details">
                        ${content.title ? `<p><strong>Title:</strong> ${content.title}</p>` : ''}
                        ${content.description ? `<p><strong>Description:</strong> ${content.description}</p>` : ''}
                        ${content.caption ? `<p><strong>Caption:</strong> ${content.caption}</p>` : ''}
                        ${content.hashtags ? `<p><strong>Hashtags:</strong> ${content.hashtags.join(', ')}</p>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    clearContentPreview() {
        const existingPreview = document.querySelector('.ai-content-preview');
        if (existingPreview) {
            existingPreview.remove();
        }
    }

    async editAIContent() {
        // Create modal for editing AI content
        const modal = this.createEditModal();
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    createEditModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Edit AI Generated Content</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Description:</label>
                        <textarea id="editDescription" rows="4">${this.aiContent?.description || ''}</textarea>
                    </div>
                    <div class="form-group">
                        <label>Hashtags (comma separated):</label>
                        <input type="text" id="editHashtags" value="${(this.aiContent?.hashtags || []).join(', ')}">
                    </div>
                    <div class="modal-actions">
                        <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                        <button class="btn btn-primary" onclick="app.saveEditedContent()">Save Changes</button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    saveEditedContent() {
        const description = document.getElementById('editDescription').value;
        const hashtags = document.getElementById('editHashtags').value
            .split(',').map(tag => tag.trim()).filter(tag => tag);

        // Update aiContent
        if (this.aiContent) {
            this.aiContent.description = description;
            this.aiContent.hashtags = hashtags;
        }

        // Refresh preview
        this.displayContentPreview(this.aiContent);
        
        // Close modal
        document.querySelector('.modal').remove();
        
        this.showToast('Content updated successfully!', 'success');
    }

    async regenerateContent() {
        await this.generateContentPreview();
    }

    async handleUpload() {
        const form = document.getElementById('uploadForm');
        const formData = new FormData();
        
        // Get form values
        const title = document.getElementById('videoTitle').value.trim();
        const category = document.getElementById('videoCategory').value;
        const selectedPlatforms = this.getSelectedPlatforms();
        const generateContent = document.getElementById('generateContent').checked;
        const scheduleTime = document.getElementById('scheduleTime').value;
        const videoInput = document.getElementById('videoInput');

        // Validation
        if (!title) {
            this.showToast('Please enter a video title', 'error');
            return;
        }

        if (selectedPlatforms.length === 0) {
            this.showToast('Please select at least one platform', 'error');
            return;
        }

        if (!videoInput.files || videoInput.files.length === 0) {
            this.showToast('Please select a video file', 'error');
            return;
        }

        // Add files
        Array.from(videoInput.files).forEach((file, index) => {
            formData.append(`video_${index}`, file);
        });

        // Add form data
        formData.append('title', title);
        formData.append('category', category);
        formData.append('platforms', JSON.stringify(selectedPlatforms));
        formData.append('generateContent', generateContent);
        
        if (scheduleTime) {
            formData.append('scheduleTime', scheduleTime);
        }

        // Add AI content if available
        if (this.aiContent) {
            formData.append('description', this.aiContent.description || '');
            formData.append('hashtags', JSON.stringify(this.aiContent.hashtags || []));
            formData.append('aiContent', JSON.stringify(this.aiContent));
        }

        this.showLoading('Uploading and processing your video...');

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(result.message, 'success');
                
                // Show results
                this.displayUploadResults(result);
                
                // Reset form
                form.reset();
                this.clearContentPreview();
                this.resetUploadArea();
                
                // Refresh data
                this.loadScheduledPosts();
                this.loadAnalytics();
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast('Upload failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayUploadResults(result) {
        // Create results modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-check-circle"></i> Upload Results</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="result-summary">
                        <h4>${result.data.title}</h4>
                        <p><strong>Status:</strong> ${result.data.status}</p>
                        <p><strong>Platforms:</strong> ${result.data.platforms.join(', ')}</p>
                        ${result.viral_score ? `<p><strong>Viral Score:</strong> ${result.viral_score}/100</p>` : ''}
                    </div>
                    
                    <div class="result-details">
                        <h5>Generated Content:</h5>
                        <p><strong>Description:</strong> ${result.data.description}</p>
                        <div class="hashtags">
                            <strong>Hashtags:</strong>
                            ${result.data.hashtags.map(tag => `<span class="hashtag-chip">#${tag}</span>`).join('')}
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button class="btn btn-primary" onclick="this.closest('.modal').remove()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    getSelectedPlatforms() {
        const checkboxes = document.querySelectorAll('.platform-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    validateVideoFile(file) {
        const allowedTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/quicktime', 'video/x-msvideo'];
        const maxSize = 500 * 1024 * 1024; // 500MB
        
        return allowedTypes.includes(file.type) && file.size <= maxSize;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    resetUploadArea() {
        const uploadContent = document.querySelector('.upload-content');
        uploadContent.innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <h3>Arraste seus vídeos aqui</h3>
            <p>ou <span class="upload-link">clique para selecionar</span></p>
            <small>Formatos suportados: MP4, MOV, AVI (máx. 500MB)</small>
        `;
    }

    setupPlatformCards() {
        const platformCards = document.querySelectorAll('.platform-card');
        platformCards.forEach(card => {
            card.addEventListener('click', () => {
                const checkbox = card.querySelector('.platform-checkbox');
                checkbox.checked = !checkbox.checked;
                card.classList.toggle('selected', checkbox.checked);
            });
        });
    }

    setupAccountManagement() {
        const connectButtons = document.querySelectorAll('.btn-connect');
        connectButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const platform = e.target.dataset.platform;
                this.connectPlatform(platform);
            });
        });
    }

    async connectPlatform(platform) {
        if (platform === 'youtube') {
            try {
                const response = await fetch('/oauth/youtube/start');
                const result = await response.json();
                
                if (result.auth_url) {
                    // Open OAuth window
                    const popup = window.open(result.auth_url, 'youtube_auth', 'width=500,height=600');
                    
                    // Monitor popup
                    const checkClosed = setInterval(() => {
                        if (popup.closed) {
                            clearInterval(checkClosed);
                            // Check connection status
                            this.checkPlatformConnection('youtube');
                        }
                    }, 1000);
                }
            } catch (error) {
                this.showToast('Failed to start YouTube authentication', 'error');
            }
        } else {
            // For other platforms, show connection modal
            this.showConnectionModal(platform);
        }
    }

    showConnectionModal(platform) {
        const modal = document.getElementById('accountModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Connect ${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
        
        // Platform-specific connection forms
        const connectionForms = {
            instagram: `
                <form id="connectForm">
                    <div class="form-group">
                        <label>Access Token:</label>
                        <input type="text" name="access_token" required>
                    </div>
                    <div class="form-group">
                        <label>User ID:</label>
                        <input type="text" name="user_id" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Connect</button>
                </form>
            `,
            tiktok: `
                <form id="connectForm">
                    <div class="form-group">
                        <label>Access Token:</label>
                        <input type="text" name="access_token" required>
                    </div>
                    <div class="form-group">
                        <label>Open ID:</label>
                        <input type="text" name="open_id" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Connect</button>
                </form>
            `,
            kawai: `
                <form id="connectForm">
                    <div class="form-group">
                        <label>API Key:</label>
                        <input type="text" name="api_key" required>
                    </div>
                    <div class="form-group">
                        <label>User ID:</label>
                        <input type="text" name="user_id" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Connect</button>
                </form>
            `
        };
        
        modalBody.innerHTML = connectionForms[platform] || '<p>Connection form not available</p>';
        
        // Handle form submission
        const form = document.getElementById('connectForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handlePlatformConnection(platform, form);
            });
        }
        
        modal.style.display = 'block';
    }

    async handlePlatformConnection(platform, form) {
        const formData = new FormData(form);
        const credentials = Object.fromEntries(formData.entries());
        credentials.platform = platform;

        try {
            const response = await fetch('/api/accounts/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(result.message, 'success');
                document.getElementById('accountModal').style.display = 'none';
                this.updatePlatformStatus(platform, 'connected');
            } else {
                this.showToast(result.message || 'Connection failed', 'error');
            }
        } catch (error) {
            this.showToast('Connection failed: ' + error.message, 'error');
        }
    }

    async checkPlatformConnection(platform) {
        try {
            const response = await fetch('/api/accounts/status');
            const result = await response.json();
            
            if (result.success && result.accounts[platform]) {
                this.updatePlatformStatus(platform, result.accounts[platform].status);
            }
        } catch (error) {
            console.error('Failed to check platform status:', error);
        }
    }

    updatePlatformStatus(platform, status) {
        const accountCard = document.querySelector(`.account-card.${platform}`);
        if (accountCard) {
            const statusElement = accountCard.querySelector('.status');
            const button = accountCard.querySelector('.btn-connect');
            
            if (status === 'connected') {
                statusElement.textContent = 'Conectado';
                statusElement.className = 'status connected';
                button.textContent = 'Desconectar';
                button.className = 'btn btn-disconnect';
                this.connectedPlatforms.add(platform);
            } else {
                statusElement.textContent = 'Desconectado';
                statusElement.className = 'status disconnected';
                button.textContent = 'Conectar Conta';
                button.className = 'btn btn-connect';
                this.connectedPlatforms.delete(platform);
            }
        }
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show target section
        document.getElementById(sectionName).classList.add('active');
        
        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        
        this.currentSection = sectionName;
        
        // Load section-specific data
        switch(sectionName) {
            case 'schedule':
                this.loadScheduledPosts();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'accounts':
                this.loadAccountStatus();
                break;
        }
    }

    async loadScheduledPosts() {
        try {
            const response = await fetch('/api/schedule');
            const result = await response.json();
            
            if (result.success) {
                this.displayScheduledPosts(result.posts);
            }
        } catch (error) {
            console.error('Failed to load scheduled posts:', error);
        }
    }

    displayScheduledPosts(posts) {
        const scheduleList = document.getElementById('scheduleList');
        
        if (posts.length === 0) {
            scheduleList.innerHTML = '<p class="no-data">Nenhum post agendado encontrado</p>';
            return;
        }
        
        scheduleList.innerHTML = posts.map(post => `
            <div class="schedule-item" data-post-id="${post.id}">
                <div class="schedule-info">
                    <h4>${post.title}</h4>
                    <p>Plataformas: ${post.platforms.join(', ')}</p>
                    <p>Data: ${new Date(post.schedule_time).toLocaleString()}</p>
                </div>
                <div class="schedule-actions">
                    <button class="btn btn-sm btn-secondary" onclick="app.editScheduledPost('${post.id}')">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="app.cancelScheduledPost('${post.id}')">
                        <i class="fas fa-trash"></i> Cancelar
                    </button>
                </div>
            </div>
        `).join('');
    }

    async cancelScheduledPost(postId) {
        if (!confirm('Tem certeza que deseja cancelar este post agendado?')) {
            return;
        }

        try {
            const response = await fetch(`/api/schedule/${postId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showToast('Post cancelado com sucesso', 'success');
                this.loadScheduledPosts();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showToast('Erro ao cancelar post: ' + error.message, 'error');
        }
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics?range=30d');
            const result = await response.json();
            
            if (result.success) {
                this.displayAnalytics(result);
            }
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    }

    displayAnalytics(data) {
        const summary = data.summary || {};
        
        // Update summary cards
        document.getElementById('totalViews').textContent = this.formatNumber(summary.views || 0);
        document.getElementById('totalLikes').textContent = this.formatNumber(summary.likes || 0);
        document.getElementById('totalShares').textContent = this.formatNumber(summary.shares || 0);
        document.getElementById('totalPosts').textContent = this.formatNumber(summary.posts || 0);
        
        // Update chart if available
        this.updatePerformanceChart(data.chartData || {});
    }

    updatePerformanceChart(chartData) {
        const canvas = document.getElementById('performanceChart');
        const ctx = canvas.getContext('2d');
        
        // Simple chart implementation (you might want to use Chart.js for more features)
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#3498db';
        ctx.fillRect(10, 10, 100, 50);
        ctx.fillStyle = '#fff';
        ctx.font = '14px Arial';
        ctx.fillText('Performance Chart', 20, 35);
    }

    async loadAccountStatus() {
        try {
            const response = await fetch('/api/accounts/status');
            const result = await response.json();
            
            if (result.success) {
                Object.keys(result.accounts).forEach(platform => {
                    this.updatePlatformStatus(platform, result.accounts[platform].status);
                });
            }
        } catch (error) {
            console.error('Failed to load account status:', error);
        }
    }

    async loadInitialData() {
        await this.loadAccountStatus();
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${this.getToastIcon(type)}"></i>
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingContent = overlay.querySelector('.loading-content p');
        loadingContent.textContent = message;
        overlay.style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SocialMediaApp();
});

// Modal functionality
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-close')) {
        e.target.closest('.modal').style.display = 'none';
    }
    
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});