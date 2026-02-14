/**
 * GTS URL Helper Module
 * 
 * Provides URL interpolation and convenience methods for config-driven URLs.
 * All URLs should come from window.GTS.urls (injected by Django templates),
 * never hard-coded in JS.
 * 
 * Requires: GTS namespace to exist (from config.js or base.html)
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    // URLs namespace - will be populated by Django template
    window.GTS.urls = window.GTS.urls || {};

    /**
     * Interpolate a URL template with the provided parameters.
     * 
     * @param {string} template - URL template with {param} placeholders
     * @param {Object} params - Key-value pairs to substitute
     * @returns {string} The interpolated URL
     * @throws {Error} If a required parameter is missing
     * 
     * @example
     * GTS.urls.interpolate('/api/jobs/{job_id}/detail/', { job_id: 123 })
     * // Returns: '/api/jobs/123/detail/'
     */
    GTS.urls.interpolate = function(template, params) {
        if (!template) {
            console.error('[GTS.urls] interpolate called with empty template');
            return '';
        }

        params = params || {};
        var result = template;

        // Find all {param} placeholders and replace them
        var placeholderRegex = /\{(\w+)\}/g;
        var match;
        var missing = [];

        // First pass: find all placeholders
        var placeholders = [];
        while ((match = placeholderRegex.exec(template)) !== null) {
            placeholders.push(match[1]);
        }

        // Second pass: replace placeholders with values
        placeholders.forEach(function(key) {
            if (params.hasOwnProperty(key) && params[key] != null) {
                result = result.replace(new RegExp('\\{' + key + '\\}', 'g'), params[key]);
            } else {
                missing.push(key);
            }
        });

        if (missing.length > 0) {
            console.error('[GTS.urls] Missing required params: ' + missing.join(', ') + ' for template: ' + template);
        }

        return result;
    };

    /**
     * Build a URL with query parameters.
     * 
     * @param {string} baseUrl - The base URL
     * @param {Object} queryParams - Query parameters to append
     * @returns {string} URL with query string
     * 
     * @example
     * GTS.urls.withQuery('/jobs/new/partial/', { edit: 123, date: '2025-01-01' })
     * // Returns: '/jobs/new/partial/?edit=123&date=2025-01-01'
     */
    GTS.urls.withQuery = function(baseUrl, queryParams) {
        if (!baseUrl) return '';
        if (!queryParams || Object.keys(queryParams).length === 0) return baseUrl;

        var params = new URLSearchParams();
        Object.keys(queryParams).forEach(function(key) {
            var value = queryParams[key];
            if (value != null && value !== '') {
                params.append(key, value);
            }
        });

        var queryString = params.toString();
        if (!queryString) return baseUrl;

        var separator = baseUrl.indexOf('?') >= 0 ? '&' : '?';
        return baseUrl + separator + queryString;
    };

    // =========================================================================
    // CONVENIENCE METHODS
    // These wrap common URL patterns for cleaner callsites
    // =========================================================================

    /**
     * Get job detail API URL
     * @param {string|number} jobId
     * @returns {string}
     */
    GTS.urls.jobDetailApi = function(jobId) {
        var template = GTS.urls.jobDetailApiTemplate;
        if (!template) {
            console.error('[GTS.urls] jobDetailApiTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { job_id: jobId });
    };

    /**
     * Get job update status API URL
     * @param {string|number} jobId
     * @returns {string}
     */
    GTS.urls.jobUpdateStatus = function(jobId) {
        var template = GTS.urls.jobUpdateStatusTemplate;
        if (!template) {
            console.error('[GTS.urls] jobUpdateStatusTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { job_id: jobId });
    };

    /**
     * Get job delete API URL
     * @param {string|number} jobId
     * @returns {string}
     */
    GTS.urls.jobDelete = function(jobId) {
        var template = GTS.urls.jobDeleteTemplate;
        if (!template) {
            console.error('[GTS.urls] jobDeleteTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { job_id: jobId });
    };

    /**
     * Get job delete recurring API URL
     * @param {string|number} jobId
     * @returns {string}
     */
    GTS.urls.jobDeleteRecurring = function(jobId) {
        var template = GTS.urls.jobDeleteRecurringTemplate;
        if (!template) {
            console.error('[GTS.urls] jobDeleteRecurringTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { job_id: jobId });
    };

    /**
     * Get job create/edit partial URL
     * @param {Object} [queryParams] - Optional query params (e.g. { edit: jobId } or { date: '2025-01-01' })
     * @returns {string}
     */
    GTS.urls.jobCreatePartial = function(queryParams) {
        var baseUrl = GTS.urls.jobCreatePartialBase;
        if (!baseUrl) {
            console.error('[GTS.urls] jobCreatePartialBase not configured');
            return '';
        }
        return GTS.urls.withQuery(baseUrl, queryParams);
    };

    /**
     * Get call reminder create partial URL
     * @param {Object} [queryParams] - Optional query params (e.g. { date: '2025-01-01', calendar: 1 })
     * @returns {string}
     */
    GTS.urls.callReminderCreatePartial = function(queryParams) {
        var baseUrl = GTS.urls.callReminderCreatePartialBase;
        if (!baseUrl) {
            console.error('[GTS.urls] callReminderCreatePartialBase not configured');
            return '';
        }
        return GTS.urls.withQuery(baseUrl, queryParams);
    };

    /**
     * Get call reminder update URL
     * @param {string|number} pk - Reminder ID
     * @returns {string}
     */
    GTS.urls.callReminderUpdate = function(pk) {
        var template = GTS.urls.callReminderUpdateTemplate;
        if (!template) {
            console.error('[GTS.urls] callReminderUpdateTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { pk: pk });
    };

    /**
     * Get call reminder delete URL
     * @param {string|number} pk - Reminder ID
     * @returns {string}
     */
    GTS.urls.callReminderDelete = function(pk) {
        var template = GTS.urls.callReminderDeleteTemplate;
        if (!template) {
            console.error('[GTS.urls] callReminderDeleteTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { pk: pk });
    };

    /**
     * Get job call reminder update URL
     * @param {string|number} jobId
     * @returns {string}
     */
    GTS.urls.jobCallReminderUpdate = function(jobId) {
        var template = GTS.urls.jobCallReminderUpdateTemplate;
        if (!template) {
            console.error('[GTS.urls] jobCallReminderUpdateTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { job_id: jobId });
    };

    /**
     * Get mark call reminder complete URL
     * @param {string|number} jobId
     * @returns {string}
     */
    GTS.urls.markCallReminderComplete = function(jobId) {
        var template = GTS.urls.markCallReminderCompleteTemplate;
        if (!template) {
            console.error('[GTS.urls] markCallReminderCompleteTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { job_id: jobId });
    };

    /**
     * Get job print URL
     * @param {string|number} jobId
     * @param {string} printType - 'wo', 'wo-customer', or 'invoice'
     * @returns {string}
     */
    GTS.urls.jobPrint = function(jobId, printType) {
        var templateMap = {
            'invoice': GTS.urls.jobPrintInvoiceTemplate
        };
        var template = templateMap[printType];
        if (!template) {
            console.error('[GTS.urls] Print template not configured for type: ' + printType);
            return '';
        }
        return GTS.urls.interpolate(template, { job_id: jobId });
    };

    // =========================================================================
    // WORK ORDERS (v2)
    // =========================================================================

    /**
     * Work Order create URL (with query params).
     * @param {Object} [queryParams] - e.g. { job: 123 }
     * @returns {string}
     */
    GTS.urls.workOrderNew = function(queryParams) {
        var baseUrl = GTS.urls.workOrderNewBase;
        if (!baseUrl) {
            console.error('[GTS.urls] workOrderNewBase not configured');
            return '';
        }
        return GTS.urls.withQuery(baseUrl, queryParams);
    };

    /**
     * Work Order edit URL.
     * @param {string|number} pk
     * @returns {string}
     */
    GTS.urls.workOrderEdit = function(pk) {
        var template = GTS.urls.workOrderEditTemplate;
        if (!template) {
            console.error('[GTS.urls] workOrderEditTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { pk: pk });
    };

    /**
     * Work Order PDF URL.
     * @param {string|number} pk
     * @returns {string}
     */
    GTS.urls.workOrderPdf = function(pk) {
        var template = GTS.urls.workOrderPdfTemplate;
        if (!template) {
            console.error('[GTS.urls] workOrderPdfTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { pk: pk });
    };

    /**
     * Accounting customer update URL.
     * @param {string|number} orgid
     * @returns {string}
     */
    GTS.urls.accountingCustomerUpdate = function(orgid) {
        var template = GTS.urls.accountingCustomerUpdateTemplate;
        if (!template) {
            console.error('[GTS.urls] accountingCustomerUpdateTemplate not configured');
            return '';
        }
        return GTS.urls.interpolate(template, { orgid: orgid });
    };

    /**
     * Accounting customer search URL (with query params).
     * @param {Object} [queryParams] - e.g. { q: 'acme' }
     * @returns {string}
     */
    GTS.urls.accountingCustomerSearchUrl = function(queryParams) {
        var baseUrl = GTS.urls.accountingCustomerSearch;
        if (!baseUrl) {
            console.error('[GTS.urls] accountingCustomerSearch not configured');
            return '';
        }
        return GTS.urls.withQuery(baseUrl, queryParams);
    };

    /**
     * Accounting item search URL (with query params).
     * @param {Object} [queryParams] - e.g. { q: 'bolt' }
     * @returns {string}
     */
    GTS.urls.accountingItemSearchUrl = function(queryParams) {
        var baseUrl = GTS.urls.accountingItemSearch;
        if (!baseUrl) {
            console.error('[GTS.urls] accountingItemSearch not configured');
            return '';
        }
        return GTS.urls.withQuery(baseUrl, queryParams);
    };

    GTS.urls.workOrderCustomerTaxRateUrl = function(queryParams) {
        var baseUrl = GTS.urls.workOrderCustomerTaxRate;
        if (!baseUrl) {
            console.error('[GTS.urls] workOrderCustomerTaxRate not configured');
            return '';
        }
        return GTS.urls.withQuery(baseUrl, queryParams);
    };

    GTS.urls.workOrderComputeTotalsUrl = function() {
        var baseUrl = GTS.urls.workOrderComputeTotals;
        if (!baseUrl) {
            console.error('[GTS.urls] workOrderComputeTotals not configured');
            return '';
        }
        return baseUrl;
    };

})();

