// static/js/utils/api-client.js
class APIClient {
    constructor() {
        this.baseURL = '/api';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: {
                ...this.defaultHeaders,
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            throw error;
        }
    }

    // Convenience methods
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    async uploadFile(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            headers: {}, // Let browser set Content-Type for FormData
            body: formData
        });
    }
}

// Enhanced app initialization with new components
document.addEventListener('DOMContentLoaded', () => {
    // Initialize existing app
    app.init();
    
    // Initialize new components
    window.viralAnalyzer = new ViralAnalyzer();
    window.templateManager = new ContentTemplateManager();
    window.performanceTracker = new PerformanceTracker();
    window.apiClient = new APIClient();
    
    // Add enhanced upload functionality
    enhanceUploadManager();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup tooltips and help system
    setupHelpSystem();
});

function enhanceUploadManager() {
    // Add analyze viral potential button to upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        const analyzeButton = document.createElement('button');
        analyzeButton.type = 'button';
        analyzeButton.className = 'btn btn-secondary';
        analyzeButton.innerHTML = '<i class="fas fa-chart-line"></i> Analyze Viral Potential';
        analyzeButton.id = 'analyzeViralBtn';
        
        // Insert before submit button
        const submitButton = uploadForm.querySelector('button[type="submit"]');
        submitButton.parentNode.insertBefore(analyzeButton, submitButton);
        
        // Add event listener
        analyzeButton.addEventListener('click', () => {
            const formData = new FormData(uploadForm);
            const contentData = {
                title: formData.get('title'),
                description: formData.get('description') || '',
                category: formData.get('category'),
                platforms: Array.from(document.querySelectorAll('.platform-checkbox:checked')).map(cb => cb.value)
            };
            
            window.viralAnalyzer.analyzeContent(contentData);
        });
    }
    
    // Add template button
    const templateButton = document.createElement('button');
    templateButton.type = 'button';
    templateButton.className = 'btn btn-info';
    templateButton.innerHTML = '<i class="fas fa-templates"></i> Use Template';
    templateButton.id = 'useTemplateBtn';
    
    if (uploadForm) {
        const analyzeButton = document.getElementById('analyzeViralBtn');
        analyzeButton.parentNode.insertBefore(templateButton, analyzeButton);
        
        templateButton.addEventListener('click', () => {
            window.templateManager.showModal();
        });
    }
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'u':
                    e.preventDefault();
                    document.querySelector('[data-section="upload"]').click();
                    break;
                case 'a':
                    e.preventDefault();
                    document.querySelector('[data-section="analytics"]').click();
                    break;
                case 's':
                    e.preventDefault();
                    document.querySelector('[data-section="schedule"]').click();
                    break;
                case 't':
                    e.preventDefault();
                    window.templateManager.showModal();
                    break;
            }
        }
        
        // Escape key closes modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                modal.classList.remove('show');
            });
        }
    });
}

function setupHelpSystem() {
    // Add help tooltips
    const helpElements = document.querySelectorAll('[data-help]');
    
    helpElements.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            showTooltip(e.target, e.target.dataset.help);
        });
        
        element.addEventListener('mouseleave', () => {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.id = 'activeTooltip';
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = `${rect.left + (rect.width / 2)}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
    
    setTimeout(() => tooltip.classList.add('show'), 10);
}

function hideTooltip() {
    const tooltip = document.getElementById('activeTooltip');
    if (tooltip) {
        tooltip.remove();
    }
}