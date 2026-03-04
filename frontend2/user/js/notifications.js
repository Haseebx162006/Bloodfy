/**
 * User Notifications Script
 * Handles fetching, displaying and marking notifications as read
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch
    fetchNotifications();

    // Event Listeners
    const markAllReadBtn = document.getElementById('markAllRead');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', () => markAllAsRead());
    }

    // Set body as loaded
    document.body.classList.add('loaded');
});

async function fetchNotifications() {
    const listContainer = document.getElementById('notificationsList');
    if (!listContainer) return;

    try {
        const response = await API.notifications.getAppNotifications();

        if (response.success && response.data) {
            const notifications = response.data.notifications || [];

            if (notifications.length === 0) {
                listContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-bell-slash"></i>
                        <p>No notifications yet.</p>
                    </div>
                `;
                return;
            }

            renderNotifications(notifications, listContainer);
        } else {
            listContainer.innerHTML = `<div class="empty-state"><p>${response.message || 'Failed to load notifications'}</p></div>`;
        }
    } catch (error) {
        console.error('Error fetching notifications:', error);
        listContainer.innerHTML = `<div class="empty-state"><p>Error: ${error.message || 'Failed to connect to server'}</p></div>`;
    }
}

function renderNotifications(notifications, container) {
    container.innerHTML = '';

    notifications.forEach(notif => {
        const card = document.createElement('div');
        card.className = `notification-card ${notif.is_read ? '' : 'unread'}`;
        card.dataset.id = notif.id;

        const iconClass = getIconClass(notif.notification_type);
        const typeClass = `icon-${notif.notification_type || 'info'}`;
        const timeStr = formatTime(notif.created_at);

        card.innerHTML = `
            <div class="notification-icon ${typeClass}">
                <i class="fa-solid ${iconClass}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">
                    <span>${notif.title}</span>
                    <span class="notification-time">${timeStr}</span>
                </div>
                <p class="notification-message">${notif.message}</p>
                ${!notif.is_read ? `<button class="mark-read-btn" onclick="markAsRead('${notif.id}')">Mark as read</button>` : ''}
            </div>
        `;
        container.appendChild(card);
    });
}

function getIconClass(type) {
    switch (type) {
        case 'success': return 'fa-circle-check';
        case 'warning': return 'fa-triangle-exclamation';
        case 'danger': return 'fa-circle-xmark';
        case 'blood_request': return 'fa-droplet';
        case 'donor_approval': return 'fa-user-check';
        default: return 'fa-circle-info';
    }
}

function formatTime(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString();
}

// Global functions for inline event handlers
window.markAsRead = async function (notificationId) {
    try {
        const response = await API.notifications.markAppAsRead(notificationId);
        if (response.success) {
            const card = document.querySelector(`.notification-card[data-id="${notificationId}"]`);
            if (card) {
                card.classList.remove('unread');
                const btn = card.querySelector('.mark-read-btn');
                if (btn) btn.remove();
            }
        }
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
};

async function markAllAsRead() {
    try {
        const response = await API.notifications.markAppAsRead();
        if (response.success) {
            const unreadCards = document.querySelectorAll('.notification-card.unread');
            unreadCards.forEach(card => {
                card.classList.remove('unread');
                const btn = card.querySelector('.mark-read-btn');
                if (btn) btn.remove();
            });
        }
    } catch (error) {
        console.error('Error marking all notifications as read:', error);
    }
}
