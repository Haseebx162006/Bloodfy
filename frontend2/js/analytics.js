/**
 * Analytics Page Integration Script
 * Display statistics and charts
 */

document.addEventListener('DOMContentLoaded', async () => {
    await initializeAnalyticsPage();
});

// =============================================================================
// ANALYTICS PAGE
// =============================================================================

async function initializeAnalyticsPage() {
    console.log('Initializing analytics page...');

    // Load all statistics
    await Promise.all([
        loadDonorStats(),
        loadBloodStockStats(),
        loadAIMetrics(),
    ]);
}

// =============================================================================
// LOAD STATISTICS
// =============================================================================

async function loadDonorStats() {
    try {
        const result = await API.donors.getStatistics();

        if (result.success && result.data) {
            displayDonorStats(result.data);
        }
    } catch (error) {
        console.error('Error loading donor stats:', error);
    }
}

function displayDonorStats(stats) {
    // Update donor statistics elements
    const totalDonorsEl = document.getElementById('totalDonors');
    if (totalDonorsEl) totalDonorsEl.textContent = stats.total_donors || 0;

    const activeDonorsEl = document.getElementById('activeDonors');
    if (activeDonorsEl) activeDonorsEl.textContent = stats.active_donors || 0;

    const eligibleDonorsEl = document.getElementById('eligibleDonors');
    if (eligibleDonorsEl) eligibleDonorsEl.textContent = stats.eligible_donors || 0;

    const totalDonationsEl = document.getElementById('totalDonations');
    if (totalDonationsEl) totalDonationsEl.textContent = stats.total_donations || 0;
}

async function loadBloodStockStats() {
    try {
        const result = await API.bloodStock.getStatistics();

        if (result.success && result.data) {
            displayBloodStockStats(result.data);
        }
    } catch (error) {
        console.error('Error loading blood stock stats:', error);
    }
}

function displayBloodStockStats(stats) {
    // Update blood stock statistics
    const totalUnitsEl = document.getElementById('totalUnits');
    if (totalUnitsEl) totalUnitsEl.textContent = stats.total_units || 0;

    const criticalStockEl = document.getElementById('criticalStock');
    if (criticalStockEl) criticalStockEl.textContent = stats.critical_count || 0;

    const lowStockEl = document.getElementById('lowStock');
    if (lowStockEl) lowStockEl.textContent = stats.low_count || 0;

    // Display blood group distribution if available
    if (stats.by_blood_group) {
        displayBloodGroupChart(stats.by_blood_group);
    }
}

async function loadAIMetrics() {
    try {
        const result = await API.ai.getMetrics();

        if (result.success && result.data) {
            displayAIMetrics(result.data);
        }
    } catch (error) {
        console.error('Error loading AI metrics:', error);
    }
}

function displayAIMetrics(metrics) {
    // Update AI metrics
    const accuracyEl = document.getElementById('aiAccuracy');
    if (accuracyEl) accuracyEl.textContent = (metrics.accuracy || 0) + '%';

    const predictionsEl = document.getElementById('totalPredictions');
    if (predictionsEl) predictionsEl.textContent = metrics.total_predictions || 0;

    const successRateEl = document.getElementById('successRate');
    if (successRateEl) successRateEl.textContent = (metrics.success_rate || 0) + '%';
}

// =============================================================================
// CHARTS (Simple Text-Based for Now)
// =============================================================================

function displayBloodGroupChart(bloodGroupData) {
    const chartContainer = document.getElementById('bloodGroupChart');

    if (!chartContainer) return;

    // Clear existing content
    chartContainer.innerHTML = '';

    // Create simple bar chart using HTML/CSS
    Object.entries(bloodGroupData).forEach(([bloodGroup, count]) => {
        const barWrapper = document.createElement('div');
        barWrapper.style.cssText = 'margin-bottom: 10px;';

        const label = document.createElement('div');
        label.textContent = `${bloodGroup}: ${count} units`;
        label.style.cssText = 'font-size: 0.9rem; margin-bottom: 5px;';

        const barOuter = document.createElement('div');
        barOuter.style.cssText = 'width: 100%; height: 25px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden;';

        const barInner = document.createElement('div');
        const maxCount = Math.max(...Object.values(bloodGroupData));
        const percentage = (count / maxCount) * 100;
        barInner.style.cssText = `width: ${percentage}%; height: 100%; background: var(--primary-red); transition: width 0.5s ease;`;

        barOuter.appendChild(barInner);
        barWrapper.appendChild(label);
        barWrapper.appendChild(barOuter);
        chartContainer.appendChild(barWrapper);
    });
}

// =============================================================================
// EXPORT FUNCTIONALITY
// =============================================================================

window.exportAnalyticsReport = async function () {
    try {
        showSuccess('Generating analytics report...');

        const [donorStats, stockStats, aiMetrics] = await Promise.all([
            API.donors.getStatistics(),
            API.bloodStock.getStatistics(),
            API.ai.getMetrics(),
        ]);

        const report = {
            generated_at: new Date().toISOString(),
            donor_statistics: donorStats.data,
            blood_stock_statistics: stockStats.data,
            ai_metrics: aiMetrics.data,
        };

        // Download as JSON
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bloodify-analytics-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);

        showSuccess('Analytics report downloaded!');
    } catch (error) {
        console.error('Error exporting analytics:', error);
        showError('Failed to export analytics report');
    }
};
