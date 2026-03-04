/**
 * Donor Registration Script
 * Handles the registration form submission and UI states
 */

document.addEventListener('DOMContentLoaded', () => {
    const registrationForm = document.getElementById('donorRegistrationForm');
    const submitBtn = document.getElementById('submitBtn');
    const formView = document.getElementById('formView');
    const successView = document.getElementById('successView');

    if (registrationForm) {
        registrationForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Basic validation
            if (!validateForm()) return;

            // Prepare data
            const formData = new FormData(registrationForm);
            const donorData = {
                blood_group: formData.get('blood_group'),
                phone_number: formData.get('phone_number'),
                city: formData.get('city'),
                cnic: formData.get('cnic'),
                date_of_birth: formData.get('date_of_birth'),
                weight_kg: parseFloat(formData.get('weight_kg')),
                address: formData.get('address'),
                medical_history: formData.get('medical_history') || ''
            };

            try {
                // Show loading state
                setLoading(true);

                const response = await API.donors.register(donorData);

                if (response.success) {
                    // Show success view
                    formView.style.display = 'none';
                    successView.style.display = 'block';

                    // Update local user data if possible
                    updateLocalDonorStatus('DONOR_PENDING');

                    showToast('Application submitted successfully!', 'success');
                } else {
                    showToast(response.message || 'Failed to submit application', 'error');
                }
            } catch (error) {
                console.error('Registration error:', error);
                const errorMsg = error.message || 'An unexpected error occurred';
                showToast(errorMsg, 'error');

                if (error.errors) {
                    highlightFieldErrors(error.errors);
                }
            } finally {
                setLoading(false);
            }
        });
    }

    // Set body as loaded
    document.body.classList.add('loaded');
});

function validateForm() {
    const weight = document.getElementById('weight').value;
    const dob = document.getElementById('dob').value;
    const terms = document.getElementById('terms').checked;

    if (parseFloat(weight) < 45) {
        showToast('Weight must be at least 45kg to donate blood', 'error');
        return false;
    }

    if (!terms) {
        showToast('Please agree to the terms and conditions', 'error');
        return false;
    }

    // Age validation
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }

    if (age < 18) {
        showToast('You must be at least 18 years old to donate blood', 'error');
        return false;
    }

    return true;
}

function setLoading(isLoading) {
    const submitBtn = document.getElementById('submitBtn');
    if (isLoading) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
    } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-user-plus"></i> Submit Application';
    }
}

function updateLocalDonorStatus(status) {
    const userData = getUserData();
    if (userData) {
        userData.donor_status = status;
        setUserData(userData);
    }
}

function highlightFieldErrors(errors) {
    // Clear previous errors if any (form-specific highlight logic can go here)
    console.log('Field errors:', errors);
}

function showToast(message, type = 'info') {
    // Create toast if it doesn't exist
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }

    const icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-circle-exclamation' : 'fa-info-circle');

    toast.className = `toast ${type} show`;
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}
