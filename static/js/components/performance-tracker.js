// static/js/components/performance-tracker.js
class PerformanceTracker {
    constructor() {
        this.charts = {};
        this.currentPeriod = '30d';
        this.setupTracker();
    }

    setupTracker() {
        this.bindEvents();
        this.loadPerformanceData();
    }

    bindEvents() {
        // Period selection
        const periodButtons = document.querySelectorAll('[data-period]');
        periodButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.changePeriod(e.target.dataset.period);
            });
        });

        // Refresh data
        const refreshBtn = document.getElementById('refreshAnalytics');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadPerformanceData();
            });
        }
    }

    async loadPerformanceData() {
        try {
            const response = await fetch(`/api/analytics?period=${this.currentPeriod}`);
            const data = await response.json();
            
            if (data.success) {
                this.updateAnalyticsDisplay(data);
                this.renderPerformanceCharts(data.chartData);
                this.showInsights(data.insights);
            }
        } catch (error) {
            console.error('Failed to load performance data:', error);
            Toast.error('Failed to load analytics data');
        }
    }

    updateAnalyticsDisplay(data) {
        const summary = data.summary;
        
        // Update metric cards
        if (DOM.analyticsElements) {
            DOM.analyticsElements.totalViews.textContent = this.formatNumber(summary.views);
            DOM.analyticsElements.totalLikes.textContent = this.formatNumber(summary.likes);
            DOM.analyticsElements.totalShares.textContent = this.formatNumber(summary.shares);
            DOM.analyticsElements.totalPosts.textContent = this.formatNumber(summary.posts);
        }

        // Update platform breakdown
        this.updatePlatformBreakdown(data.platformBreakdown);
        
        // Animate counters
        this.animateCounters();
    }

    updatePlatformBreakdown(breakdown) {
        const breakdownContainer = document.getElementById('platformBreakdown');
        if (!breakdownContainer) return;

        breakdownContainer.innerHTML = '';
        
        Object.entries(breakdown).forEach(([platform, data]) => {
            const platformElement = document.createElement('div');
            platformElement.className = 'platform-breakdown-item';
            
            platformElement.innerHTML = `
                <div class="platform-info">
                    <i class="fab fa-${platform}"></i>
                    <span class="platform-name">${platform}</span>
                </div>
                <div class="platform-metrics">
                    <div class="metric">
                        <span class="metric-value">${this.formatNumber(data.views)}</span>
                        <span class="metric-label">Views</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${data.engagement}%</span>
                        <span class="metric-label">Engagement</span>
                    </div>
                </div>
                <div class="platform-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${data.engagement}%"></div>
                    </div>
                </div>
            `;
            
            breakdownContainer.appendChild(platformElement);
        });
    }

    renderPerformanceCharts(chartData) {
        // Main performance chart
        this.renderMainChart(chartData);
        
        // Platform comparison chart
        this.renderPlatformChart(chartData);
        
        // Engagement timeline
        this.renderEngagementChart(chartData);
    }

    renderMainChart(data) {
        const canvas = document.getElementById('performanceChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart
        if (this.charts.main) {
            this.charts.main.destroy();
        }

        this.charts.main = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Views',
                        data: data.views,
                        borderColor: '#ff6b6b',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Engagement',
                        data: data.engagement,
                        borderColor: '#feca57',
                        backgroundColor: 'rgba(254, 202, 87, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: 'white' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    showInsights(insights) {
        const insightsContainer = document.getElementById('performanceInsights');
        if (!insightsContainer) return;

        insightsContainer.innerHTML = '';

        insights.forEach(insight => {
            const insightElement = document.createElement('div');
            insightElement.className = `insight-card ${insight.type}`;
            
            insightElement.innerHTML = `
                <div class="insight-icon">
                    <i class="fas fa-${this.getInsightIcon(insight.type)}"></i>
                </div>
                <div class="insight-content">
                    <h4>${insight.title}</h4>
                    <p>${insight.description}</p>
                    <div class="insight-action">${insight.action}</div>
                </div>
            `;
            
            insightsContainer.appendChild(insightElement);
        });
    }

    getInsightIcon(type) {
        const icons = {
            'positive': 'arrow-up',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'tip': 'lightbulb'
        };
        return icons[type] || 'info-circle';
    }

    animateCounters() {
        const counters = document.querySelectorAll('.analytics-content h3');
        
        counters.forEach(counter => {
            const target = parseInt(counter.textContent.replace(/[^0-9]/g, ''));
            let current = 0;
            const increment = target / 50;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = this.formatNumber(target);
                    clearInterval(timer);
                } else {
                    counter.textContent = this.formatNumber(Math.floor(current));
                }
            }, 20);
        });
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    changePeriod(period) {
        this.currentPeriod = period;
        
        // Update active button
        const periodButtons = document.querySelectorAll('[data-period]');
        periodButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.period === period);
        });
        
        // Reload data
        this.loadPerformanceData();
    }
}