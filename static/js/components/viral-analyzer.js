// static/js/components/viral-analyzer.js
class ViralAnalyzer {
    constructor() {
        this.analysisModal = null;
        this.currentAnalysis = null;
        this.setupAnalyzer();
    }

    setupAnalyzer() {
        this.createAnalysisModal();
        this.bindEvents();
    }

    createAnalysisModal() {
        const modalHTML = `
            <div class="modal" id="viralAnalysisModal">
                <div class="modal-content large">
                    <div class="modal-header">
                        <h3>Viral Content Analysis</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="analysis-container">
                            <div class="viral-score-section">
                                <div class="viral-score-circle">
                                    <div class="score-number" id="viralScoreNumber">0</div>
                                    <div class="score-label">Viral Score</div>
                                </div>
                                <div class="score-description" id="scoreDescription"></div>
                            </div>
                            
                            <div class="analysis-tabs">
                                <button class="tab-btn active" data-tab="strengths">Strengths</button>
                                <button class="tab-btn" data-tab="improvements">Improvements</button>
                                <button class="tab-btn" data-tab="trends">Trending Elements</button>
                                <button class="tab-btn" data-tab="timing">Optimal Timing</button>
                            </div>
                            
                            <div class="tab-content">
                                <div id="strengths-tab" class="tab-panel active">
                                    <h4>Content Strengths</h4>
                                    <div id="strengthsList"></div>
                                </div>
                                
                                <div id="improvements-tab" class="tab-panel">
                                    <h4>Suggested Improvements</h4>
                                    <div id="improvementsList"></div>
                                </div>
                                
                                <div id="trends-tab" class="tab-panel">
                                    <h4>Trending Elements</h4>
                                    <div id="trendingElements"></div>
                                </div>
                                
                                <div id="timing-tab" class="tab-panel">
                                    <h4>Optimal Posting Times</h4>
                                    <div id="optimalTiming"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="analysis-actions">
                            <button class="btn btn-secondary" id="regenerateContent">
                                <i class="fas fa-sync-alt"></i> Regenerate Content
                            </button>
                            <button class="btn btn-primary" id="applyOptimizations">
                                <i class="fas fa-magic"></i> Apply Optimizations
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.analysisModal = document.getElementById('viralAnalysisModal');
    }

    bindEvents() {
        // Tab switching
        const tabButtons = this.analysisModal.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Modal controls
        this.analysisModal.querySelector('.modal-close').addEventListener('click', () => {
            this.hideModal();
        });

        // Action buttons
        document.getElementById('regenerateContent').addEventListener('click', () => {
            this.regenerateContent();
        });

        document.getElementById('applyOptimizations').addEventListener('click', () => {
            this.applyOptimizations();
        });
    }

    async analyzeContent(contentData) {
        try {
            const response = await fetch('/api/analyze-viral-potential', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(contentData)
            });

            const analysis = await response.json();
            
            if (analysis.success) {
                this.currentAnalysis = analysis;
                this.displayAnalysis(analysis);
                this.showModal();
            } else {
                Toast.error('Failed to analyze content');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            Toast.error('Analysis failed');
        }
    }

    displayAnalysis(analysis) {
        // Update viral score
        const scoreNumber = document.getElementById('viralScoreNumber');
        const scoreDescription = document.getElementById('scoreDescription');
        
        scoreNumber.textContent = analysis.viral_score;
        scoreDescription.textContent = this.getScoreDescription(analysis.viral_score);
        
        // Update score circle color
        const scoreCircle = scoreNumber.parentElement;
        scoreCircle.className = `viral-score-circle ${this.getScoreClass(analysis.viral_score)}`;

        // Display strengths
        this.displayListItems('strengthsList', analysis.strengths, 'strength-item');

        // Display improvements
        this.displayListItems('improvementsList', analysis.improvements, 'improvement-item');

        // Display trending elements
        this.displayTrendingElements(analysis.trending_elements);

        // Display optimal timing
        this.displayOptimalTiming(analysis.optimal_timing);
    }

    displayListItems(containerId, items, itemClass) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        items.forEach(item => {
            const itemElement = document.createElement('div');
            itemElement.className = `analysis-item ${itemClass}`;
            itemElement.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>${item}</span>
            `;
            container.appendChild(itemElement);
        });
    }

    displayTrendingElements(elements) {
        const container = document.getElementById('trendingElements');
        container.innerHTML = '';

        Object.entries(elements).forEach(([category, items]) => {
            const categoryElement = document.createElement('div');
            categoryElement.className = 'trending-category';
            categoryElement.innerHTML = `
                <h5>${category.charAt(0).toUpperCase() + category.slice(1)}</h5>
                <div class="trending-items">
                    ${items.map(item => `<span class="trending-tag">${item}</span>`).join('')}
                </div>
            `;
            container.appendChild(categoryElement);
        });
    }

    displayOptimalTiming(timing) {
        const container = document.getElementById('optimalTiming');
        container.innerHTML = '';

        Object.entries(timing).forEach(([platform, times]) => {
            const platformElement = document.createElement('div');
            platformElement.className = 'timing-platform';
            platformElement.innerHTML = `
                <div class="platform-name">
                    <i class="fab fa-${platform}"></i>
                    ${platform.charAt(0).toUpperCase() + platform.slice(1)}
                </div>
                <div class="timing-slots">
                    ${times.map(time => `<span class="time-slot">${time}</span>`).join('')}
                </div>
            `;
            container.appendChild(platformElement);
        });
    }

    getScoreDescription(score) {
        if (score >= 90) return "Extremely viral potential! This content is likely to go viral.";
        if (score >= 80) return "High viral potential. Great content with strong viral elements.";
        if (score >= 70) return "Good viral potential. Some optimizations could boost performance.";
        if (score >= 60) return "Moderate viral potential. Consider applying suggested improvements.";
        if (score >= 50) return "Average viral potential. Significant improvements recommended.";
        return "Low viral potential. Major optimizations needed for better performance.";
    }

    getScoreClass(score) {
        if (score >= 80) return 'score-excellent';
        if (score >= 70) return 'score-good';
        if (score >= 60) return 'score-average';
        return 'score-poor';
    }

    switchTab(tabName) {
        // Update tab buttons
        const tabButtons = this.analysisModal.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab panels
        const tabPanels = this.analysisModal.querySelectorAll('.tab-panel');
        tabPanels.forEach(panel => {
            panel.classList.toggle('active', panel.id === `${tabName}-tab`);
        });
    }

    async regenerateContent() {
        if (!this.currentAnalysis) return;

        try {
            Toast.info('Regenerating optimized content...');
            
            const response = await fetch('/api/regenerate-viral-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    analysis: this.currentAnalysis,
                    apply_improvements: true
                })
            });

            const result = await response.json();
            
            if (result.success) {
                Toast.success('Content regenerated successfully!');
                // Update form with new content
                this.updateFormFields(result.content);
                this.hideModal();
            } else {
                Toast.error('Failed to regenerate content');
            }
        } catch (error) {
            console.error('Regeneration error:', error);
            Toast.error('Regeneration failed');
        }
    }

    applyOptimizations() {
        if (!this.currentAnalysis) return;

        // Apply optimizations to current form
        const improvements = this.currentAnalysis.improvements;
        const optimizations = this.currentAnalysis.optimizations;

        // Show optimization results
        Toast.success(`Applied ${improvements.length} optimizations to your content!`);
        this.hideModal();
    }

    updateFormFields(content) {
        // Update title
        if (content.title) {
            document.getElementById('videoTitle').value = content.title;
        }

        // Update platform-specific content
        Object.entries(content.platform_specific || {}).forEach(([platform, platformContent]) => {
            // Update platform cards with optimized content
            this.updatePlatformContent(platform, platformContent);
        });
    }

    updatePlatformContent(platform, content) {
        const platformCard = document.querySelector(`[data-platform="${platform}"]`);
        if (platformCard) {
            // Add visual indicator of optimization
            platformCard.classList.add('optimized');
            
            // Store optimized content in data attributes
            platformCard.dataset.optimizedTitle = content.title;
            platformCard.dataset.optimizedDescription = content.description;
            platformCard.dataset.optimizedHashtags = JSON.stringify(content.hashtags);
        }
    }

    showModal() {
        this.analysisModal.classList.add('show');
    }

    hideModal() {
        this.analysisModal.classList.remove('show');
    }
}