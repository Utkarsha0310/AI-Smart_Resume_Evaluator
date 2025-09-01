// ===== Chart Management System =====

class ChartManager {
    constructor(data) {
        this.data = data;
        this.charts = new Map();
        this.chartDefaults = this.getChartDefaults();
        this.colorScheme = this.getColorScheme();
    }

    getChartDefaults() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        usePointStyle: true,
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary') || '#1E293B'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 25, 47, 0.9)',
                    titleColor: '#FFFFFF',
                    bodyColor: '#CBD5E1',
                    borderColor: '#1F4068',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(203, 213, 225, 0.1)'
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary') || '#475569'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(203, 213, 225, 0.1)'
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary') || '#475569'
                    }
                }
            }
        };
    }

    getColorScheme() {
        return {
            primary: ['#0A192F', '#1F4068', '#162447', '#3A7BD5'],
            success: ['#22C55E', '#16A34A', '#15803D', '#166534'],
            warning: ['#F59E0B', '#D97706', '#B45309', '#92400E'],
            danger: ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'],
            info: ['#3B82F6', '#2563EB', '#1D4ED8', '#1E40AF'],
            gradient: [
                'rgba(58, 123, 213, 0.8)',
                'rgba(31, 64, 104, 0.8)',
                'rgba(22, 36, 71, 0.8)',
                'rgba(10, 25, 47, 0.8)'
            ]
        };
    }

    initializeSection(sectionName) {
        switch (sectionName) {
            case 'overview':
                this.initOverviewCharts();
                break;
            case 'performance':
                this.initPerformanceCharts();
                break;
            case 'content':
                this.initContentCharts();
                break;
            case 'predictions':
                this.initPredictionsCharts();
                break;
        }
    }

    initOverviewCharts() {
        this.createScoresRadarChart();
        this.createScoresPieChart();
        this.createSectionCoverageChart();
        this.createPriorityIssuesChart();
    }

    initPerformanceCharts() {
        this.createPerformanceBarChart();
        this.createATSGaugeChart();
        this.createReadabilityChart();
        this.createGrammarDoughnutChart();
    }

    initContentCharts() {
        this.createKeywordFrequencyChart();
        this.createActionVerbsChart();
        this.createContentStatsChart();
        this.createEntityDistributionChart();
        this.createKeywordDensityChart();
    }

    initPredictionsCharts() {
        this.createJobPredictionsChart();
        this.createIndustryComparisonChart();
        this.createImprovementPotentialChart();
        this.createScoreProjectionChart();
        this.createBenchmarkComparisonChart();
    }

    // Overview Charts
    createScoresRadarChart() {
        const ctx = document.getElementById('scoresRadarChart');
        if (!ctx || this.charts.has('scoresRadar')) return;

        const scores = this.data.scores || {};
        
        const config = {
            type: 'radar',
            data: {
                labels: ['Grammar', 'Readability', 'Formatting', 'ATS', 'Keywords'],
                datasets: [{
                    label: 'Your Scores',
                    data: [
                        scores.grammar || 0,
                        scores.readability || 0,
                        scores.formatting || 0,
                        scores.ats || 0,
                        scores.keywords || 0
                    ],
                    borderColor: this.colorScheme.primary[3],
                    backgroundColor: this.colorScheme.gradient[0],
                    pointBackgroundColor: this.colorScheme.primary[1],
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary')
                        },
                        grid: {
                            color: 'rgba(203, 213, 225, 0.2)'
                        },
                        angleLines: {
                            color: 'rgba(203, 213, 225, 0.2)'
                        }
                    }
                }
            }
        };

        this.charts.set('scoresRadar', new Chart(ctx, config));
    }

    createScoresPieChart() {
        const ctx = document.getElementById('scoresPieChart');
        if (!ctx || this.charts.has('scoresPie')) return;

        const scores = this.data.scores || {};
        const categories = ['Grammar', 'Readability', 'Formatting', 'ATS', 'Keywords'];
        const data = [
            scores.grammar || 0,
            scores.readability || 0,
            scores.formatting || 0,
            scores.ats || 0,
            scores.keywords || 0
        ];

        const config = {
            type: 'doughnut',
            data: {
                labels: categories,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        this.colorScheme.success[0],
                        this.colorScheme.info[0],
                        this.colorScheme.primary[1],
                        this.colorScheme.warning[0],
                        this.colorScheme.danger[0]
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...this.chartDefaults,
                cutout: '60%',
                plugins: {
                    ...this.chartDefaults.plugins,
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary'),
                            generateLabels: function(chart) {
                                const data = chart.data;
                                return data.labels.map((label, i) => {
                                    return {
                                        text: `${label}: ${data.datasets[0].data[i]}%`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].backgroundColor[i],
                                        pointStyle: 'circle'
                                    };
                                });
                            }
                        }
                    }
                }
            }
        };

        this.charts.set('scoresPie', new Chart(ctx, config));
    }

    createSectionCoverageChart() {
        const ctx = document.getElementById('sectionCoverageChart');
        if (!ctx || this.charts.has('sectionCoverage')) return;

        const structure = this.data.structure || {};
        const sections = structure.sections || {};
        
        const labels = Object.keys(sections);
        const data = Object.values(sections).map(count => count > 0 ? 1 : 0);

        const config = {
            type: 'bar',
            data: {
                labels: labels.map(label => label.charAt(0).toUpperCase() + label.slice(1)),
                datasets: [{
                    label: 'Section Present',
                    data: data,
                    backgroundColor: data.map(value => 
                        value > 0 ? this.colorScheme.success[0] : this.colorScheme.danger[0]
                    ),
                    borderColor: data.map(value => 
                        value > 0 ? this.colorScheme.success[1] : this.colorScheme.danger[1]
                    ),
                    borderWidth: 1
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    ...this.chartDefaults.scales,
                    y: {
                        ...this.chartDefaults.scales.y,
                        min: 0,
                        max: 1,
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return value === 1 ? 'Present' : 'Missing';
                            },
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary')
                        }
                    }
                }
            }
        };

        this.charts.set('sectionCoverage', new Chart(ctx, config));
    }

    createPriorityIssuesChart() {
        const ctx = document.getElementById('priorityIssuesChart');
        if (!ctx || this.charts.has('priorityIssues')) return;

        const recommendations = this.data.recommendations || [];
        const priorityCounts = { High: 0, Medium: 0, Low: 0 };
        
        recommendations.forEach(rec => {
            if (priorityCounts.hasOwnProperty(rec.priority)) {
                priorityCounts[rec.priority]++;
            }
        });

        const config = {
            type: 'doughnut',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    data: [priorityCounts.High, priorityCounts.Medium, priorityCounts.Low],
                    backgroundColor: [
                        this.colorScheme.danger[0],
                        this.colorScheme.warning[0],
                        this.colorScheme.info[0]
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...this.chartDefaults,
                cutout: '50%'
            }
        };

        this.charts.set('priorityIssues', new Chart(ctx, config));
    }

    // Performance Charts
    createPerformanceBarChart() {
        const ctx = document.getElementById('performanceBarChart');
        if (!ctx || this.charts.has('performanceBar')) return;

        const scores = this.data.scores || {};
        
        const config = {
            type: 'bar',
            data: {
                labels: ['Grammar', 'Readability', 'Formatting', 'ATS', 'Keywords'],
                datasets: [{
                    label: 'Score',
                    data: [
                        scores.grammar || 0,
                        scores.readability || 0,
                        scores.formatting || 0,
                        scores.ats || 0,
                        scores.keywords || 0
                    ],
                    backgroundColor: this.colorScheme.gradient,
                    borderColor: this.colorScheme.primary,
                    borderWidth: 1
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    ...this.chartDefaults.scales,
                    y: {
                        ...this.chartDefaults.scales.y,
                        min: 0,
                        max: 100
                    }
                }
            }
        };

        this.charts.set('performanceBar', new Chart(ctx, config));
    }

    createATSGaugeChart() {
        const ctx = document.getElementById('atsGaugeChart');
        if (!ctx || this.charts.has('atsGauge')) return;

        const atsScore = this.data.scores?.ats || 0;
        
        // Create gauge using doughnut chart
        const config = {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [atsScore, 100 - atsScore],
                    backgroundColor: [
                        this.getScoreColor(atsScore),
                        'rgba(203, 213, 225, 0.2)'
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                ...this.chartDefaults,
                rotation: -90,
                circumference: 180,
                plugins: {
                    ...this.chartDefaults.plugins,
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                }
            },
            plugins: [{
                id: 'gaugeText',
                afterDraw: (chart) => {
                    const { ctx, chartArea } = chart;
                    ctx.save();
                    
                    const centerX = (chartArea.left + chartArea.right) / 2;
                    const centerY = (chartArea.top + chartArea.bottom) / 2 + 20;
                    
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.font = 'bold 24px Arial';
                    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary');
                    ctx.fillText(`${atsScore}%`, centerX, centerY);
                    
                    ctx.font = '14px Arial';
                    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
                    ctx.fillText('ATS Score', centerX, centerY + 25);
                    
                    ctx.restore();
                }
            }]
        };

        this.charts.set('atsGauge', new Chart(ctx, config));
    }

    createReadabilityChart() {
        const ctx = document.getElementById('readabilityChart');
        if (!ctx || this.charts.has('readability')) return;

        const readability = this.data.readability || {};
        
        const config = {
            type: 'line',
            data: {
                labels: ['Flesch Reading Ease', 'Readability Score', 'Target Score'],
                datasets: [{
                    label: 'Current',
                    data: [readability.flesch_ease || 0, readability.score || 0, 80],
                    borderColor: this.colorScheme.primary[3],
                    backgroundColor: this.colorScheme.gradient[0],
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    ...this.chartDefaults.scales,
                    y: {
                        ...this.chartDefaults.scales.y,
                        min: 0,
                        max: 100
                    }
                }
            }
        };

        this.charts.set('readability', new Chart(ctx, config));
    }

    createGrammarDoughnutChart() {
        const ctx = document.getElementById('grammarDoughnutChart');
        if (!ctx || this.charts.has('grammarDoughnut')) return;

        const grammarScore = this.data.scores?.grammar || 0;
        
        const config = {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [grammarScore, 100 - grammarScore],
                    backgroundColor: [
                        this.getScoreColor(grammarScore),
                        'rgba(203, 213, 225, 0.2)'
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                ...this.chartDefaults,
                plugins: {
                    ...this.chartDefaults.plugins,
                    legend: {
                        display: false
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: (chart) => {
                    const { ctx, chartArea } = chart;
                    ctx.save();
                    
                    const centerX = (chartArea.left + chartArea.right) / 2;
                    const centerY = (chartArea.top + chartArea.bottom) / 2;
                    
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.font = 'bold 28px Arial';
                    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary');
                    ctx.fillText(`${grammarScore}%`, centerX, centerY);
                    
                    ctx.restore();
                }
            }]
        };

        this.charts.set('grammarDoughnut', new Chart(ctx, config));
    }

    // Content Analysis Charts
    createKeywordFrequencyChart() {
        const ctx = document.getElementById('keywordFrequencyChart');
        if (!ctx || this.charts.has('keywordFrequency')) return;

        const keywords = this.data.keywords?.top_10 || [];
        
        const config = {
            type: 'bar',
            data: {
                labels: keywords.slice(0, 10).map(kw => kw[0]),
                datasets: [{
                    label: 'Frequency Score',
                    data: keywords.slice(0, 10).map(kw => kw[1]),
                    backgroundColor: this.colorScheme.gradient,
                    borderColor: this.colorScheme.primary[1],
                    borderWidth: 1
                }]
            },
            options: {
                ...this.chartDefaults,
                indexAxis: 'y',
                scales: {
                    x: {
                        ...this.chartDefaults.scales.x,
                        beginAtZero: true
                    },
                    y: {
                        ...this.chartDefaults.scales.y
                    }
                }
            }
        };

        this.charts.set('keywordFrequency', new Chart(ctx, config));
    }

    createActionVerbsChart() {
        const ctx = document.getElementById('actionVerbsChart');
        if (!ctx || this.charts.has('actionVerbs')) return;

        const actionVerbs = this.data.action_verbs || {};
        
        const config = {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [actionVerbs.unique_verbs || 0, Math.max(0, 20 - (actionVerbs.unique_verbs || 0))],
                    backgroundColor: [
                        this.colorScheme.success[0],
                        'rgba(203, 213, 225, 0.2)'
                    ],
                    borderWidth: 0,
                    cutout: '60%'
                }]
            },
            options: {
                ...this.chartDefaults,
                plugins: {
                    ...this.chartDefaults.plugins,
                    legend: {
                        display: false
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: (chart) => {
                    const { ctx, chartArea } = chart;
                    ctx.save();
                    
                    const centerX = (chartArea.left + chartArea.right) / 2;
                    const centerY = (chartArea.top + chartArea.bottom) / 2;
                    
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.font = 'bold 20px Arial';
                    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary');
                    ctx.fillText(`${actionVerbs.unique_verbs || 0}`, centerX, centerY - 5);
                    
                    ctx.font = '12px Arial';
                    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
                    ctx.fillText('Action Verbs', centerX, centerY + 15);
                    
                    ctx.restore();
                }
            }]
        };

        this.charts.set('actionVerbs', new Chart(ctx, config));
    }

    createContentStatsChart() {
        const ctx = document.getElementById('contentStatsChart');
        if (!ctx || this.charts.has('contentStats')) return;

        const wordCount = this.data.word_count || 0;
        const textLength = this.data.text_length || 0;
        const keywordCount = this.data.keywords?.count || 0;
        
        const config = {
            type: 'bar',
            data: {
                labels: ['Word Count', 'Character Count', 'Keywords'],
                datasets: [{
                    label: 'Count',
                    data: [wordCount, Math.round(textLength / 10), keywordCount * 10],
                    backgroundColor: [
                        this.colorScheme.info[0],
                        this.colorScheme.warning[0],
                        this.colorScheme.success[0]
                    ],
                    borderColor: [
                        this.colorScheme.info[1],
                        this.colorScheme.warning[1],
                        this.colorScheme.success[1]
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                ...this.chartDefaults,
                plugins: {
                    ...this.chartDefaults.plugins,
                    tooltip: {
                        ...this.chartDefaults.plugins.tooltip,
                        callbacks: {
                            label: function(context) {
                                const label = context.label;
                                let value = context.parsed.y;
                                
                                if (label === 'Character Count') {
                                    value = value * 10;
                                } else if (label === 'Keywords') {
                                    value = value / 10;
                                }
                                
                                return `${label}: ${value}`;
                            }
                        }
                    }
                }
            }
        };

        this.charts.set('contentStats', new Chart(ctx, config));
    }

    createEntityDistributionChart() {
        const ctx = document.getElementById('entityDistributionChart');
        if (!ctx || this.charts.has('entityDistribution')) return;

        const entities = this.data.entities || {};
        const entityTypes = Object.keys(entities).slice(0, 8);
        const entityCounts = entityTypes.map(type => entities[type].length);
        
        const config = {
            type: 'pie',
            data: {
                labels: entityTypes,
                datasets: [{
                    data: entityCounts,
                    backgroundColor: this.colorScheme.primary.concat(this.colorScheme.info),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...this.chartDefaults,
                plugins: {
                    ...this.chartDefaults.plugins,
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary')
                        }
                    }
                }
            }
        };

        this.charts.set('entityDistribution', new Chart(ctx, config));
    }

    createKeywordDensityChart() {
        const ctx = document.getElementById('keywordDensityChart');
        if (!ctx || this.charts.has('keywordDensity')) return;

        const keywords = this.data.keywords?.top_10 || [];
        
        const config = {
            type: 'line',
            data: {
                labels: keywords.slice(0, 15).map(kw => kw[0]),
                datasets: [{
                    label: 'Keyword Density',
                    data: keywords.slice(0, 15).map(kw => kw[1] * 100),
                    borderColor: this.colorScheme.primary[3],
                    backgroundColor: this.colorScheme.gradient[0],
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    ...this.chartDefaults.scales,
                    y: {
                        ...this.chartDefaults.scales.y,
                        beginAtZero: true
                    }
                }
            }
        };

        this.charts.set('keywordDensity', new Chart(ctx, config));
    }

    // Predictions Charts
    createJobPredictionsChart() {
        const ctx = document.getElementById('jobPredictionsChart');
        if (!ctx || this.charts.has('jobPredictions')) return;

        const predictions = this.data.job_predictions || [];
        
        const config = {
            type: 'bar',
            data: {
                labels: predictions.map(pred => pred.role),
                datasets: [{
                    label: 'Match Score (%)',
                    data: predictions.map(pred => pred.match_score),
                    backgroundColor: predictions.map((_, index) => this.colorScheme.gradient[index % this.colorScheme.gradient.length]),
                    borderColor: this.colorScheme.primary[1],
                    borderWidth: 1
                }]
            },
            options: {
                ...this.chartDefaults,
                indexAxis: 'y',
                scales: {
                    x: {
                        ...this.chartDefaults.scales.x,
                        min: 0,
                        max: 100
                    },
                    y: {
                        ...this.chartDefaults.scales.y
                    }
                }
            }
        };

        this.charts.set('jobPredictions', new Chart(ctx, config));
    }

    createIndustryComparisonChart() {
        const ctx = document.getElementById('industryComparisonChart');
        if (!ctx || this.charts.has('industryComparison')) return;

        const comparison = this.data.exemplar_comparison || {};
        const matchScore = comparison.match_score || 0;
        
        const config = {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [matchScore, 100 - matchScore],
                    backgroundColor: [
                        this.getScoreColor(matchScore),
                        'rgba(203, 213, 225, 0.2)'
                    ],
                    borderWidth: 0,
                    cutout: '65%'
                }]
            },
            options: {
                ...this.chartDefaults,
                plugins: {
                    ...this.chartDefaults.plugins,
                    legend: {
                        display: false
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw: (chart) => {
                    const { ctx, chartArea } = chart;
                    ctx.save();
                    
                    const centerX = (chartArea.left + chartArea.right) / 2;
                    const centerY = (chartArea.top + chartArea.bottom) / 2;
                    
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.font = 'bold 24px Arial';
                    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary');
                    ctx.fillText(`${Math.round(matchScore)}%`, centerX, centerY - 5);
                    
                    ctx.font = '12px Arial';
                    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');
                    ctx.fillText('Industry Match', centerX, centerY + 20);
                    
                    ctx.restore();
                }
            }]
        };

        this.charts.set('industryComparison', new Chart(ctx, config));
    }

    createImprovementPotentialChart() {
        const ctx = document.getElementById('improvementPotentialChart');
        if (!ctx || this.charts.has('improvementPotential')) return;

        const scores = this.data.scores || {};
        const currentScores = [
            scores.grammar || 0,
            scores.readability || 0,
            scores.formatting || 0,
            scores.ats || 0,
            scores.keywords || 0
        ];
        
        const potentialScores = currentScores.map(score => Math.min(100, score + 15));
        
        const config = {
            type: 'radar',
            data: {
                labels: ['Grammar', 'Readability', 'Formatting', 'ATS', 'Keywords'],
                datasets: [{
                    label: 'Current',
                    data: currentScores,
                    borderColor: this.colorScheme.primary[1],
                    backgroundColor: 'rgba(31, 64, 104, 0.2)',
                    pointBackgroundColor: this.colorScheme.primary[1]
                }, {
                    label: 'Potential',
                    data: potentialScores,
                    borderColor: this.colorScheme.success[0],
                    backgroundColor: 'rgba(34, 197, 94, 0.2)',
                    pointBackgroundColor: this.colorScheme.success[0]
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary')
                        }
                    }
                }
            }
        };

        this.charts.set('improvementPotential', new Chart(ctx, config));
    }

    createScoreProjectionChart() {
        const ctx = document.getElementById('scoreProjectionChart');
        if (!ctx || this.charts.has('scoreProjection')) return;

        const currentScore = this.data.scores?.composite || 0;
        const timeline = ['Current', '1 Month', '3 Months', '6 Months'];
        const projectedScores = [
            currentScore,
            Math.min(100, currentScore + 10),
            Math.min(100, currentScore + 20),
            Math.min(100, currentScore + 30)
        ];
        
        const config = {
            type: 'line',
            data: {
                labels: timeline,
                datasets: [{
                    label: 'Projected Score',
                    data: projectedScores,
                    borderColor: this.colorScheme.success[0],
                    backgroundColor: this.colorScheme.gradient[0],
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    ...this.chartDefaults.scales,
                    y: {
                        ...this.chartDefaults.scales.y,
                        min: 0,
                        max: 100
                    }
                }
            }
        };

        this.charts.set('scoreProjection', new Chart(ctx, config));
    }

    createBenchmarkComparisonChart() {
        const ctx = document.getElementById('benchmarkComparisonChart');
        if (!ctx || this.charts.has('benchmarkComparison')) return;

        const scores = this.data.scores || {};
        const categories = ['Grammar', 'Readability', 'Formatting', 'ATS', 'Keywords'];
        const userScores = [
            scores.grammar || 0,
            scores.readability || 0,
            scores.formatting || 0,
            scores.ats || 0,
            scores.keywords || 0
        ];
        
        // Industry benchmarks (example data)
        const industryBenchmarks = [85, 80, 82, 88, 75];
        const topPerformers = [95, 92, 94, 96, 90];
        
        const config = {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [{
                    label: 'Your Score',
                    data: userScores,
                    backgroundColor: this.colorScheme.primary[3],
                    borderColor: this.colorScheme.primary[1],
                    borderWidth: 1
                }, {
                    label: 'Industry Average',
                    data: industryBenchmarks,
                    backgroundColor: this.colorScheme.warning[0],
                    borderColor: this.colorScheme.warning[1],
                    borderWidth: 1
                }, {
                    label: 'Top Performers',
                    data: topPerformers,
                    backgroundColor: this.colorScheme.success[0],
                    borderColor: this.colorScheme.success[1],
                    borderWidth: 1
                }]
            },
            options: {
                ...this.chartDefaults,
                scales: {
                    ...this.chartDefaults.scales,
                    y: {
                        ...this.chartDefaults.scales.y,
                        min: 0,
                        max: 100
                    }
                }
            }
        };

        this.charts.set('benchmarkComparison', new Chart(ctx, config));
    }

    // Utility methods
    getScoreColor(score) {
        if (score >= 90) return this.colorScheme.success[0];
        if (score >= 80) return this.colorScheme.info[0];
        if (score >= 70) return this.colorScheme.warning[0];
        if (score >= 60) return this.colorScheme.danger[0];
        return this.colorScheme.danger[1];
    }

    exportAllCharts() {
        const zip = new JSZip();
        const promises = [];

        this.charts.forEach((chart, name) => {
            const canvas = chart.canvas;
            const imgData = canvas.toDataURL('image/png');
            const imgBlob = this.dataURLtoBlob(imgData);
            zip.file(`${name}_chart.png`, imgBlob);
        });

        zip.generateAsync({ type: 'blob' }).then(content => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(content);
            link.download = 'resume_analysis_charts.zip';
            link.click();
        });
    }

    exportData() {
        const csvContent = this.convertDataToCSV(this.data);
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'resume_analysis_data.csv';
        link.click();
    }

    dataURLtoBlob(dataURL) {
        const arr = dataURL.split(',');
        const mime = arr[0].match(/:(.*?);/)[1];
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);
        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], { type: mime });
    }

    convertDataToCSV(data) {
        const rows = [];
        
        // Header
        rows.push(['Metric', 'Value', 'Category']);
        
        // Scores
        if (data.scores) {
            Object.entries(data.scores).forEach(([key, value]) => {
                rows.push([key, value, 'Score']);
            });
        }
        
        // Keywords
        if (data.keywords && data.keywords.top_10) {
            data.keywords.top_10.forEach(([keyword, score]) => {
                rows.push([keyword, score, 'Keyword']);
            });
        }
        
        // Job predictions
        if (data.job_predictions) {
            data.job_predictions.forEach(pred => {
                rows.push([pred.role, pred.match_score, 'Job Prediction']);
            });
        }
        
        return rows.map(row => row.join(',')).join('\n');
    }

    destroy() {
        this.charts.forEach(chart => {
            chart.destroy();
        });
        this.charts.clear();
    }
}

// Initialize charts when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Register Chart.js defaults
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-primary') || '#1E293B';
        Chart.defaults.borderColor = 'rgba(203, 213, 225, 0.2)';
    }
});

// Export for global use
window.ChartManager = ChartManager;
