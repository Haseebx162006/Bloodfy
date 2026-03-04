document.addEventListener('DOMContentLoaded', () => {
    // =============================================================================
    // Admin Login (admin-login.html)
    // =============================================================================
    const adminLoginForm = document.getElementById('loginFormElement');
    if (adminLoginForm && (window.location.pathname.includes('admin-login.html') || document.title.includes('Admin'))) {
        adminLoginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const emailInput = adminLoginForm.querySelector('input[type="email"]');
            const passwordInput = adminLoginForm.querySelector('input[type="password"]');
            const email = emailInput ? emailInput.value.trim() : '';
            const password = passwordInput ? passwordInput.value : '';

            if (!email || !password) {
                alert('Please enter both email and password.');
                return;
            }

            const submitBtn = adminLoginForm.querySelector('button[type="submit"]');
            const originalBtnContent = submitBtn.innerHTML;

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';

                const result = await API.auth.login(email, password);

                if (result.success) {
                    const user = getUserData();
                    const userType = user?.user_type || '';
                    const isStaff = user?.is_staff === true;
                    const isSuperuser = user?.is_superuser === true;

                    // Verify this is an admin user
                    if (userType === 'admin' || userType === 'ADMIN' || isStaff || isSuperuser) {
                        submitBtn.innerHTML = '<i class="fas fa-check"></i> Success';
                        submitBtn.style.background = '#00C853';
                        setTimeout(() => {
                            window.location.href = '../admin/pages/dashboard.html';
                        }, 800);
                    } else {
                        // Not an admin - clear auth and show error
                        clearAuthToken();
                        alert('Access denied. This login is for administrators only.');
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalBtnContent;
                    }
                }
            } catch (error) {
                console.error('Login error:', error);
                alert(error.message || 'Login failed. Please check your credentials.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnContent;
            }
        });
    }

    // =============================================================================
    // Public Login (user-login.html) - handled by inline script in HTML
    // This is a fallback only if auth.js is included in user-login.html
    // =============================================================================

    // =============================================================================
    // Donor Registration (index.html)
    // =============================================================================
    const registerForm = document.getElementById('registerFormElement');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(registerForm);

            // Map form data to backend expected fields
            const payload = {
                first_name: formData.get('first_name'),
                last_name: formData.get('last_name'),
                email: formData.get('email'),
                phone_number: formData.get('phone_number'),
                cnic: formData.get('cnic'),
                blood_group: formData.get('blood_group'),
                date_of_birth: formData.get('date_of_birth'),
                city: formData.get('city'),
                address: formData.get('address'),
                password: formData.get('password'),
                password_confirm: formData.get('password_confirm'),
                user_type: 'donor' // Public signup is always donor
            };

            const submitBtn = document.getElementById('registerBtn');
            const originalBtnContent = submitBtn.innerHTML;

            try {
                if (payload.password !== payload.password_confirm) {
                    throw new Error('Passwords do not match');
                }

                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering...';

                // Use the UNIFIED auth register endpoint
                const result = await API.auth.register(payload);

                if (result.success) {
                    alert('Registration successful! Please login with your credentials.');
                    registerForm.reset();
                    if (typeof showLoginForm === 'function') {
                        showLoginForm();
                    }
                }
            } catch (error) {
                console.error('Registration error:', error);
                let msg = error.message || 'Registration failed';
                if (error.errors) {
                    const firstError = Object.values(error.errors)[0];
                    msg = Array.isArray(firstError) ? firstError[0] : firstError;
                }
                alert(msg);
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnContent;
            }
        });
    }

    // =============================================================================
    // Check CNIC Feature (index.html - if exists)
    // =============================================================================

    const checkCnicForm = document.getElementById('checkForm');
    const recordResultContainer = document.getElementById('recordResult');

    if (checkCnicForm && recordResultContainer) {
        checkCnicForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const cnic = document.getElementById('checkCnic')?.value;

            if (!cnic) {
                showError('Please enter a CNIC number', recordResultContainer);
                return;
            }

            showLoading(recordResultContainer);

            try {
                // Search for donor by CNIC
                const result = await API.donors.getList({ cnic: cnic });

                if (result.success && result.data && result.data.length > 0) {
                    const donor = result.data[0];

                    recordResultContainer.innerHTML = `
                        <div class="record" style="
                            background: rgba(0, 200, 83, 0.1);
                            border: 1px solid #00C853;
                            padding: 20px;
                            border-radius: 10px;
                            color: var(--text-primary);
                        ">
                            <h3 style="margin-bottom: 15px; color: #00C853;">
                                <i class="fas fa-user-check"></i> Donor Found
                            </h3>
                            <p><strong>Name:</strong> ${donor.user?.name || 'N/A'}</p>
                            <p><strong>CNIC:</strong> ${donor.user?.cnic || 'N/A'}</p>
                            <p><strong>Blood Group:</strong> <span class="blood-type-tag">${donor.blood_group}</span></p>
                            <p><strong>Last Donation:</strong> ${formatDate(donor.last_donation_date)}</p>
                            <p><strong>Eligibility:</strong> ${donor.is_eligible ? '✅ Eligible' : '❌ Not Eligible (Cooldown)'}</p>
                        </div>
                    `;
                } else {
                    recordResultContainer.innerHTML = `
                        <p class="muted" style="color: var(--text-secondary); text-align: center; padding: 20px;">
                            <i class="fas fa-search"></i> No donor record found for CNIC: ${cnic}
                        </p>
                    `;
                }
            } catch (error) {
                showError(error.message || 'Error searching for donor', recordResultContainer);
            }
        });
    }
});
