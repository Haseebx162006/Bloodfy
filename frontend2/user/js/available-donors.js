/**
 * Available Donors Integration Script
 * Handles fetching, filtering and displaying approved donors
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    loadDonors();

    // Event Listeners
    const bloodGroupFilter = document.getElementById('bloodGroupFilter');
    const cityFilter = document.getElementById('cityFilter');
    const resetBtn = document.getElementById('resetFilters');

    if (bloodGroupFilter) {
        bloodGroupFilter.addEventListener('change', () => applyFilters());
    }

    if (cityFilter) {
        let timeout;
        cityFilter.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => applyFilters(), 500);
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            bloodGroupFilter.value = '';
            cityFilter.value = '';
            loadDonors();
        });
    }

    // Set body as loaded
    document.body.classList.add('loaded');
});

async function loadDonors(filters = {}) {
    const grid = document.getElementById('donorsGrid');
    if (!grid) return;

    // Show loading state
    grid.innerHTML = `
        <div class="loading-state">
            <i class="fa-solid fa-spinner fa-spin"></i>
            <p>Finding life savers...</p>
        </div>
    `;

    try {
        // Query param construction
        const params = {
            ...filters,
            is_active: true,
            user_donor_status: 'DONOR_APPROVED' // Backend filters this but just to be safe
        };

        const response = await API.donors.getList(params);

        if (response.success && response.data) {
            const donors = response.data.donors || [];

            if (donors.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-user-slash"></i>
                        <h2>No donors found</h2>
                        <p>Try changing your filters or check back later.</p>
                    </div>
                `;
                return;
            }

            renderDonors(donors, grid);
        } else {
            grid.innerHTML = `<div class="empty-state"><p>${response.message || 'Failed to load donors'}</p></div>`;
        }
    } catch (error) {
        console.error('Error loading donors:', error);
        grid.innerHTML = `<div class="empty-state"><p>Error: ${error.message || 'Failed to connect to server'}</p></div>`;
    }
}

function renderDonors(donors, container) {
    container.innerHTML = '';

    donors.forEach(donor => {
        const card = document.createElement('div');
        card.className = 'donor-card';

        const availabilityText = donor.availability_status ? 'Available' : 'On Cooldown';
        const availabilityClass = donor.availability_status ? 'status-available' : 'status-unavailable';
        const name = donor.name || 'Anonymous Donor';
        const phone = donor.phone || '';

        card.innerHTML = `
            <div class="donor-blood-badge">${donor.blood_group}</div>
            <div class="donor-info">
                <h3>${name}</h3>
                <div class="donor-meta">
                    <div class="meta-item">
                        <i class="fa-solid fa-location-dot"></i>
                        <span>${donor.city || 'Location N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fa-solid fa-clock"></i>
                        <span>Last Donation: ${donor.last_donation_date || 'None'}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fa-solid fa-star"></i>
                        <span>Response Rate: ${donor.response_rate || 0}%</span>
                    </div>
                </div>
                <div class="donor-status ${availabilityClass}">${availabilityText}</div>
                <a href="tel:${phone}" class="contact-donor-btn">
                    <i class="fa-solid fa-phone"></i> Contact Donor
                </a>
            </div>
        `;
        container.appendChild(card);
    });
}

function applyFilters() {
    const bloodGroup = document.getElementById('bloodGroupFilter').value;
    const city = document.getElementById('cityFilter').value;

    const filters = {};
    if (bloodGroup) filters.blood_group = bloodGroup;
    if (city) filters.city = city;

    loadDonors(filters);
}
