// static/js/components/content-templates.js
class ContentTemplateManager {
    constructor() {
        this.templates = {};
        this.currentTemplate = null;
        this.setupTemplateManager();
    }

    setupTemplateManager() {
        this.createTemplateModal();
        this.loadTemplates();
        this.bindEvents();
    }

    createTemplateModal() {
        const modalHTML = `
            <div class="modal" id="templateModal">
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>Content Templates</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="template-categories">
                            <button class="category-btn active" data-category="all">All Templates</button>
                            <button class="category-btn" data-category="viral">Viral Templates</button>
                            <button class="category-btn" data-category="educational">Educational</button>
                            <button class="category-btn" data-category="entertainment">Entertainment</button>
                        </div>
                        
                        <div class="templates-grid" id="templatesGrid">
                            <!-- Templates will be loaded here -->
                        </div>
                        
                        <div class="template-preview" id="templatePreview" style="display: none;">
                            <h4>Template Preview</h4>
                            <div class="preview-content">
                                <div class="preview-section">
                                    <h5>Title Example</h5>
                                    <p id="previewTitle"></p>
                                </div>
                                <div class="preview-section">
                                    <h5>Description Example</h5>
                                    <p id="previewDescription"></p>
                                </div>
                                <div class="preview-section">
                                    <h5>Variables Needed</h5>
                                    <div id="previewVariables"></div>
                                </div>
                            </div>
                            <div class="template-actions">
                                <button class="btn btn-secondary" id="customizeTemplate">
                                    <i class="fas fa-edit"></i> Customize
                                </button>
                                <button class="btn btn-primary" id="useTemplate">
                                    <i class="fas fa-magic"></i> Use Template
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.templateModal = document.getElementById('templateModal');
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/content-templates');
            const data = await response.json();
            
            if (data.success) {
                this.templates = data.templates;
                this.renderTemplates();
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
        }
    }

    renderTemplates(category = 'all') {
        const grid = document.getElementById('templatesGrid');
        grid.innerHTML = '';

        const filteredTemplates = this.filterTemplates(category);

        filteredTemplates.forEach(template => {
            const templateCard = document.createElement('div');
            templateCard.className = 'template-card';
            templateCard.dataset.templateId = template.id;
            
            templateCard.innerHTML = `
                <div class="template-header">
                    <h4>${template.name}</h4>
                    <div class="template-score">
                        <i class="fas fa-fire"></i>
                        <span>${template.viral_score || 85}</span>
                    </div>
                </div>
                <div class="template-description">
                    ${template.description}
                </div>
                <div class="template-stats">
                    <div class="stat">
                        <i class="fas fa-eye"></i>
                        <span>${template.avg_views || 'N/A'}</span>
                    </div>
                    <div class="stat">
                        <i class="fas fa-heart"></i>
                        <span>${template.avg_engagement || 'N/A'}</span>
                    </div>
                </div>
                <div class="template-platforms">
                    ${template.best_platforms.map(platform => 
                        `<span class="platform-tag">${platform}</span>`
                    ).join('')}
                </div>
            `;
            
            templateCard.addEventListener('click', () => {
                this.selectTemplate(template);
            });
            
            grid.appendChild(templateCard);
        });
    }

    filterTemplates(category) {
        if (category === 'all') {
            return Object.values(this.templates);
        }
        
        return Object.values(this.templates).filter(template => 
            template.category === category
        );
    }

    selectTemplate(template) {
        // Update selection
        const cards = document.querySelectorAll('.template-card');
        cards.forEach(card => card.classList.remove('selected'));
        
        const selectedCard = document.querySelector(`[data-template-id="${template.id}"]`);
        selectedCard.classList.add('selected');

        // Show preview
        this.showTemplatePreview(template);
        this.currentTemplate = template;
    }

    showTemplatePreview(template) {
        const preview = document.getElementById('templatePreview');
        
        document.getElementById('previewTitle').textContent = template.title_example;
        document.getElementById('previewDescription').textContent = template.description_example;
        
        // Show required variables
        const variablesContainer = document.getElementById('previewVariables');
        variablesContainer.innerHTML = '';
        
        template.variables.forEach(variable => {
            const varElement = document.createElement('span');
            varElement.className = 'variable-tag';
            varElement.textContent = `{${variable}}`;
            variablesContainer.appendChild(varElement);
        });
        
        preview.style.display = 'block';
    }

    bindEvents() {
        // Category filtering
        const categoryButtons = document.querySelectorAll('.category-btn');
        categoryButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                categoryButtons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.renderTemplates(e.target.dataset.category);
            });
        });

        // Modal controls
        this.templateModal.querySelector('.modal-close').addEventListener('click', () => {
            this.hideModal();
        });

        // Template actions
        document.getElementById('useTemplate').addEventListener('click', () => {
            this.useTemplate();
        });

        document.getElementById('customizeTemplate').addEventListener('click', () => {
            this.customizeTemplate();
        });
    }

    async useTemplate() {
        if (!this.currentTemplate) return;

        // Show variable input modal
        this.showVariableInputModal();
    }

    showVariableInputModal() {
        const template = this.currentTemplate;
        
        const modalHTML = `
            <div class="modal" id="variableInputModal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Customize Template: ${template.name}</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="templateVariableForm">
                            ${template.variables.map(variable => `
                                <div class="form-group">
                                    <label for="var_${variable}">${variable}</label>
                                    <input type="text" id="var_${variable}" name="${variable}" 
                                           placeholder="Enter ${variable}" required>
                                </div>
                            `).join('')}
                            
                            <div class="form-group">
                                <label>Target Platforms</label>
                                <div class="platform-selection">
                                    ${template.best_platforms.map(platform => `
                                        <label class="platform-checkbox">
                                            <input type="checkbox" name="platforms" value="${platform}" checked>
                                            <span>${platform}</span>
                                        </label>
                                    `).join('')}
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-magic"></i> Generate Content
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        const variableModal = document.getElementById('variableInputModal');
        
        // Show modal
        variableModal.classList.add('show');
        
        // Handle form submission
        document.getElementById('templateVariableForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.generateTemplateContent(new FormData(e.target));
            
            // Clean up
            variableModal.remove();
            this.hideModal();
        });
        
