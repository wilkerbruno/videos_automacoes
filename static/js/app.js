// App State
const appState = {
    currentSection: 'upload',
    connectedAccounts: new Set(),
    uploadedFiles: [],
    scheduledPosts: [],
    analytics: {
        totalViews: 0,
        totalLikes: 0,
        totalShares: 0,
        totalPosts: 0
    }
};

// DOM Elements
const DOM = {
    navButtons: document.querySelectorAll('.nav-btn'),
    sections: document.querySelectorAll('.section'),
    uploadForm: document.getElementById('uploadForm'),
    uploadArea: document.getElementById('uploadArea'),
    videoInput: document.getElementById('videoInput'),
    videoTitle: document.getElementById('videoTitle'),
    videoCategory: document.getElementById('videoCategory'),
    platformCards: document.querySelectorAll('.platform-card'),
    platformCheckboxes: document.querySelectorAll('.platform-checkbox'),
    generateContent: document.getElementById('generateContent'),
    scheduleTime: document.getElementById('scheduleTime'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer'),
    accountModal: document.getElementById('accountModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalBody: document.getElementById('modalBody'),
    connectButtons: document.querySelectorAll('.btn-connect'),
    scheduleList: document.getElementById('scheduleList'),
    platformFilter: document.getElementById('platformFilter'),
    dateFilter: document.getElementById('dateFilter'),
    analyticsElements: {
        totalViews: document.getElementById('totalViews'),
        totalLikes: document.getElementById('totalLikes'),
        totalShares: document.getElementById('totalShares'),
        totalPosts: document.getElementById('totalPosts')
    }
};

// Utility Functions
const Utils = {
    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format date
    formatDate(dateString) {
        return new Date(dateString).toLocaleString('pt-BR');
    },

    // Generate unique ID
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Toast Notification System
const Toast = {
    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        DOM.toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'error');
    },

    info(message) {
        this.show(message, 'info');
    }
};

// API Service
const ApiService = {
    baseUrl: '/api',

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // Upload video
    async uploadVideo(formData) {
        const response = await fetch(`${this.baseUrl}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        return await response.json();
    },

    // Generate content with AI
    async generateContent(title, category, platforms) {
        return await this.request('/generate-content', {
            method: 'POST',
            body: JSON.stringify({ title, category, platforms })
        });
    },

    // Schedule post
    async schedulePost(postData) {
        return await this.request('/schedule', {
            method: 'POST',
            body: JSON.stringify(postData)
        });
    },

    // Get scheduled posts
    async getScheduledPosts(filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.request(`/schedule?${params}`);
    },

    // Connect social media account
    async connectAccount(platform, credentials) {
        return await this.request('/accounts/connect', {
            method: 'POST',
            body: JSON.stringify({ platform, ...credentials })
        });
    },

    // Get account status
    async getAccountStatus() {
        return await this.request('/accounts/status');
    },

    // Get analytics
    async getAnalytics(dateRange) {
        return await this.request(`/analytics?range=${dateRange}`);
    },

    // Post to platforms
    async postToPlatforms(postData) {
        return await this.request('/post', {
            method: 'POST',
            body: JSON.stringify(postData)
        });
    }
};

// Navigation Handler
class Navigation {
    init() {
        DOM.navButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const section = e.target.dataset.section;
                this.switchSection(section);
            });
        });
    }

    switchSection(sectionName) {
        // Update nav buttons
        DOM.navButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update sections
        DOM.sections.forEach(section => section.classList.remove('active'));
        document.getElementById(sectionName).classList.add('active');

        appState.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'accounts':
                await AccountManager.loadAccountStatus();
                break;
            case 'schedule':
                await ScheduleManager.loadScheduledPosts();
                break;
            case 'analytics':
                await AnalyticsManager.loadAnalytics();
                break;
        }
    }
}

// Upload Manager
class UploadManager {
    init() {
        this.setupDragAndDrop();
        this.setupFileInput();
        this.setupForm();
        this.setupPlatformSelection();
    }

    setupDragAndDrop() {
        DOM.uploadArea.addEventListener('click', () => {
            DOM.videoInput.click();
        });

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            DOM.uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            DOM.uploadArea.addEventListener(eventName, () => {
                DOM.uploadArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            DOM.uploadArea.addEventListener(eventName, () => {
                DOM.uploadArea.classList.remove('dragover');
            }, false);
        });

        DOM.uploadArea.addEventListener('drop', this.handleDrop.bind(this), false);
    }

    setupFileInput() {
        DOM.videoInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }

    setupForm() {
        DOM.uploadForm.addEventListener('submit', this.handleSubmit.bind(this));
    }

    setupPlatformSelection() {
        DOM.platformCards.forEach(card => {
            card.addEventListener('click', () => {
                const checkbox = card.querySelector('.platform-checkbox');
                checkbox.checked = !checkbox.checked;
                card.classList.toggle('selected', checkbox.checked);
            });
        });

        DOM.platformCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const card = e.target.closest('.platform-card');
                card.classList.toggle('selected', e.target.checked);
            });
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        this.handleFiles(files);
    }

    handleFiles(files) {
        Array.from(files).forEach(file => {
            if (this.validateFile(file)) {
                this.displayFile(file);
                appState.uploadedFiles.push(file);
            }
        });
    }

    validateFile(file) {
        const maxSize = 500 * 1024 * 1024; // 500MB
        const allowedTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/quicktime'];

        if (!allowedTypes.includes(file.type)) {
            Toast.error('Formato de arquivo não suportado. Use MP4, MOV ou AVI.');
            return false;
        }

        if (file.size > maxSize) {
            Toast.error('Arquivo muito grande. Máximo 500MB.');
            return false;
        }

        return true;
    }

    displayFile(file) {
        const uploadContent = DOM.uploadArea.querySelector('.upload-content');
        uploadContent.innerHTML = `
            <i class="fas fa-check-circle" style="color: #2ed573;"></i>
            <h3>Arquivo selecionado</h3>
            <p><strong>${file.name}</strong> (${Utils.formatFileSize(file.size)})</p>
            <small>Clique para selecionar outros arquivos</small>
        `;
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (appState.uploadedFiles.length === 0) {
            Toast.error('Selecione pelo menos um arquivo de vídeo.');
            return;
        }

        const selectedPlatforms = Array.from(DOM.platformCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        if (selectedPlatforms.length === 0) {
            Toast.error('Selecione pelo menos uma plataforma.');
            return;
        }

        this.showLoading(true);

        try {
            const formData = new FormData();
            
            // Add files
            appState.uploadedFiles.forEach((file, index) => {
                formData.append(`video_${index}`, file);
            });

            // Add form data
            formData.append('title', DOM.videoTitle.value);
            formData.append('category', DOM.videoCategory.value);
            formData.append('platforms', JSON.stringify(selectedPlatforms));
            formData.append('generateContent', DOM.generateContent.checked);
            formData.append('scheduleTime', DOM.scheduleTime.value);

            const response = await ApiService.uploadVideo(formData);
            
            Toast.success('Vídeo processado com sucesso!');
            this.resetForm();

            // If scheduled, add to schedule list
            if (DOM.scheduleTime.value) {
                appState.scheduledPosts.push(response);
            }

        } catch (error) {
            Toast.error('Erro ao processar vídeo: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        DOM.loadingOverlay.classList.toggle('show', show);
    }

    resetForm() {
        DOM.uploadForm.reset();
        appState.uploadedFiles = [];
        
        DOM.platformCards.forEach(card => {
            card.classList.remove('selected');
        });

        DOM.uploadArea.querySelector('.upload-content').innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <h3>Arraste seus vídeos aqui</h3>
            <p>ou <span class="upload-link">clique para selecionar</span></p>
            <small>Formatos suportados: MP4, MOV, AVI (máx. 500MB)</small>
        `;
    }
}

// Account Manager
class AccountManager {
    init() {
        this.setupConnectButtons();
        this.setupModal();
    }

    setupConnectButtons() {
        DOM.connectButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const platform = e.target.dataset.platform;
                this.showConnectionModal(platform);
            });
        });
    }

    setupModal() {
        const modal = DOM.accountModal;
        const closeBtn = modal.querySelector('.modal-close');

        closeBtn.addEventListener('click', () => {
            this.hideModal();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideModal();
            }
        });
    }

    showConnectionModal(platform) {
        DOM.modalTitle.textContent = `Conectar ${platform}`;
        DOM.modalBody.innerHTML = this.getConnectionForm(platform);
        DOM.accountModal.classList.add('show');

        // Setup form submission
        const form = DOM.modalBody.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleConnection(e, platform));
        }
    }

    getConnectionForm(platform) {
        const forms = {
            youtube: `
                <form>
                    <div class="form-group">
                        <label>API Key do YouTube</label>
                        <input type="text" name="apiKey" placeholder="Sua API Key" required>
                    </div>
                    <div class="form-group">
                        <label>Channel ID</label>
                        <input type="text" name="channelId" placeholder="ID do seu canal" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Conectar</button>
                </form>
            `,
            instagram: `
                <form>
                    <div class="form-group">
                        <label>Username</label>
                        <input type="text" name="username" placeholder="Seu username" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password" placeholder="Sua senha" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Conectar</button>
                </form>
            `,
            tiktok: `
                <form>
                    <div class="form-group">
                        <label>Access Token</label>
                        <input type="text" name="accessToken" placeholder="Seu access token" required>
                    </div>
                    <div class="form-group">
                        <label>User ID</label>
                        <input type="text" name="userId" placeholder="Seu user ID" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Conectar</button>
                </form>
            `,
            kawai: `
                <form>
                    <div class="form-group">
                        <label>API Key</label>
                        <input type="text" name="apiKey" placeholder="Sua API Key" required>
                    </div>
                    <div class="form-group">
                        <label>User ID</label>
                        <input type="text" name="userId" placeholder="Seu user ID" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Conectar</button>
                </form>
            `
        };

        return forms[platform] || '<p>Formulário não disponível para esta plataforma.</p>';
    }

    async handleConnection(e, platform) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const credentials = Object.fromEntries(formData);

        try {
            const response = await ApiService.connectAccount(platform, credentials);
            
            if (response.success) {
                Toast.success(`Conta ${platform} conectada com sucesso!`);
                this.updateAccountStatus(platform, true);
                appState.connectedAccounts.add(platform);
                this.hideModal();
            } else {
                Toast.error(response.message || 'Erro ao conectar conta');
            }
        } catch (error) {
            Toast.error('Erro ao conectar conta: ' + error.message);
        }
    }

    updateAccountStatus(platform, connected) {
        const accountCard = document.querySelector(`.account-card.${platform}`);
        if (accountCard) {
            const statusSpan = accountCard.querySelector('.status');
            const button = accountCard.querySelector('.btn-connect');
            
            if (connected) {
                statusSpan.textContent = 'Conectado';
                statusSpan.className = 'status connected';
                button.innerHTML = '<i class="fas fa-unlink"></i> Desconectar';
            } else {
                statusSpan.textContent = 'Desconectado';
                statusSpan.className = 'status disconnected';
                button.innerHTML = '<i class="fas fa-link"></i> Conectar Conta';
            }
        }
    }

    async loadAccountStatus() {
        try {
            const response = await ApiService.getAccountStatus();
            
            Object.entries(response.accounts).forEach(([platform, status]) => {
                this.updateAccountStatus(platform, status.connected);
                if (status.connected) {
                    appState.connectedAccounts.add(platform);
                }
            });
        } catch (error) {
            console.error('Erro ao carregar status das contas:', error);
        }
    }

    hideModal() {
        DOM.accountModal.classList.remove('show');
    }
}

