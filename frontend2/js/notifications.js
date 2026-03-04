/**
 * Notifications Page Integration Script
 * Display and manage notification logs
 */

document.addEventListener('DOMContentLoaded', async () => {
    await initializeNotificationsPage();
});

// =============================================================================
// NOTIFICATIONS PAGE
// =============================================================================

async function initializeNotificationsPage() {
    console.log('Initializing notifications page...');

    // Load notifications list
    await loadNotifications();

    // Load statistics (if admin)
    const userData = getUserData();
    if (userData && userData.user_type === 'admin') {
        await loadNotificationStats();
    }

    // Setup filters
    setupNotificationFilters();

    // Setup send notification button (admin only)
    setupSendNotificationButton();
}

// =============================================================================
// LOAD NOTIFICATIONS
// =============================================================================

async function loadNotifications(filters = {}) {
    const container = document.querySelector('.notifications-list') ||
        document.querySelector('.notification-table tbody') ||
        document.querySelector('.table-body');

    if (!container) {
        console.warn('Notifications container not found');
        return;
    }

    showLoading(container);

    try {
        // Build query string
        const queryParams = new URLSearchParams();
        if (filters.type) queryParams.append('type', filters.type);
        if (filters.status) queryParams.append('status', filters.status);

        const endpoint = `/notifications/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        const result = await apiRequest(endpoint);

        if (result.success && result.data) {
            const notifications = result.data.notifications || [];

            if (notifications.length === 0) {
                container.innerHTML = '<tr><td colspan="6" style="text-align: center; padding:40px; color: var(--text-secondary);">No notifications found</td></tr>';
                return;
            }

            displayNotifications(notifications, container);
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        showError('Failed to load notifications', container);
    }
}

function displayNotifications(notifications, container) {
    container.innerHTML = '';

    notifications.forEach(notification => {
        const row = document.createElement('tr');
        row.className = 'notification-row';

        const recipientName = notification.donor?.user?.name ||
            notification.donor?.user?.first_name + ' ' + notification.donor?.user?.last_name ||
            'Unknown';

        const statusClasses = {
            'sent': 'status-sent',
            'delivered': 'status-delivered',
            'failed': 'status-failed',
            'pending': 'status-pending'
        };

        const typeClasses = {
            'sms': 'type-sms',
            'email': 'type-email',
            'both': 'type-both'
        };

        const status = notification.delivery_status || 'pending';
        const messageType = notification.message_type || 'sms';

        row.innerHTML = `
            <td>${formatDate(notification.created_at)}</td>
            <td>${recipientName}</td>
            <td><span class="type-badge ${typeClasses[messageType]}">${messageType.toUpperCase()}</span></td>
            <td class="message-content">${notification.message_content || notification.subject || 'N/A'}</td>
            <td><span class="status-badge ${statusClasses[status]}">${status.toUpperCase()}</span></td>
            <td>${notification.sent_at ? formatDate(notification.sent_at) : '-'}</td>
        `;

        container.appendChild(row);
    });
}

// =============================================================================
// NOTIFICATION STATS
// =============================================================================

async function loadNotificationStats() {
    try {
        const result = await apiRequest('/notifications/stats/');

        if (result.success && result.data) {
            displayNotificationStats(result.data);
        }
    } catch (error) {
        console.error('Error loading notification stats:', error);
    }
}

function displayNotificationStats(stats) {
    // Update stat cards if they exist
    const totalElement = document.getElementById('totalNotifications');
    if (totalElement) totalElement.textContent = stats.total_sent || 0;

    const deliveredElement = document.getElementById('totalDelivered');
    if (deliveredElement) deliveredElement.textContent = stats.total_delivered || 0;

    const failedElement = document.getElementById('totalFailed');
    if (failedElement) failedElement.textContent = stats.total_failed || 0;

    const deliveryRateElement = document.getElementById('deliveryRate');
    if (deliveryRateElement) deliveryRateElement.textContent = (stats.delivery_rate || 0) + '%';

    const responseRateElement = document.getElementById('responseRate');
    if (responseRateElement) responseRateElement.textContent = (stats.response_rate || 0) + '%';
}

// =============================================================================
// SEND NOTIFICATION (ADMIN)
// =============================================================================

function setupSendNotificationButton() {
    const sendBtn = document.getElementById('sendNotificationBtn') ||
        document.querySelector('.btn-send-notification');

    if (sendBtn) {
        sendBtn.addEventListener('click', () => {
            showSendNotificationModal();
        });
    }
}

function showSendNotificationModal() {
    let modal = document.getElementById('sendNotificationModal');

    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'sendNotificationModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Send Notification</h2>
                    <button class="modal-close" onclick="closeSendNotificationModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="sendNotificationForm">
                        <div class="form-group">
                            <label for="donorIdSelect">Select Donor *</label>
                            <select id="donorIdSelect" name="donor_id" class="form-input" required>
                                <option value="">Loading donors...</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="messageType">Message Type *</label>
                            <select id="messageType" name="message_type" class="form-input" required>
                                <option value="sms">SMS</option>
                                <option value="email">Email</option>
                                <option value="both">Both</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="subject">Subject</label>
                            <input type="text" id="subject" name="subject" class="form-input">
                        </div>
                        
                        <div class="form-group">
                            <label for="messageContent">Message *</label>
                            <textarea id="messageContent" name="message_content" class="form-input" rows="4" required></textarea>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="btn-secondary" onclick="closeSendNotificationModal()">Cancel</button>
                            <button type="submit" class="btn-primary">
                                <i class="fas fa-paper-plane"></i> Send Notification
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Load donors for the select dropdown
        loadDonorsForNotification();
    }

    modal.style.display = 'flex';

    // Setup form submission
    const form = document.getElementById('sendNotificationForm');
    form.onsubmit = async (e) => {
        e.preventDefault();
        await handleSendNotification(new FormData(form));
    };
}

window.closeSendNotificationModal = function () {
    const modal = document.getElementById('sendNotificationModal');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('sendNotificationForm')?.reset();
    }
};

async function loadDonorsForNotification() {
    try {
        const result = await API.donors.getList({ is_eligible: true });

        if (result.success && result.data) {
            const donors = Array.isArray(result.data) ? result.data : result.data.donors || [];
            const select = document.getElementById('donorIdSelect');

            if (select && donors.length > 0) {
                select.innerHTML = '<option value="">Select a donor</option>';
                donors.forEach(donor => {
                    const name = donor.user?.name || donor.user?.first_name + ' ' + donor.user?.last_name;
                    const option = document.createElement('option');
                    option.value = donor.id;
                    option.textContent = `${name} (${donor.blood_group})`;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading donors:', error);
    }
}

async function handleSendNotification(formData) {
    const notificationData = {
        donor_id: formData.get('donor_id'),
        message_type: formData.get('message_type'),
        message_content: formData.get('message_content'),
        subject: formData.get('subject') || undefined,
    };

    try {
        const result = await apiRequest('/notifications/send-manual/', {
            method: 'POST',
            body: notificationData,
        });

        if (result.success) {
            showSuccess('Notification sent successfully!');
            closeSendNotificationModal();
            await loadNotifications();
        }
    } catch (error) {
        console.error('Error sending notification:', error);
        showError(error.message || 'Failed to send notification');
    }
}

// =============================================================================
// FILTERS
// =============================================================================

function setupNotificationFilters() {
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');

    [typeFilter, statusFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', () => {
                applyNotificationFilters();
            });
        }
    });
}

function applyNotificationFilters() {
    const filters = {};

    const type = document.getElementById('typeFilter')?.value;
    if (type) filters.type = type;

    const status = document.getElementById('statusFilter')?.value;
    if (status) filters.status = status;

    loadNotifications(filters);
}
