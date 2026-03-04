/**
 * Emergency Search Integration Script
 * Handles emergency donor search and display
 */

document.addEventListener('DOMContentLoaded', () => {
    // =============================================================================
    // Emergency Search Form
    // =============================================================================

    const searchForm = document.getElementById('emergencySearchForm');
    const resultsSection = document.querySelector('.results-section');

    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Get form values
            const bloodGroupSelect = document.getElementById('emergencyBloodGroup');
            const locationInput = document.getElementById('emergencyLocation');

            const bloodGroup = bloodGroupSelect.value.trim();
            const location = locationInput.value.trim();

            // Validate
            if (!bloodGroup || !location) {
                showError('Please select a blood group and enter a location');
                return;
            }

            // Get search button
            const searchButton = document.getElementById('btnSearchEmergency');

            // Show loading
            const originalButtonText = searchButton.innerHTML;
            searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
            searchButton.disabled = true;

            try {
                // Try to get user's current location for distance calculation
                let userLat = null;
                let userLon = null;
                let locationMethod = 'city-based';

                try {
                    // Show location detection message
                    showInfo('Detecting your location...');

                    const position = await new Promise((resolve, reject) => {
                        if (!navigator.geolocation) {
                            reject(new Error('Geolocation not supported'));
                            return;
                        }

                        navigator.geolocation.getCurrentPosition(
                            resolve,
                            reject,
                            {
                                enableHighAccuracy: true,
                                timeout: 10000,
                                maximumAge: 300000 // 5 minutes
                            }
                        );
                    });

                    userLat = position.coords.latitude;
                    userLon = position.coords.longitude;
                    locationMethod = 'location-based';

                    console.log(`✓ User location detected: ${userLat}, ${userLon}`);
                    showSuccess('Using your current location for accurate distance calculation');

                } catch (geoError) {
                    console.warn('Geolocation failed:', geoError.message);

                    if (geoError.code === 1) { // PERMISSION_DENIED
                        showInfo('Location access denied. Using city-based search.');
                    } else if (geoError.code === 2) { // POSITION_UNAVAILABLE
                        showInfo('Location unavailable. Using city-based search.');
                    } else if (geoError.code === 3) { // TIMEOUT
                        showInfo('Location timeout. Using city-based search.');
                    } else {
                        showInfo('Using city-based search.');
                    }
                }

                // Build query parameters
                const params = new URLSearchParams({
                    blood_group: bloodGroup,
                    location: location
                });

                if (userLat && userLon) {
                    params.append('latitude', userLat);
                    params.append('longitude', userLon);
                }

                // Call emergency search API
                const response = await fetch(
                    `${API_CONFIG.BASE_URL}/donors/emergency/search/?${params.toString()}`,
                    {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('bloodify_auth_token')}`,
                            'Content-Type': 'application/json'
                        }
                    }
                );

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.message || 'Search failed');
                }

                if (result.success && result.data) {
                    displaySearchResults(result.data, bloodGroup, location, locationMethod);
                } else {
                    throw new Error('Invalid response from server');
                }

                // Reset button
                searchButton.innerHTML = originalButtonText;
                searchButton.disabled = false;

            } catch (error) {
                console.error('Emergency search error:', error);
                showError(error.message || 'Search failed. Please try again.');

                // Reset button
                searchButton.innerHTML = originalButtonText;
                searchButton.disabled = false;
            }
        });
    }

    // =============================================================================
    // Display Search Results
    // =============================================================================

    function displaySearchResults(data, bloodGroup, location, locationMethod = 'city-based') {
        if (!resultsSection) return;

        // Update results header
        const resultsHeader = resultsSection.querySelector('.results-header span');
        if (resultsHeader) {
            const matchCount = data.donors?.length || 0;
            const locationIcon = locationMethod === 'location-based'
                ? '<i class="fa-solid fa-location-crosshairs" style="color: #4CAF50;"></i>'
                : '<i class="fa-solid fa-map-marker-alt"></i>';

            const locationText = locationMethod === 'location-based'
                ? 'Using your current location'
                : 'City-based search';

            resultsHeader.innerHTML = `
                ${matchCount} Match${matchCount !== 1 ? 'es' : ''} Found for <strong>${bloodGroup}</strong> in <strong>${location}</strong>
                <br>
                <small style="color: var(--text-secondary); font-size: 0.85rem;">
                    ${locationIcon} ${locationText}
                </small>
            `;
        }

        // Find or create results container
        let resultsContainer = resultsSection.querySelector('.results-container');
        if (!resultsContainer) {
            resultsContainer = document.createElement('div');
            resultsContainer.className = 'results-container';
            resultsSection.appendChild(resultsContainer);
        }

        // Clear existing results
        resultsContainer.innerHTML = '';

        const donors = data.donors || [];

        if (donors.length === 0) {
            const noResultsMessage = document.createElement('div');
            noResultsMessage.style.cssText = 'text-align: center; padding: 40px; color: var(--text-secondary);';
            noResultsMessage.innerHTML = `
                <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 20px; opacity: 0.3;"></i>
                <p>No donors found matching your criteria.</p>
                <p style="font-size: 0.9rem;">Try expanding your search area or contact the blood bank.</p>
            `;
            resultsContainer.appendChild(noResultsMessage);
            return;
        }

        // Create cards for each donor
        donors.forEach((donor, index) => {
            // Get initials for avatar
            const name = donor.name || 'Unknown';
            const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
            const distance = donor.distance || 0;
            const city = donor.city || 'Unknown';

            // Determine what to show in the badge
            let badgeContent;
            if (distance > 0) {
                badgeContent = `<i class="fa-solid fa-route"></i> ${distance.toFixed(1)} km away`;
            } else {
                badgeContent = `<i class="fa-solid fa-location-dot"></i> ${city}`;
            }

            // Create card
            const card = document.createElement('div');
            card.className = 'donor-result-card';
            card.style.animation = `fadeIn 0.5s ease ${index * 0.1}s both`;

            card.innerHTML = `
                <div class="donor-info">
                    <div class="donor-avatar">${initials}</div>
                    <div>
                        <h4 style="font-size: 1.1rem;">${name}</h4>
                        <span class="dist-badge">
                            ${badgeContent}
                        </span>
                    </div>
                </div>
                <div class="action-btns">
                    <button class="btn-icon btn-sms" title="Send SMS" data-donor-id="${donor.id}" data-donor-name="${name}" data-action="sms">
                        <i class="fa-solid fa-comment-sms"></i>
                    </button>
                    <button class="btn-icon btn-call" title="Call Now" data-donor-id="${donor.id}" data-donor-name="${name}" data-phone="${donor.phone_number || ''}" data-action="call">
                        <i class="fa-solid fa-phone"></i>
                    </button>
                </div>
            `;

            resultsContainer.appendChild(card);
        });

        // Attach event listeners to action buttons
        attachActionListeners();
    }

    // =============================================================================
    // Attach Action Listeners
    // =============================================================================

    function attachActionListeners() {
        const actionButtons = document.querySelectorAll('.action-btns button');

        actionButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                const donorId = button.dataset.donorId;
                const donorName = button.dataset.donorName;
                const action = button.dataset.action;
                const phone = button.dataset.phone;

                if (action === 'call') {
                    handleCall(phone, donorName);
                } else if (action === 'sms') {
                    await handleSMS(donorId, donorName);
                }
            });
        });
    }

    // =============================================================================
    // Handle Call Action
    // =============================================================================

    function handleCall(phoneNumber, donorName) {
        if (!phoneNumber) {
            showError('Phone number not available for this donor');
            return;
        }

        // Show phone number card
        showPhoneNumberCard(donorName, phoneNumber, 'CALL');
    }

    // =============================================================================
    // Handle SMS Action
    // =============================================================================

    async function handleSMS(donorId, donorName) {
        // First, get the donor's phone number from the button
        const button = document.querySelector(`[data-donor-id="${donorId}"][data-action="sms"]`);
        const phoneNumber = button?.closest('.donor-result-card')?.querySelector('[data-action="call"]')?.dataset.phone;

        if (!phoneNumber) {
            showError('Phone number not available for this donor');
            return;
        }

        // Show phone number card
        showPhoneNumberCard(donorName, phoneNumber, 'SMS');
    }

    // =============================================================================
    // Show Phone Number Card
    // =============================================================================

    function showPhoneNumberCard(donorName, phoneNumber, contactType) {
        // Remove existing modal if any
        const existingModal = document.querySelector('.phone-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'phone-modal';
        modal.innerHTML = `
            <div class="phone-modal-overlay"></div>
            <div class="phone-modal-content">
                <div class="phone-modal-header">
                    <h3>
                        <i class="fa-solid fa-${contactType === 'CALL' ? 'phone' : 'comment-sms'}"></i>
                        Contact Donor
                    </h3>
                    <button class="phone-modal-close" onclick="closePhoneModal()">
                        <i class="fa-solid fa-times"></i>
                    </button>
                </div>
                <div class="phone-modal-body">
                    <div class="donor-name-display">
                        <i class="fa-solid fa-user-circle"></i>
                        <span>${donorName}</span>
                    </div>
                    <div class="phone-number-display">
                        <i class="fa-solid fa-phone"></i>
                        <span class="phone-number">${phoneNumber}</span>
                        <button class="copy-btn" onclick="copyPhoneNumber('${phoneNumber}')" title="Copy number">
                            <i class="fa-solid fa-copy"></i>
                        </button>
                    </div>
                    <p class="contact-note">
                        ${contactType === 'CALL'
                ? 'Click the button below to initiate a call to this donor.'
                : 'Click the button below to send an SMS to this donor.'}
                    </p>
                </div>
                <div class="phone-modal-footer">
                    <button class="btn-cancel" onclick="closePhoneModal()">Cancel</button>
                    <button class="btn-contact" onclick="proceedWithContact('${phoneNumber}', '${contactType}')">
                        <i class="fa-solid fa-${contactType === 'CALL' ? 'phone' : 'comment-sms'}"></i>
                        ${contactType === 'CALL' ? 'Call Now' : 'Send SMS'}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Animate in
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);

        // Close on overlay click
        modal.querySelector('.phone-modal-overlay').addEventListener('click', closePhoneModal);
    }

    // =============================================================================
    // Close Phone Modal
    // =============================================================================

    window.closePhoneModal = function () {
        const modal = document.querySelector('.phone-modal');
        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    };

    // =============================================================================
    // Copy Phone Number
    // =============================================================================

    window.copyPhoneNumber = function (phoneNumber) {
        navigator.clipboard.writeText(phoneNumber).then(() => {
            showSuccess('Phone number copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = phoneNumber;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showSuccess('Phone number copied to clipboard!');
        });
    };

    // =============================================================================
    // Proceed with Contact
    // =============================================================================

    window.proceedWithContact = function (phoneNumber, contactType) {
        closePhoneModal();

        if (contactType === 'CALL') {
            // Initiate phone call
            window.location.href = `tel:${phoneNumber}`;
        } else {
            // Initiate SMS
            window.location.href = `sms:${phoneNumber}`;
        }
    };

    // =============================================================================
    // Utility Functions
    // =============================================================================

    function showSuccess(message) {
        showToast(message, 'success');
    }

    function showError(message) {
        showToast(message, 'error');
    }

    function showInfo(message) {
        showToast(message, 'info');
    }

    function showToast(message, type = 'info') {
        // Remove existing toast of same type
        const existingToast = document.querySelector(`.emergency-toast-${type}`);
        if (existingToast) {
            existingToast.remove();
        }

        // Create toast
        const toast = document.createElement('div');
        toast.className = `emergency-toast emergency-toast-${type}`;

        const colors = {
            success: { bg: '#388E3C', icon: 'check-circle' },
            error: { bg: '#D32F2F', icon: 'exclamation-circle' },
            info: { bg: '#1976D2', icon: 'info-circle' }
        };

        const color = colors[type] || colors.info;

        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${color.bg};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
        `;

        toast.innerHTML = `
            <i class="fa-solid fa-${color.icon}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        // Auto hide
        const duration = type === 'error' ? 5000 : type === 'success' ? 4000 : 3000;
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
});

// Add fadeIn animation and modal styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    .results-container {
        margin-top: 20px;
    }

    /* Phone Number Modal */
    .phone-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .phone-modal.active {
        opacity: 1;
    }

    .phone-modal-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
    }

    .phone-modal-content {
        position: relative;
        background: rgba(30, 30, 30, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 82, 82, 0.3);
        border-radius: 16px;
        width: 90%;
        max-width: 450px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        animation: slideUp 0.3s ease;
    }

    @keyframes slideUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }

    .phone-modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 25px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .phone-modal-header h3 {
        margin: 0;
        font-size: 1.3rem;
        color: #FF5252;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .phone-modal-close {
        background: none;
        border: none;
        color: #94A3B8;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 5px;
        transition: color 0.3s;
    }

    .phone-modal-close:hover {
        color: #F1F5F9;
    }

    .phone-modal-body {
        padding: 25px;
    }

    .donor-name-display {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        color: #F1F5F9;
        font-size: 1.1rem;
    }

    .donor-name-display i {
        font-size: 1.5rem;
        color: #FF5252;
    }

    .phone-number-display {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 18px;
        background: rgba(41, 98, 255, 0.1);
        border: 2px solid rgba(41, 98, 255, 0.3);
        border-radius: 10px;
        margin-bottom: 20px;
    }

    .phone-number-display i {
        font-size: 1.3rem;
        color: #2962FF;
    }

    .phone-number {
        flex: 1;
        font-size: 1.3rem;
        font-weight: 600;
        color: #F1F5F9;
        letter-spacing: 1px;
    }

    .copy-btn {
        background: rgba(41, 98, 255, 0.2);
        border: 1px solid rgba(41, 98, 255, 0.4);
        color: #2962FF;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s;
        font-size: 1rem;
    }

    .copy-btn:hover {
        background: rgba(41, 98, 255, 0.3);
        transform: scale(1.05);
    }

    .contact-note {
        color: #94A3B8;
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
        text-align: center;
    }

    .phone-modal-footer {
        display: flex;
        gap: 12px;
        padding: 20px 25px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .btn-cancel {
        flex: 1;
        padding: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #F1F5F9;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s;
    }

    .btn-cancel:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    .btn-contact {
        flex: 1;
        padding: 12px;
        background: #D50000;
        border: none;
        color: white;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        transition: all 0.3s;
        box-shadow: 0 0 15px rgba(213, 0, 0, 0.3);
    }

    .btn-contact:hover {
        background: #FF1744;
        box-shadow: 0 0 25px rgba(255, 23, 68, 0.5);
        transform: translateY(-2px);
    }
`;
document.head.appendChild(style);

