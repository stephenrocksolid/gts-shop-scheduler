/**
 * SettingsHandlers - Manages settings form interactions and network path validation
 * Handles network path validation, connection testing, and UI state management
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare SettingsHandlers if it doesn't already exist
    if (typeof window.SettingsHandlers === 'undefined') {

        class SettingsHandlers {
            constructor(config = {}) {
                // Configuration and dependencies
                this.config = config;
                this.pathInput = null;
                this.networkStatus = null;
                this.validationStatus = null;
                this.validationIcon = null;
                this.validationText = null;
                this.validationError = null;
                this.networkCredentials = null;
                this.testConnectionButton = null;
                this.networkUsername = null;
                this.networkPassword = null;

                // State management
                this.isInitialized = false;
                this.isValidating = false;
                this.validationTimeout = null;

                // Initialize if dependencies are available
                this.initialize();
            }

            /**
             * Initialize the settings handlers module
             */
            initialize() {
                // Check for required dependencies
                if (!window.RentalConfig) {
                    window.Logger?.error('SettingsHandlers: RentalConfig is required but not available');
                    return;
                }

                if (!window.Logger) {
                    console.warn('SettingsHandlers: Logger not available, falling back to console logging');
                }

                // Initialize DOM elements
                this.initializeElements();

                if (!this.validateElements()) {
                    window.Logger?.error('SettingsHandlers: Required settings form elements not found');
                    return;
                }

                // Setup event listeners
                this.setupEventListeners();

                // Initial setup
                this.performInitialSetup();

                this.isInitialized = true;
                window.Logger?.debug('SettingsHandlers initialized successfully');
            }

            /**
             * Initialize DOM element references
             */
            initializeElements() {
                this.pathInput = document.getElementById('id_license_scan_path');
                this.networkStatus = document.getElementById('network-status');
                this.validationStatus = document.getElementById('validation-status');
                this.validationIcon = document.getElementById('validation-icon');
                this.validationText = document.getElementById('validation-text');
                this.validationError = document.getElementById('validation-error');
                this.networkCredentials = document.getElementById('network-credentials');
                this.testConnectionButton = document.getElementById('test-connection-button');
                this.networkUsername = document.getElementById('network_username');
                this.networkPassword = document.getElementById('network_password');
            }

            /**
             * Validate that required elements exist
             * @returns {boolean} True if all required elements are present
             */
            validateElements() {
                const required = {
                    pathInput: this.pathInput,
                    networkStatus: this.networkStatus,
                    validationStatus: this.validationStatus,
                    validationIcon: this.validationIcon,
                    validationText: this.validationText,
                    validationError: this.validationError,
                    networkCredentials: this.networkCredentials
                };

                const missing = Object.entries(required)
                    .filter(([name, element]) => !element)
                    .map(([name]) => name);

                if (missing.length > 0) {
                    window.Logger?.error('SettingsHandlers: Missing required elements', { missing });
                    return false;
                }

                return true;
            }

            /**
             * Setup all event listeners
             */
            setupEventListeners() {
                // Path input change handler with debouncing
                if (this.pathInput) {
                    this.pathInput.addEventListener('input', (e) => {
                        this.handlePathInputChange(e);
                    });
                }

                // Test connection button handler
                if (this.testConnectionButton) {
                    this.testConnectionButton.addEventListener('click', async (e) => {
                        await this.handleTestConnection(e);
                    });
                }

                window.Logger?.debug('SettingsHandlers: Event listeners setup complete');
            }

            /**
             * Handle path input change with debouncing
             * @param {Event} e - Input change event
             */
            handlePathInputChange(e) {
                const path = e.target.value;

                window.Logger?.debug('SettingsHandlers: Path input changed', { path });

                // Clear previous validation timeout
                if (this.validationTimeout) {
                    clearTimeout(this.validationTimeout);
                }

                // Update network credentials visibility immediately
                this.updateNetworkCredentialsVisibility(path);

                // Debounce validation
                const debounceDelay = window.RentalConfig?.timing?.debounceDelay || 300;
                this.validationTimeout = setTimeout(() => {
                    this.updatePathValidation(path);
                }, debounceDelay);
            }

            /**
             * Update network credentials section visibility
             * @param {string} path - Path to check
             */
            updateNetworkCredentialsVisibility(path) {
                if (!this.networkCredentials) return;

                const isNetworkPath = this.isNetworkPath(path);
                this.networkCredentials.classList.toggle('hidden', !isNetworkPath);

                window.Logger?.debug('SettingsHandlers: Network credentials visibility updated', {
                    path,
                    isNetworkPath,
                    isVisible: !isNetworkPath
                });
            }

            /**
             * Check if path is a network path
             * @param {string} path - Path to check
             * @returns {boolean} True if network path
             */
            isNetworkPath(path) {
                return path && (path.startsWith('\\\\') || path.startsWith('//'));
            }

            /**
             * Update path validation status
             * @param {string} path - Path to validate
             */
            async updatePathValidation(path) {
                if (this.isValidating) {
                    window.Logger?.debug('SettingsHandlers: Validation already in progress, skipping');
                    return;
                }

                window.Logger?.debug('SettingsHandlers: Starting path validation', { path });

                // Clear validation if no path
                if (!path) {
                    this.clearValidationStatus();
                    return;
                }

                this.isValidating = true;

                try {
                    const isNetworkPath = this.isNetworkPath(path);

                    // Update network status visibility
                    if (this.networkStatus) {
                        this.networkStatus.classList.toggle('hidden', !isNetworkPath);
                    }

                    if (isNetworkPath) {
                        await this.validateNetworkPath(path);
                    } else {
                        // For local paths, just hide validation
                        this.hideValidationStatus();
                    }

                } catch (error) {
                    window.Logger?.error('SettingsHandlers: Error during path validation', error);
                    this.showValidationError('Validation Error', 'Failed to validate path, but you can still proceed with caution.');
                } finally {
                    this.isValidating = false;
                }
            }

            /**
             * Validate network path via API
             * @param {string} path - Network path to validate
             */
            async validateNetworkPath(path) {
                try {
                    window.Logger?.debug('SettingsHandlers: Validating network path', { path });

                    const response = await fetch(
                        `${window.RentalConfig.getApiUrl('validateNetworkPath')}?path=${encodeURIComponent(path)}`,
                        {
                            headers: window.RentalConfig.getApiHeaders()
                        }
                    );

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();

                    if (data.valid) {
                        this.showValidationSuccess('Valid Network Path');
                        window.Logger?.info('SettingsHandlers: Network path validation successful', { path });
                    } else {
                        const warningMessage = data.error || 'Network path may not be fully accessible';
                        this.showValidationWarning('Warning: ' + warningMessage, data.details);
                        window.Logger?.warn('SettingsHandlers: Network path validation warning', {
                            path,
                            error: data.error,
                            details: data.details
                        });
                    }

                } catch (error) {
                    window.Logger?.error('SettingsHandlers: Network path validation failed', error);
                    this.showValidationError('Validation Error', 'Failed to validate path, but you can still proceed with caution.');
                }
            }

            /**
             * Show successful validation status
             * @param {string} message - Success message
             */
            showValidationSuccess(message) {
                if (!this.validationStatus) return;

                this.validationStatus.classList.remove('hidden');

                if (this.validationIcon) {
                    this.validationIcon.innerHTML = `
                        <svg class="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                    `;
                }

                if (this.validationText) {
                    this.validationText.textContent = message;
                    this.validationText.classList.remove('text-red-600', 'text-yellow-600');
                    this.validationText.classList.add('text-green-600');
                }

                if (this.validationError) {
                    this.validationError.classList.add('hidden');
                }
            }

            /**
             * Show warning validation status
             * @param {string} message - Warning message
             * @param {string} details - Additional details
             */
            showValidationWarning(message, details = null) {
                if (!this.validationStatus) return;

                this.validationStatus.classList.remove('hidden');

                if (this.validationIcon) {
                    this.validationIcon.innerHTML = `
                        <svg class="h-4 w-4 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    `;
                }

                if (this.validationText) {
                    this.validationText.textContent = message;
                    this.validationText.classList.remove('text-green-600', 'text-red-600');
                    this.validationText.classList.add('text-yellow-600');
                }

                if (this.validationError) {
                    if (details) {
                        this.validationError.textContent = details;
                    } else {
                        this.validationError.textContent = 'You can proceed, but the path may not be accessible for license scanning.';
                    }
                    this.validationError.classList.remove('hidden');
                }
            }

            /**
             * Show error validation status
             * @param {string} message - Error message
             * @param {string} details - Additional details
             */
            showValidationError(message, details = null) {
                if (!this.validationStatus) return;

                this.validationStatus.classList.remove('hidden');

                if (this.validationIcon) {
                    this.validationIcon.innerHTML = `
                        <svg class="h-4 w-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    `;
                }

                if (this.validationText) {
                    this.validationText.textContent = message;
                    this.validationText.classList.remove('text-green-600', 'text-yellow-600');
                    this.validationText.classList.add('text-red-600');
                }

                if (this.validationError && details) {
                    this.validationError.textContent = details;
                    this.validationError.classList.remove('hidden');
                }
            }

            /**
             * Clear all validation status
             */
            clearValidationStatus() {
                if (this.networkStatus) {
                    this.networkStatus.classList.add('hidden');
                }
                this.hideValidationStatus();
            }

            /**
             * Hide validation status
             */
            hideValidationStatus() {
                if (this.validationStatus) {
                    this.validationStatus.classList.add('hidden');
                }
                if (this.validationError) {
                    this.validationError.classList.add('hidden');
                }
            }

            /**
             * Handle test connection button click
             * @param {Event} e - Click event
             */
            async handleTestConnection(e) {
                e.preventDefault();

                if (!this.pathInput || !this.networkUsername || !this.networkPassword) {
                    window.Logger?.error('SettingsHandlers: Missing required elements for connection test');
                    this.showAlert('Error: Missing required form elements.');
                    return;
                }

                const path = this.pathInput.value;
                const username = this.networkUsername.value;
                const password = this.networkPassword.value;

                // Validate inputs
                if (!path || !this.isNetworkPath(path)) {
                    this.showAlert('Please enter a valid network path first');
                    return;
                }

                window.Logger?.debug('SettingsHandlers: Testing network connection', { path, username });

                // Set loading state
                this.setTestButtonLoadingState(true);

                try {
                    const params = new URLSearchParams({
                        path: path,
                        username: username,
                        password: password
                    });

                    const response = await fetch(
                        `${window.RentalConfig.getApiUrl('testNetworkConnection')}?${params.toString()}`,
                        {
                            headers: window.RentalConfig.getApiHeaders()
                        }
                    );

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();

                    if (data.success) {
                        this.showAlert('Connection successful!');
                        // Refresh validation display
                        await this.updatePathValidation(path);
                        window.Logger?.info('SettingsHandlers: Network connection test successful', { path, username });
                    } else {
                        const errorMessage = data.error || 'Could not connect to network path';
                        this.showAlert(`Connection failed: ${errorMessage}`);
                        window.Logger?.warn('SettingsHandlers: Network connection test failed', {
                            path,
                            username,
                            error: errorMessage
                        });
                    }

                } catch (error) {
                    window.Logger?.error('SettingsHandlers: Error testing network connection', error);
                    this.showAlert('Error testing connection. Please try again.');
                } finally {
                    this.setTestButtonLoadingState(false);
                }
            }

            /**
             * Set test button loading state
             * @param {boolean} isLoading - Whether button should show loading state
             */
            setTestButtonLoadingState(isLoading) {
                if (!this.testConnectionButton) return;

                if (isLoading) {
                    this.testConnectionButton.dataset.originalText = this.testConnectionButton.textContent;
                    this.testConnectionButton.textContent = 'Testing...';
                    this.testConnectionButton.disabled = true;
                    window.Logger?.showLoading(this.testConnectionButton, 'Testing...');
                } else {
                    const originalText = this.testConnectionButton.dataset.originalText || 'Test Connection';
                    this.testConnectionButton.textContent = originalText;
                    this.testConnectionButton.disabled = false;
                    window.Logger?.hideLoading(this.testConnectionButton, originalText);
                }
            }

            /**
             * Show alert message to user
             * @param {string} message - Alert message
             */
            showAlert(message) {
                // Use native alert for now, could be enhanced with custom modal
                alert(message);
            }

            /**
             * Perform initial setup
             */
            performInitialSetup() {
                if (!this.pathInput) return;

                // Initial validation
                const initialPath = this.pathInput.value;
                if (initialPath) {
                    this.updatePathValidation(initialPath);
                    this.updateNetworkCredentialsVisibility(initialPath);
                }

                window.Logger?.info('SettingsHandlers: Initial setup completed', {
                    hasInitialPath: !!initialPath,
                    isNetworkPath: this.isNetworkPath(initialPath)
                });
            }

            /**
             * Cleanup method for removing event listeners and resetting state
             */
            destroy() {
                if (this.validationTimeout) {
                    clearTimeout(this.validationTimeout);
                }
                this.isInitialized = false;
                this.isValidating = false;
                window.Logger?.debug('SettingsHandlers: Destroyed');
            }
        }

        // Export SettingsHandlers class to global scope
        window.SettingsHandlers = SettingsHandlers;

        // Auto-initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function () {
            // Wait for dependencies to be available
            if (window.RentalConfig) {
                window.settingsHandlers = new SettingsHandlers();
            } else {
                // Wait a bit for dependencies to load
                setTimeout(() => {
                    if (window.RentalConfig) {
                        window.settingsHandlers = new SettingsHandlers();
                    } else {
                        console.error('SettingsHandlers: RentalConfig dependency not available');
                    }
                }, 100);
            }
        });

    } else {
        window.Logger?.debug('SettingsHandlers already exists, skipping initialization');
    }

})(); // End of IIFE 