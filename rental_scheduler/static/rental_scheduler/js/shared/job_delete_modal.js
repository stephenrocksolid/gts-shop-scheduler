/**
 * GTS Job Delete Modal Module
 * 
 * Provides modal-based job deletion with recurring scope support.
 * Intercepts delete link clicks to show an in-page modal instead of navigating.
 * Works on both the calendar search results and the jobs list page.
 * 
 * Requires: GTS.urls, GTS.csrf, window.showToast, GTS.initOnce
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    // =========================================================================
    // MODAL HTML TEMPLATES
    // =========================================================================

    /**
     * Build the modal HTML for delete confirmation.
     * Matches the styling of job_confirm_delete.html.
     * 
     * @param {Object} jobInfo - Job information from row data attributes
     * @returns {string} HTML string for the modal
     */
    function buildModalHTML(jobInfo) {
        var isRecurring = jobInfo.isRecurringParent || jobInfo.isRecurringInstance;
        var isParent = jobInfo.isRecurringParent;

        var scopePickerHTML = '';
        if (isRecurring) {
            scopePickerHTML = '\n' +
                '<div class="mb-6">\n' +
                '    <label class="block text-sm font-medium text-gray-700 mb-3">Delete scope:</label>\n' +
                '    <div class="space-y-2">\n' +
                (isParent ? '' :
                '        <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">\n' +
                '            <input type="radio" name="delete_scope" value="this_only" checked class="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300">\n' +
                '            <span class="ml-3">\n' +
                '                <span class="block text-sm font-medium text-gray-900">Delete only this event</span>\n' +
                '                <span class="block text-xs text-gray-500">Other events in the series will remain</span>\n' +
                '            </span>\n' +
                '        </label>\n') +
                '        <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">\n' +
                '            <input type="radio" name="delete_scope" value="this_and_future" ' + (isParent ? 'checked' : '') + ' class="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300">\n' +
                '            <span class="ml-3">\n' +
                '                <span class="block text-sm font-medium text-gray-900">Delete this and all future events</span>\n' +
                '                <span class="block text-xs text-gray-500">Past events in the series will remain</span>\n' +
                '            </span>\n' +
                '        </label>\n' +
                '        <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">\n' +
                '            <input type="radio" name="delete_scope" value="all" class="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300">\n' +
                '            <span class="ml-3">\n' +
                '                <span class="block text-sm font-medium text-gray-900">Delete entire series</span>\n' +
                '                <span class="block text-xs text-gray-500">All events in this series will be deleted</span>\n' +
                '            </span>\n' +
                '        </label>\n' +
                '    </div>\n' +
                '</div>\n';
        }

        return '' +
            '<div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" data-modal-backdrop></div>\n' +
            '<div class="fixed inset-0 z-10 overflow-y-auto">\n' +
            '    <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">\n' +
            '        <div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg" data-modal-content>\n' +
            '            <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">\n' +
            '                <div class="sm:flex sm:items-start">\n' +
            '                    <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">\n' +
            '                        <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">\n' +
            '                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>\n' +
            '                        </svg>\n' +
            '                    </div>\n' +
            '                    <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left flex-1">\n' +
            '                        <h3 class="text-lg font-semibold leading-6 text-gray-900">Delete Job</h3>\n' +
            '                        <div class="mt-2">\n' +
            '                            <p class="text-sm text-gray-500">Are you sure you want to delete this job?</p>\n' +
            '                        </div>\n' +
            '                    </div>\n' +
            '                </div>\n' +
            '\n' +
            '                <div class="mt-4 bg-gray-50 rounded-lg p-4">\n' +
            '                    <h4 class="text-sm font-medium text-gray-900 mb-2">Job Details</h4>\n' +
            '                    <div class="text-sm text-gray-600 space-y-1">\n' +
            '                        <p><strong>Customer:</strong> ' + escapeHtml(jobInfo.displayName) + '</p>\n' +
            (jobInfo.phone ? '                        <p><strong>Phone:</strong> ' + escapeHtml(jobInfo.phone) + '</p>\n' : '') +
            '                        <p><strong>Start:</strong> ' + escapeHtml(jobInfo.start) + '</p>\n' +
            '                        <p><strong>End:</strong> ' + escapeHtml(jobInfo.end) + '</p>\n' +
            '                        <p><strong>Calendar:</strong> ' + escapeHtml(jobInfo.calendar) + '</p>\n' +
            (isRecurring ? '                        <p><strong>Type:</strong> <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">Recurring ' + (isParent ? 'Series' : 'Instance') + '</span></p>\n' : '') +
            '                    </div>\n' +
            '                </div>\n' +
            '\n' +
            scopePickerHTML +
            '\n' +
            '                <div class="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3">\n' +
            '                    <div class="flex">\n' +
            '                        <div class="flex-shrink-0">\n' +
            '                            <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">\n' +
            '                                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>\n' +
            '                            </svg>\n' +
            '                        </div>\n' +
            '                        <div class="ml-3">\n' +
            '                            <p class="text-sm text-yellow-700">This action cannot be undone.</p>\n' +
            '                        </div>\n' +
            '                    </div>\n' +
            '                </div>\n' +
            '            </div>\n' +
            '            <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">\n' +
            '                <button type="button" data-modal-confirm class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto">\n' +
            '                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">\n' +
            '                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>\n' +
            '                    </svg>\n' +
            '                    Delete Job\n' +
            '                </button>\n' +
            '                <button type="button" data-modal-cancel class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto">\n' +
            '                    Cancel\n' +
            '                </button>\n' +
            '            </div>\n' +
            '        </div>\n' +
            '    </div>\n' +
            '</div>';
    }

    /**
     * Simple HTML escape utility.
     */
    function escapeHtml(text) {
        if (!text) return '';
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // =========================================================================
    // MODAL LIFECYCLE
    // =========================================================================

    /**
     * Show the delete confirmation modal.
     * 
     * @param {Object} jobInfo - Job information extracted from row
     * @param {Function} onConfirm - Callback when delete is confirmed, receives scope
     */
    function showModal(jobInfo, onConfirm) {
        var modalRoot = document.getElementById('gts-modal-root');
        if (!modalRoot) {
            console.error('[GTS.jobDeleteModal] Modal root #gts-modal-root not found');
            return;
        }

        // Clear and populate modal
        modalRoot.innerHTML = buildModalHTML(jobInfo);
        modalRoot.classList.remove('hidden');

        // Prevent body scroll while modal is open
        document.body.style.overflow = 'hidden';

        // Get references
        var confirmBtn = modalRoot.querySelector('[data-modal-confirm]');
        var cancelBtn = modalRoot.querySelector('[data-modal-cancel]');
        var backdrop = modalRoot.querySelector('[data-modal-backdrop]');

        function closeModal() {
            modalRoot.classList.add('hidden');
            modalRoot.innerHTML = '';
            document.body.style.overflow = '';
        }

        function handleConfirm() {
            // Get selected scope (default to 'this_only' for non-recurring)
            var scopeInput = modalRoot.querySelector('input[name="delete_scope"]:checked');
            var scope = scopeInput ? scopeInput.value : null;

            // Disable button and show loading state
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '' +
                '<svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">' +
                '    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>' +
                '    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>' +
                '</svg>' +
                'Deleting...';

            onConfirm(scope, function(success) {
                if (success) {
                    closeModal();
                } else {
                    // Re-enable button on error
                    confirmBtn.disabled = false;
                    confirmBtn.innerHTML = '' +
                        '<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
                        '    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>' +
                        '</svg>' +
                        'Delete Job';
                }
            });
        }

        // Attach event listeners
        if (confirmBtn) {
            confirmBtn.addEventListener('click', handleConfirm);
        }
        if (cancelBtn) {
            cancelBtn.addEventListener('click', closeModal);
        }
        if (backdrop) {
            backdrop.addEventListener('click', closeModal);
        }

        // Close on Escape key
        function handleEscape(e) {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscape);
            }
        }
        document.addEventListener('keydown', handleEscape);
    }

    // =========================================================================
    // DELETE API CALLS
    // =========================================================================

    /**
     * Perform the delete API call.
     * 
     * @param {string|number} jobId
     * @param {Object} jobInfo - Job info with recurrence flags
     * @param {string|null} scope - Delete scope for recurring jobs
     * @param {Function} callback - Called with (success: boolean)
     */
    function performDelete(jobId, jobInfo, scope, callback) {
        var isRecurring = jobInfo.isRecurringParent || jobInfo.isRecurringInstance;
        var url;
        var body = {};

        if (isRecurring && scope) {
            url = GTS.urls.jobDeleteRecurring(jobId);
            body = { delete_scope: scope };
        } else {
            url = GTS.urls.jobDelete(jobId);
        }

        var csrfToken = GTS.csrf ? GTS.csrf.getToken() : window.getCookie('csrftoken');

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(body)
        })
        .then(function(response) {
            if (!response.ok) {
                return response.json().then(function(data) {
                    throw new Error(data.error || 'Delete failed');
                });
            }
            return response.json();
        })
        .then(function(data) {
            if (data.success) {
                if (window.showToast) {
                    var message = 'Job deleted successfully';
                    if (data.deleted_count && data.deleted_count > 1) {
                        message = data.deleted_count + ' jobs deleted successfully';
                    }
                    window.showToast(message, 'success');
                }
                // Refresh the results
                refreshResults();
                callback(true);
            } else {
                throw new Error(data.error || 'Delete failed');
            }
        })
        .catch(function(error) {
            console.error('[GTS.jobDeleteModal] Delete error:', error);
            if (window.showToast) {
                window.showToast(error.message || 'Failed to delete job', 'error');
            }
            callback(false);
        });
    }

    // =========================================================================
    // RESULT REFRESH LOGIC
    // =========================================================================

    /**
     * Refresh the results after a successful delete.
     * Detects which page we're on and uses the appropriate refresh mechanism.
     */
    function refreshResults() {
        // Check if we're on the calendar page with search panel
        var calendarSearchForm = document.getElementById('calendar-search-form');
        if (calendarSearchForm) {
            // Re-submit the search form to refresh results
            var submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            calendarSearchForm.dispatchEvent(submitEvent);
            return;
        }

        // Check if we're on the jobs list page
        var jobTableContainer = document.getElementById('job-table-container');
        if (jobTableContainer) {
            // Fetch the table partial with current query params and replace container
            var url = GTS.urls.jobListTablePartial + window.location.search;
            
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function(response) {
                if (!response.ok) throw new Error('Failed to refresh');
                return response.text();
            })
            .then(function(html) {
                jobTableContainer.innerHTML = html;
                // Process HTMX attributes so load-more continues to work
                if (window.htmx && typeof window.htmx.process === 'function') {
                    window.htmx.process(jobTableContainer);
                }
            })
            .catch(function(error) {
                console.error('[GTS.jobDeleteModal] Refresh error:', error);
                // Fallback: reload the page
                window.location.reload();
            });
            return;
        }

        // Fallback: reload page
        window.location.reload();
    }

    // =========================================================================
    // CLICK HANDLER & INITIALIZATION
    // =========================================================================

    /**
     * Extract job info from a job row element.
     * 
     * @param {HTMLElement} row - The .job-row element
     * @returns {Object} Job info object
     */
    function extractJobInfo(row) {
        return {
            id: row.getAttribute('data-job-id'),
            displayName: row.getAttribute('data-job-display-name') || 'Unknown',
            phone: row.getAttribute('data-job-phone') || '',
            start: row.getAttribute('data-job-start') || '',
            end: row.getAttribute('data-job-end') || '',
            calendar: row.getAttribute('data-job-calendar') || '',
            isRecurringParent: row.hasAttribute('data-is-recurring-parent'),
            isRecurringInstance: row.hasAttribute('data-is-recurring-instance')
        };
    }

    /**
     * Handle click on delete action links.
     */
    function handleDeleteClick(e) {
        var link = e.target.closest('[data-gts-action="job-delete"]');
        if (!link) return;

        // Prevent navigation
        e.preventDefault();
        e.stopPropagation();

        // Find the parent job row
        var row = link.closest('.job-row');
        if (!row) {
            console.error('[GTS.jobDeleteModal] Could not find parent .job-row');
            return;
        }

        // Extract job info
        var jobInfo = extractJobInfo(row);
        if (!jobInfo.id) {
            console.error('[GTS.jobDeleteModal] Could not extract job ID');
            return;
        }

        // Show the modal
        showModal(jobInfo, function(scope, done) {
            performDelete(jobInfo.id, jobInfo, scope, done);
        });
    }

    /**
     * Initialize the delete modal handler.
     * Uses delegation on document.body to handle dynamically loaded content.
     */
    function init() {
        GTS.onDomReady(function() {
            GTS.initOnce('job_delete_modal', function() {
                // Single delegated click handler on body
                document.body.addEventListener('click', handleDeleteClick);
            });
        });
    }

    // Auto-initialize
    init();

    // Expose public API for programmatic use
    GTS.jobDeleteModal = {
        show: showModal,
        refresh: refreshResults
    };

})();