// Schedule Manager
class ScheduleManager {
    init() {
        this.setupFilters();
    }

    setupFilters() {
        DOM.platformFilter.addEventListener('change', this.filterSchedule.bind(this));
        DOM.dateFilter.addEventListener('change', this.filterSchedule.bind(this));
    }

    async loadScheduledPosts() {
        try {
            const filters = {
                platform: DOM.platformFilter.value,
                date: DOM.dateFilter.value
            };

            const response = await ApiService.getScheduledPosts(filters);
            this.renderScheduledPosts(response.posts);
        } catch (error) {
            console.error('Erro ao carregar agendamentos:', error);
            Toast.error('Erro ao carregar agendamentos');
        }
    }

    renderScheduledPosts(posts) {
        if (!posts || posts.length === 0) {
            DOM.scheduleList.innerHTML = `
                <div style="text-align: center; color: rgba(255,255,255,0.7); padding: 40px;">
                    <i class="fas fa-calendar" style="font-size: 3rem; margin-bottom: 20px;"></i>
                    <h3>Nenhum agendamento encontrado</h3>
                    <p>Seus posts agendados aparecerão aqui</p>
                </div>
            `;
            return;
        }

        const postsHtml = posts.map(post => `
            <div class="schedule-item" data-id="${post.id}">
                <div class="schedule-content">
                    <h4>${post.title}</h4>
                    <p><strong>Plataformas:</strong> ${post.platforms.join(', ')}</p>
                    <p><strong>Agendado para:</strong> ${Utils.formatDate(post.scheduledTime)}</p>
                    <div class="schedule-status status ${post.status}">${post.status}</div>
                </div>
                <div class="schedule-actions">
                    <button class="btn-edit" onclick="scheduleManager.editPost('${post.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-delete" onclick="scheduleManager.deletePost('${post.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        DOM.scheduleList.innerHTML = postsHtml;
    }

    filterSchedule() {
        this.loadScheduledPosts();
    }

    editPost(postId) {
        Toast.info('Funcionalidade de edição em desenvolvimento');
    }

    async deletePost(postId) {
        if (confirm('Tem certeza que deseja cancelar este agendamento?')) {
            try {
                await ApiService.request(`/schedule/${postId}`, { method: 'DELETE' });
                Toast.success('Agendamento cancelado');
                this.loadScheduledPosts();
            } catch (error) {
                Toast.error('Erro ao cancelar agendamento');
            }
        }
    }
}

// Analytics Manager
class AnalyticsManager {
    constructor() {
        this.chart = null;
    }

    async loadAnalytics() {
        try {
            const response = await ApiService.getAnalytics('30d');
            this.updateAnalyticsCards(response.summary);
            this.renderChart(response.chartData);
        } catch (error) {
            console.error('Erro ao carregar analytics:', error);
            Toast.error('Erro ao carregar analytics');
        }
    }

    updateAnalyticsCards(data) {
        DOM.analyticsElements.totalViews.textContent = this.formatNumber(data.views);
        DOM.analyticsElements.totalLikes.textContent = this.formatNumber(data.likes);
        DOM.analyticsElements.totalShares.textContent = this.formatNumber(data.shares);
        DOM.analyticsElements.totalPosts.textContent = this.formatNumber(data.posts);
        
        appState.analytics = data;
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    renderChart(data) {
        const canvas = document.getElementById('performanceChart');
        const ctx = canvas.getContext('2d');

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(255, 107, 107, 0.8)');
        gradient.addColorStop(1, 'rgba(254, 202, 87, 0.1)');

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Visualizações',
                    data: data.views,
                    borderColor: '#ff6b6b',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: 'white'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }
}

// App Initialization
class App {
    constructor() {
        this.navigation = new Navigation();
        this.uploadManager = new UploadManager();
        this.accountManager = new AccountManager();
        this.scheduleManager = new ScheduleManager();
        this.analyticsManager = new AnalyticsManager();
    }

    init() {
        // Initialize all components
        this.navigation.init();
        this.uploadManager.init();
        this.accountManager.init();
        this.scheduleManager.init();

        // Load initial data
        this.loadInitialData();

        // Setup global error handling
        window.addEventListener('error', this.handleGlobalError);
        window.addEventListener('unhandledrejection', this.handleGlobalError);
    }

    async loadInitialData() {
        try {
            // Load account status
            await this.accountManager.loadAccountStatus();
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
        }
    }

    handleGlobalError(event) {
        console.error('Global error:', event.error || event.reason);
        Toast.error('Ocorreu um erro inesperado. Tente novamente.');
    }
}

// Global instances
const app = new App();
const scheduleManager = app.scheduleManager; // For global access

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Add CSS for schedule items
const additionalCSS = `
<style>
.schedule-item {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 4px solid #feca57;
}

.schedule-content h4 {
    color: white;
    margin-bottom: 10px;
}

.schedule-content p {
    color: rgba(255, 255, 255, 0.8);
    margin: 5px 0;
    font-size: 0.9rem;
}

.schedule-actions {
    display: flex;
    gap: 10px;
}

.btn-edit, .btn-delete {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: white;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-edit:hover {
    background: rgba(254, 202, 87, 0.3);
}

.btn-delete:hover {
    background: rgba(255, 107, 107, 0.3);
}

@keyframes slideOut {
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', additionalCSS);