        // Handle modal close
        variableModal.querySelector('.modal-close').addEventListener('click', () => {
            variableModal.remove();
        });
    }

    async generateTemplateContent(formData) {
        try {
            Toast.info('Generating content from template...');
            
            const variables = {};
            const platforms = [];
            
            for (let [key, value] of formData.entries()) {
                if (key === 'platforms') {
                    platforms.push(value);
                } else {
                    variables[key] = value;
                }
            }
            
            const response = await fetch('/api/generate-from-template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    template_id: this.currentTemplate.id,
                    variables: variables,
                    platforms: platforms
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                Toast.success('Template content generated successfully!');
                this.applyTemplateContent(result.content);
            } else {
                Toast.error('Failed to generate template content');
            }
        } catch (error) {
            console.error('Template generation error:', error);
            Toast.error('Template generation failed');
        }
    }

    applyTemplateContent(content) {
        // Apply generated content to form
        if (content.title) {
            document.getElementById('videoTitle').value = content.title;
        }

        // Select platforms
        const platformCheckboxes = document.querySelectorAll('.platform-checkbox');
        platformCheckboxes.forEach(checkbox => {
            const platformValue = checkbox.value;
            checkbox.checked = content.platforms && content.platforms.includes(platformValue);
            
            // Update visual selection
            const platformCard = checkbox.closest('.platform-card');
            platformCard.classList.toggle('selected', checkbox.checked);
        });

        // Store platform-specific content
        Object.entries(content.platform_specific || {}).forEach(([platform, platformContent]) => {
            this.storePlatformContent(platform, platformContent);
        });
    }

    storePlatformContent(platform, content) {
        const platformCard = document.querySelector(`[data-platform="${platform}"]`);
        if (platformCard) {
            platformCard.dataset.templateTitle = content.title;
            platformCard.dataset.templateDescription = content.description;
            platformCard.dataset.templateHashtags = JSON.stringify(content.hashtags);
            
            // Add visual indicator
            platformCard.classList.add('has-template-content');
        }
    }

    showModal() {
        this.templateModal.classList.add('show');
    }

    hideModal() {
        this.templateModal.classList.remove('show');
    }
}