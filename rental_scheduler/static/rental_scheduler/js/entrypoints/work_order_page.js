/**
 * Work Order Page Entrypoint (v2)
 *
 * Handles:
 * - Customer search/select + create/update via Classic Accounting APIs
 * - Item search/select for line items
 * - Line add/remove
 * - Client-side totals preview (server remains source of truth)
 *
 * Requirements:
 * - No hard-coded URLs (use window.GTS.urls + shared url helpers)
 * - Idempotent init (use GTS.initOnce + delegation)
 */
(function() {
    'use strict';

    if (!window.GTS) return;

    GTS.onDomReady(function() {
        if (!GTS.initOnce) return;
        GTS.initOnce('work_order_page_v2', function() {
            initCustomerUI();
            initLineItemsUI();
            initTotalsUI();
            initSaveGuard();
            initUnsavedChangesGuard();
        });
    });

    // =========================================================================
    // Small utilities
    // =========================================================================

    function debounce(fn, delayMs) {
        var t = null;
        return function() {
            var args = arguments;
            clearTimeout(t);
            t = setTimeout(function() { fn.apply(null, args); }, delayMs);
        };
    }

    function show(el) {
        if (!el) return;
        el.classList.remove('hidden');
    }

    function hide(el) {
        if (!el) return;
        el.classList.add('hidden');
    }

    function closest(el, selector) {
        return el && el.closest ? el.closest(selector) : null;
    }

    function parseMoney(value) {
        var n = parseFloat(String(value || '').replace(/[^0-9.\-]/g, ''));
        if (isNaN(n)) return 0;
        return n;
    }

    function fmtMoney(n) {
        if (n == null || isNaN(n)) n = 0;
        return '$' + (Math.round(n * 100) / 100).toFixed(2);
    }

    function safeFetchJson(url, options) {
        return fetch(url, options).then(function(resp) {
            return resp.json().catch(function() { return {}; }).then(function(data) {
                if (!resp.ok) {
                    var msg = data && (data.error || data.message) ? (data.error || data.message) : ('Request failed (' + resp.status + ')');
                    var err = new Error(msg);
                    err.status = resp.status;
                    err.data = data;
                    throw err;
                }
                return data;
            });
        });
    }

    // =========================================================================
    // Tax rate state (module-level, shared across customer + totals UI)
    // =========================================================================

    var currentTaxRate = 0;
    var currentTaxExempt = false;

    function fetchTaxRateForCustomer(orgId) {
        if (!orgId || !GTS.urls || !GTS.urls.workOrderCustomerTaxRateUrl) {
            currentTaxRate = 0;
            currentTaxExempt = false;
            updateTaxExemptIndicator();
            if (typeof window.__woRecomputeTotals === 'function') window.__woRecomputeTotals();
            return;
        }
        var url = GTS.urls.workOrderCustomerTaxRateUrl({ customer_org_id: orgId });
        safeFetchJson(url).then(function(data) {
            currentTaxRate = parseFloat(data.tax_rate) || 0;
            currentTaxExempt = !!data.exempt;
            updateTaxExemptIndicator();
            if (typeof window.__woRecomputeTotals === 'function') window.__woRecomputeTotals();
        }).catch(function() {
            currentTaxRate = 0;
            currentTaxExempt = false;
            updateTaxExemptIndicator();
            if (typeof window.__woRecomputeTotals === 'function') window.__woRecomputeTotals();
        });
    }

    function clearTaxRate() {
        currentTaxRate = 0;
        currentTaxExempt = false;
        updateTaxExemptIndicator();
        if (typeof window.__woRecomputeTotals === 'function') window.__woRecomputeTotals();
    }

    function updateTaxExemptIndicator() {
        var el = document.querySelector('[data-wo-tax-exempt]');
        if (!el) return;
        var orgIdInput = document.querySelector('[data-wo-customer-org-id]');
        var hasCustomer = orgIdInput && orgIdInput.value && orgIdInput.value.trim() !== '';
        if (hasCustomer && currentTaxExempt) {
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
        }
    }

    // =========================================================================
    // Customer UI
    // =========================================================================

    function initCustomerUI() {
        var selected = null; // { org_id, name, phone, contact, email, address_* }
        var modalMode = 'create'; // create | edit
        var lastActiveElement = null;
        var isSaving = false;
        var hasShownErrors = false;
        var previousBodyOverflow = '';
        var modalKeydownHandler = null;
        var submitBtnDefaultHtml = null;
        var lastCreatePayload = null;

        function getEls() {
            return {
                orgIdInput: document.querySelector('[data-wo-customer-org-id]'),
                searchInput: document.querySelector('[data-wo-customer-search]'),
                results: document.querySelector('[data-wo-customer-results]'),
                selectedLabel: document.querySelector('[data-wo-customer-selected]'),
                createBtn: document.querySelector('[data-wo-customer-create]'),
                editBtn: document.querySelector('[data-wo-customer-edit]'),
                clearBtn: document.querySelector('[data-wo-customer-clear]'),
                modal: document.querySelector('[data-wo-customer-modal]'),
                modalBackdrop: document.querySelector('[data-wo-modal-backdrop]'),
                modalClose: document.querySelector('[data-wo-customer-modal-close]'),
                modalCancel: document.querySelector('[data-wo-customer-modal-cancel]'),
                modalTitle: document.querySelector('[data-wo-customer-modal-title]'),
                modalForm: document.querySelector('[data-wo-customer-modal-form]'),
                modalPanel: document.querySelector('[data-wo-customer-modal-panel]'),
                modalError: document.querySelector('[data-wo-customer-modal-error]'),
                dupesPanel: document.querySelector('[data-wo-customer-dupes]'),
                dupesList: document.querySelector('[data-wo-customer-dupes-list]'),
                dupesDismiss: document.querySelector('[data-wo-customer-dupes-dismiss]'),
                dupesCreateAnyway: document.querySelector('[data-wo-customer-dupes-create-anyway]'),
                submitBtn: document.querySelector('[data-wo-customer-modal-submit]'),
                nameError: document.querySelector('[data-wo-customer-name-error]'),
                emailError: document.querySelector('[data-wo-customer-email-error]'),
                address2Row: document.querySelector('[data-wo-address2-row]'),
                address2Toggle: document.querySelector('[data-wo-address2-toggle]'),
                fieldName: document.querySelector('[data-wo-cust-name]'),
                fieldPhone: document.querySelector('[data-wo-cust-phone]'),
                fieldContact: document.querySelector('[data-wo-cust-contact]'),
                fieldEmail: document.querySelector('[data-wo-cust-email]'),
                fieldAddr1: document.querySelector('[data-wo-cust-address1]'),
                fieldAddr2: document.querySelector('[data-wo-cust-address2]'),
                fieldCity: document.querySelector('[data-wo-cust-city]'),
                fieldState: document.querySelector('[data-wo-cust-state]'),
                fieldZip: document.querySelector('[data-wo-cust-zip]'),
            };
        }

        function getFocusableElements(container) {
            if (!container) return [];
            var selectors = [
                'a[href]',
                'button:not([disabled])',
                'textarea:not([disabled])',
                'input:not([disabled])',
                'select:not([disabled])',
                '[tabindex]:not([tabindex="-1"])'
            ];
            return Array.prototype.slice.call(container.querySelectorAll(selectors.join(','))).filter(function(el) {
                return !el.hasAttribute('aria-hidden');
            });
        }

        function lockBodyScroll() {
            previousBodyOverflow = document.body.style.overflow || '';
            document.body.style.overflow = 'hidden';
        }

        function unlockBodyScroll() {
            document.body.style.overflow = previousBodyOverflow;
            previousBodyOverflow = '';
        }

        function setModalError(message) {
            var els = getEls();
            if (!els.modalError) return;
            if (message) {
                els.modalError.textContent = message;
                els.modalError.classList.remove('hidden');
            } else {
                els.modalError.textContent = '';
                els.modalError.classList.add('hidden');
            }
        }

        function setFieldError(fieldEl, errorEl, message) {
            if (!fieldEl) return;
            if (message) {
                fieldEl.setAttribute('aria-invalid', 'true');
            } else {
                fieldEl.removeAttribute('aria-invalid');
            }
            if (!errorEl) return;
            if (message) {
                errorEl.textContent = message;
                errorEl.classList.remove('hidden');
            } else {
                errorEl.textContent = '';
                errorEl.classList.add('hidden');
            }
        }

        function clearModalErrors() {
            var els = getEls();
            setModalError('');
            setFieldError(els.fieldName, els.nameError, '');
            setFieldError(els.fieldEmail, els.emailError, '');
            hasShownErrors = false;
        }

        function clearDuplicateWarning() {
            var els = getEls();
            if (els.dupesList) {
                els.dupesList.innerHTML = '';
            }
            if (els.dupesPanel) {
                hide(els.dupesPanel);
            }
        }

        function formatDuplicateAddress(org) {
            var parts = [];
            if (org.address_line1) parts.push(org.address_line1);
            if (org.address_line2) parts.push(org.address_line2);
            var cityStateZip = [];
            if (org.city) cityStateZip.push(org.city);
            if (org.state) cityStateZip.push(org.state);
            if (org.zip) cityStateZip.push(org.zip);
            if (cityStateZip.length) parts.push(cityStateZip.join(', '));
            return parts.join(', ');
        }

        function renderDuplicateList(list) {
            var els = getEls();
            if (!els.dupesPanel || !els.dupesList) return;
            els.dupesList.innerHTML = '';
            if (!list || !list.length) {
                hide(els.dupesPanel);
                return;
            }

            list.forEach(function(org) {
                var row = document.createElement('div');
                row.className = 'wo-customer-dupes__item';

                var info = document.createElement('div');
                info.className = 'wo-customer-dupes__info';

                var nameEl = document.createElement('div');
                nameEl.className = 'wo-customer-dupes__name';
                var name = (org.name || '').trim();
                var phone = (org.phone || '').trim();
                var label = name || '';
                if (phone) {
                    label = label ? (label + ' (' + phone + ')') : phone;
                }
                nameEl.textContent = label || 'Unnamed customer';
                info.appendChild(nameEl);

                if (org.match_reasons && org.match_reasons.length) {
                    var reasonsEl = document.createElement('div');
                    reasonsEl.className = 'wo-customer-dupes__reasons';
                    org.match_reasons.forEach(function(reason) {
                        var pill = document.createElement('span');
                        pill.className = 'wo-customer-dupes__pill';
                        pill.textContent = reason;
                        reasonsEl.appendChild(pill);
                    });
                    info.appendChild(reasonsEl);
                }

                var useBtn = document.createElement('button');
                useBtn.type = 'button';
                useBtn.className = 'wo-btn wo-btn-outline wo-btn-sm';
                useBtn.textContent = 'Use this customer';
                useBtn.setAttribute('data-wo-customer-dup-use', '1');
                useBtn._org = org;

                row.appendChild(info);
                row.appendChild(useBtn);
                els.dupesList.appendChild(row);
            });

            show(els.dupesPanel);
        }

        function isValidEmail(value) {
            if (!value) return true;
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
        }

        function validateForm(showErrors) {
            var els = getEls();
            var name = (els.fieldName && els.fieldName.value ? els.fieldName.value : '').trim();
            var email = (els.fieldEmail && els.fieldEmail.value ? els.fieldEmail.value : '').trim();
            var errors = {};

            if (!name) {
                errors.name = 'Name is required.';
            }
            if (email && !isValidEmail(email)) {
                errors.email = 'Enter a valid email.';
            }

            if (showErrors) {
                setFieldError(els.fieldName, els.nameError, errors.name || '');
                setFieldError(els.fieldEmail, els.emailError, errors.email || '');
                setModalError(Object.keys(errors).length ? 'Please fix the highlighted fields.' : '');
                hasShownErrors = true;
            }

            return {
                isValid: Object.keys(errors).length === 0,
                errors: errors
            };
        }

        function updateSubmitState() {
            var els = getEls();
            if (!els.submitBtn) return;
            var result = validateForm(false);
            els.submitBtn.disabled = !result.isValid || isSaving;
        }

        function setSavingState(nextSaving) {
            var els = getEls();
            isSaving = !!nextSaving;

            if (els.submitBtn) {
                if (!submitBtnDefaultHtml) {
                    submitBtnDefaultHtml = els.submitBtn.innerHTML;
                }
                if (isSaving) {
                    els.submitBtn.disabled = true;
                    els.submitBtn.innerHTML = '' +
                        '<svg class="h-4 w-4 mr-2 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
                        '  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>' +
                        '  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>' +
                        '</svg>' +
                        'Saving...';
                } else {
                    els.submitBtn.innerHTML = submitBtnDefaultHtml || 'Save';
                }
            }

            if (els.modalCancel) {
                els.modalCancel.disabled = isSaving;
            }
            if (els.modalClose) {
                els.modalClose.disabled = isSaving;
            }
            if (els.dupesDismiss) {
                els.dupesDismiss.disabled = isSaving;
            }
            if (els.dupesCreateAnyway) {
                els.dupesCreateAnyway.disabled = isSaving;
            }
        }

        function showAddress2() {
            var els = getEls();
            if (els.address2Row) {
                els.address2Row.classList.remove('hidden');
            }
            if (els.address2Toggle) {
                els.address2Toggle.classList.add('hidden');
            }
            if (els.fieldAddr2) {
                els.fieldAddr2.focus();
            }
        }

        function syncAddress2State(value) {
            var els = getEls();
            var hasLine2 = value && String(value).trim();
            if (hasLine2) {
                if (els.address2Row) els.address2Row.classList.remove('hidden');
                if (els.address2Toggle) els.address2Toggle.classList.add('hidden');
            } else {
                if (els.address2Row) els.address2Row.classList.add('hidden');
                if (els.address2Toggle) els.address2Toggle.classList.remove('hidden');
            }
        }

        function attachModalKeydown() {
            var els = getEls();
            if (!els.modal || !els.modalPanel || modalKeydownHandler) return;

            modalKeydownHandler = function(e) {
                if (e.key === 'Escape') {
                    closeModal();
                    return;
                }

                if (e.key !== 'Tab') return;
                var focusable = getFocusableElements(els.modalPanel);
                if (!focusable.length) return;

                var first = focusable[0];
                var last = focusable[focusable.length - 1];

                if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                } else if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            };
            document.addEventListener('keydown', modalKeydownHandler);
        }

        function detachModalKeydown() {
            if (modalKeydownHandler) {
                document.removeEventListener('keydown', modalKeydownHandler);
                modalKeydownHandler = null;
            }
        }

        function setSelected(org) {
            selected = org || null;
            var els = getEls();
            if (!els.orgIdInput) return;
            els.orgIdInput.value = selected ? String(selected.org_id) : '';
            if (els.selectedLabel) {
                if (selected) {
                    var name = (selected.name || '').trim();
                    var phone = (selected.phone || '').trim();
                    var label = name || '';
                    if (phone) {
                        label = label ? (label + ' (' + phone + ')') : phone;
                    }
                    if (!label && selected.org_id) {
                        label = 'Customer #' + selected.org_id;
                    }
                    els.selectedLabel.textContent = label ? ('Selected: ' + label) : '';
                } else {
                    els.selectedLabel.textContent = '';
                }
            }
            if (els.editBtn) {
                els.editBtn.disabled = !selected;
            }
            if (els.clearBtn) {
                if (selected) {
                    els.clearBtn.classList.remove('hidden');
                } else {
                    els.clearBtn.classList.add('hidden');
                }
            }
            // Notify save guard of customer change
            if (typeof window.__woUpdateSaveButton === 'function') {
                window.__woUpdateSaveButton();
            }
            document.dispatchEvent(new CustomEvent('wo-customer-changed'));

            if (selected && selected.org_id) {
                if (selected.taxable === false) {
                    currentTaxRate = 0;
                    currentTaxExempt = true;
                    updateTaxExemptIndicator();
                    if (typeof window.__woRecomputeTotals === 'function') window.__woRecomputeTotals();
                } else {
                    fetchTaxRateForCustomer(selected.org_id);
                }
                fetchDefaultSalesRep(selected.org_id);
            } else {
                clearTaxRate();
            }
        }

        function fetchDefaultSalesRep(orgId) {
            var jobBySelect = document.getElementById('wo-job-by');
            if (!jobBySelect || !GTS.urls.salesReps) return;
            if (jobBySelect.value) return;
            var url = GTS.urls.salesReps + '?customer_org_id=' + encodeURIComponent(orgId);
            safeFetchJson(url).then(function(data) {
                if (data && data.customer_default_rep_id && !jobBySelect.value) {
                    jobBySelect.value = data.customer_default_rep_id;
                }
            });
        }

        function clearSelected() {
            var els = getEls();
            setSelected(null);
            if (els.searchInput) {
                els.searchInput.value = '';
            }
            if (els.results) {
                hide(els.results);
                els.results.innerHTML = '';
            }
        }

        function readInitialCustomer() {
            var script = document.getElementById('wo-initial-customer');
            if (!script) return null;
            try {
                return JSON.parse(script.textContent || '{}');
            } catch (e) {
                return null;
            }
        }

        function renderResults(list) {
            var els = getEls();
            if (!els.results) return;
            els.results.innerHTML = '';

            if (!list || list.length === 0) {
                els.results.innerHTML = '<div class="px-3 py-2 text-sm text-gray-500">No results</div>';
                show(els.results);
                return;
            }

            list.forEach(function(org) {
                var btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'wo-dropdown-item';
                btn.setAttribute('data-wo-customer-select', '1');
                btn.setAttribute('data-org-id', org.org_id);
                btn.setAttribute('role', 'option');
                var name = (org.name || '').trim();
                var phone = (org.phone || '').trim();
                var label = name || '';
                if (phone) {
                    label = label ? (label + ' (' + phone + ')') : phone;
                }
                btn.textContent = label;
                // Store details for modal edit (no address from search)
                btn._org = org;
                els.results.appendChild(btn);
            });
            show(els.results);
        }

        var doSearch = debounce(function(query) {
            var els = getEls();
            if (!els.results) return;

            if (!query || query.length < 2) {
                hide(els.results);
                els.results.innerHTML = '';
                return;
            }

            if (!GTS.urls || !GTS.urls.accountingCustomerSearchUrl) {
                GTS.showToast('Customer search URL is not configured.', 'error');
                return;
            }

            var url = GTS.urls.accountingCustomerSearchUrl({ q: query });
            els.results.innerHTML = '<div class="px-3 py-2 text-sm text-gray-500">Searching...</div>';
            show(els.results);
            safeFetchJson(url).then(function(data) {
                renderResults((data && data.results) || []);
            }).catch(function(err) {
                if (err && err.status === 503) {
                    GTS.showToast('Classic Accounting is not configured.', 'warning');
                } else {
                    GTS.showToast(err.message || 'Customer search failed.', 'error');
                }
                hide(els.results);
            });
        }, 250);

        function openModal(mode, triggerEl) {
            var els = getEls();
            if (!els.modal) return;
            modalMode = mode;
            lastActiveElement = triggerEl || document.activeElement;

            if (els.modalTitle) {
                els.modalTitle.textContent = mode === 'edit' ? 'Edit customer' : 'Create customer';
            }

            // Fill fields
            var src = (mode === 'edit' && selected) ? selected : {};
            if (els.fieldName) els.fieldName.value = src.name || '';
            if (els.fieldPhone) els.fieldPhone.value = src.phone || '';
            if (els.fieldContact) els.fieldContact.value = src.contact || '';
            if (els.fieldEmail) els.fieldEmail.value = src.email || '';
            if (els.fieldAddr1) els.fieldAddr1.value = src.address_line1 || '';
            if (els.fieldAddr2) els.fieldAddr2.value = src.address_line2 || '';
            if (els.fieldCity) els.fieldCity.value = src.city || '';
            if (els.fieldState) els.fieldState.value = (src.state || '').toUpperCase();
            if (els.fieldZip) els.fieldZip.value = src.zip || '';

            clearModalErrors();
            clearDuplicateWarning();
            setSavingState(false);
            syncAddress2State(src.address_line2 || '');

            show(els.modal);
            lockBodyScroll();
            attachModalKeydown();
            updateSubmitState();

            if (els.fieldName) {
                els.fieldName.focus();
            } else if (els.modalPanel) {
                els.modalPanel.focus();
            }
        }

        function closeModal() {
            var els = getEls();
            if (!els.modal || els.modal.classList.contains('hidden')) return;
            if (isSaving) return;
            hide(els.modal);
            detachModalKeydown();
            unlockBodyScroll();
            clearModalErrors();
            clearDuplicateWarning();
            if (lastActiveElement && typeof lastActiveElement.focus === 'function') {
                lastActiveElement.focus();
            }
        }

        function submitCustomer(payload, options) {
            var els = getEls();
            var opts = options || {};
            var mode = opts.mode || modalMode;
            var allowDuplicate = !!opts.allowDuplicate;

            var url;
            if (mode === 'edit' && selected && selected.org_id) {
                if (!GTS.urls || !GTS.urls.accountingCustomerUpdate) {
                    GTS.showToast('Customer update URL is not configured.', 'error');
                    setModalError('Customer update URL is not configured.');
                    setSavingState(false);
                    updateSubmitState();
                    return;
                }
                url = GTS.urls.accountingCustomerUpdate(selected.org_id);
            } else {
                url = (GTS.urls && GTS.urls.accountingCustomerCreate) ? GTS.urls.accountingCustomerCreate : '';
                if (!url) {
                    GTS.showToast('Customer create URL is not configured.', 'error');
                    setModalError('Customer create URL is not configured.');
                    setSavingState(false);
                    updateSubmitState();
                    return;
                }
            }

            var requestPayload = Object.assign({}, payload);
            if (allowDuplicate) {
                requestPayload.allow_duplicate = true;
            }
            if (mode === 'create' && !allowDuplicate) {
                lastCreatePayload = payload;
            }

            clearDuplicateWarning();
            setSavingState(true);

            safeFetchJson(url, {
                method: 'POST',
                headers: GTS.csrf && GTS.csrf.headers ? GTS.csrf.headers({ 'Content-Type': 'application/json' }) : { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestPayload),
            }).then(function(data) {
                var orgId = data && (data.org_id || data.orgid);
                if (!orgId) {
                    throw new Error('Missing org_id in response.');
                }
                // Update selection
                payload.org_id = orgId;
                setSelected(payload);
                var els2 = getEls();
                if (els2.searchInput) els2.searchInput.value = payload.name || '';
                setSavingState(false);
                closeModal();
                GTS.showToast('Customer saved.', 'success');
            }).catch(function(err) {
                setSavingState(false);
                updateSubmitState();
                if (err && err.status === 409 && err.data && err.data.duplicates && mode === 'create') {
                    renderDuplicateList(err.data.duplicates || []);
                    GTS.showToast('Possible duplicate customers found.', 'warning');
                    return;
                }
                if (err && err.status === 503) {
                    GTS.showToast('Classic Accounting is not configured.', 'warning');
                    setModalError('Classic Accounting is not configured.');
                } else {
                    var message = err.message || 'Customer save failed.';
                    GTS.showToast(message, 'error');
                    setModalError(message);
                }
            });
        }

        // Delegated interactions
        document.body.addEventListener('input', function(e) {
            var target = e.target;
            if (target && target.matches && target.matches('[data-wo-customer-search]')) {
                doSearch(target.value);
            }
            // State is now a select dropdown - no input manipulation needed
            if (target && target.matches && target.matches('[data-wo-cust-name], [data-wo-cust-phone], [data-wo-cust-address1], [data-wo-cust-address2], [data-wo-cust-city], [data-wo-cust-state], [data-wo-cust-zip]')) {
                clearDuplicateWarning();
            }
            if (target && target.matches && target.matches('[data-wo-cust-name], [data-wo-cust-email]')) {
                if (hasShownErrors) {
                    validateForm(true);
                }
                updateSubmitState();
            }
        });

        document.body.addEventListener('click', function(e) {
            var els = getEls();

            // Click outside results closes
            if (els.results && !closest(e.target, '[data-wo-customer-results]') && !closest(e.target, '[data-wo-customer-search]')) {
                hide(els.results);
            }

            var selectBtn = closest(e.target, '[data-wo-customer-select]');
            if (selectBtn && selectBtn._org) {
                setSelected(selectBtn._org);
                if (els.searchInput) els.searchInput.value = selectBtn._org.name || '';
                hide(els.results);
                return;
            }

            var dupUseBtn = closest(e.target, '[data-wo-customer-dup-use]');
            if (dupUseBtn && dupUseBtn._org) {
                setSelected(dupUseBtn._org);
                if (els.searchInput) els.searchInput.value = dupUseBtn._org.name || '';
                clearDuplicateWarning();
                closeModal();
                return;
            }

            var dupesDismiss = closest(e.target, '[data-wo-customer-dupes-dismiss]');
            if (dupesDismiss) {
                clearDuplicateWarning();
                return;
            }

            var dupesCreateAnyway = closest(e.target, '[data-wo-customer-dupes-create-anyway]');
            if (dupesCreateAnyway) {
                if (!lastCreatePayload) {
                    GTS.showToast('Please review customer details first.', 'warning');
                    return;
                }
                submitCustomer(lastCreatePayload, { mode: 'create', allowDuplicate: true });
                return;
            }

            var createBtn = closest(e.target, '[data-wo-customer-create]');
            if (createBtn) {
                openModal('create', createBtn);
                return;
            }

            var editBtn = closest(e.target, '[data-wo-customer-edit]');
            if (editBtn && !editBtn.disabled) {
                openModal('edit', editBtn);
                return;
            }

            var clearBtn = closest(e.target, '[data-wo-customer-clear]');
            if (clearBtn) {
                clearSelected();
                return;
            }

            var address2Toggle = closest(e.target, '[data-wo-address2-toggle]');
            if (address2Toggle) {
                showAddress2();
                return;
            }

            var closeBtn = closest(e.target, '[data-wo-customer-modal-close]');
            if (closeBtn) {
                closeModal();
                return;
            }
            var cancelBtn = closest(e.target, '[data-wo-customer-modal-cancel]');
            if (cancelBtn) {
                closeModal();
                return;
            }
            var backdrop = closest(e.target, '[data-wo-modal-backdrop]');
            if (backdrop) {
                closeModal();
                return;
            }
        });

        document.body.addEventListener('submit', function(e) {
            var form = closest(e.target, '[data-wo-customer-modal-form]');
            if (!form) return;
            e.preventDefault();

            var els = getEls();
            if (!els.fieldName) return;
            if (isSaving) return;

            setModalError('');
            var validation = validateForm(true);
            updateSubmitState();
            if (!validation.isValid) {
                return;
            }

            var payload = {
                name: els.fieldName.value ? els.fieldName.value.trim() : '',
                phone: els.fieldPhone ? els.fieldPhone.value.trim() : '',
                contact: els.fieldContact ? els.fieldContact.value.trim() : '',
                email: els.fieldEmail ? els.fieldEmail.value.trim() : '',
                address_line1: els.fieldAddr1 ? els.fieldAddr1.value.trim() : '',
                address_line2: els.fieldAddr2 ? els.fieldAddr2.value.trim() : '',
                city: els.fieldCity ? els.fieldCity.value.trim() : '',
                state: els.fieldState ? els.fieldState.value.trim().toUpperCase() : '',
                zip: els.fieldZip ? els.fieldZip.value.trim() : '',
            };
            submitCustomer(payload, { mode: modalMode });
        });

        // Hydrate selected customer on page load (after redirect)
        var els = getEls();
        if (els.orgIdInput && els.orgIdInput.value) {
            var initialCustomer = readInitialCustomer();
            if (!initialCustomer || !initialCustomer.org_id) {
                initialCustomer = { org_id: els.orgIdInput.value.trim() };
            }
            setSelected(initialCustomer);
            if (els.searchInput && initialCustomer.name) {
                els.searchInput.value = initialCustomer.name;
            }
        }
    }

    // =========================================================================
    // Line items UI (items search/select, add/remove)
    // =========================================================================

    function initLineItemsUI() {
        function findTableBody() {
            var table = document.querySelector('[data-wo-lines-table]');
            return table ? table.querySelector('tbody') : null;
        }

        function recomputeRow(row) {
            if (!row) return;
            var qtyEl = row.querySelector('[data-wo-qty]');
            var priceEl = row.querySelector('[data-wo-price]');
            var amtEl = row.querySelector('[data-wo-amount]');
            if (!qtyEl || !priceEl || !amtEl) return;
            var qty = parseMoney(qtyEl.value);
            var price = parseMoney(priceEl.value);
            amtEl.textContent = fmtMoney(qty * price);
        }

        function showLoadingSpinner(container) {
            if (!container) return;
            container.innerHTML = '<div class="flex items-center justify-center py-4">' +
                '<svg class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">' +
                '<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>' +
                '<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>' +
                '</svg></div>';
            show(container);
        }

        function renderItemResults(container, items) {
            if (!container) return;
            container.innerHTML = '';
            if (!items || items.length === 0) {
                container.innerHTML = '<div class="px-3 py-3 text-sm text-gray-500 text-center">No matching items found</div>';
                show(container);
                return;
            }
            items.forEach(function(item) {
                var btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'flex w-full items-center justify-between px-3 py-2.5 hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-0';
                btn.setAttribute('data-wo-item-select', '1');
                btn._item = item;
                var left = '<div class="text-left">' +
                    '<div class="font-medium text-gray-900 text-sm">' + (item.itemnumber || '') + '</div>' +
                    '<div class="text-xs text-gray-500 truncate max-w-xs">' + (item.salesdesc || '') + '</div>' +
                    '</div>';
                var right = item.price ? '<div class="text-sm font-medium text-gray-700 ml-4 whitespace-nowrap">' + fmtMoney(parseMoney(item.price)) + '</div>' : '';
                btn.innerHTML = left + right;
                container.appendChild(btn);
            });
            show(container);
        }

        function createBlankRow() {
            var tbody = findTableBody();
            if (!tbody) return null;
            var firstRow = tbody.querySelector('[data-wo-line-row]');
            if (!firstRow) return null;
            var clone = firstRow.cloneNode(true);
            clone.querySelectorAll('input').forEach(function(i) {
                if (i.name === 'line_qty') i.value = '1.00';
                else if (i.name === 'line_price') i.value = '0.00';
                else i.value = '';
                if (i.hasAttribute('readonly')) i.removeAttribute('readonly');
            });
            var descInput = clone.querySelector('[data-wo-description]');
            if (descInput) descInput.setAttribute('readonly', '');
            var amtEl = clone.querySelector('[data-wo-amount]');
            if (amtEl) amtEl.textContent = '0.00';
            var resEl = clone.querySelector('[data-wo-item-results]');
            if (resEl) {
                resEl.innerHTML = '';
                hide(resEl);
            }
            tbody.appendChild(clone);
            return clone;
        }

        var doItemSearch = debounce(function(row, query) {
            var results = row ? row.querySelector('[data-wo-item-results]') : null;
            if (!results) return;
            if (!query || query.length < 2) {
                hide(results);
                results.innerHTML = '';
                return;
            }
            if (!GTS.urls || !GTS.urls.accountingItemSearchUrl) {
                GTS.showToast('Item search URL is not configured.', 'error');
                return;
            }
            showLoadingSpinner(results);
            var url = GTS.urls.accountingItemSearchUrl({ q: query });
            safeFetchJson(url).then(function(data) {
                renderItemResults(results, (data && data.results) || []);
            }).catch(function(err) {
                if (err && err.status === 503) {
                    GTS.showToast('Classic Accounting is not configured.', 'warning');
                } else {
                    GTS.showToast(err.message || 'Item search failed.', 'error');
                }
                hide(results);
            });
        }, 200);

        document.body.addEventListener('input', function(e) {
            var input = e.target;

            if (input && input.matches && input.matches('[name="discount_value"]')) {
                recomputeTotals();
                return;
            }

            var row = closest(input, '[data-wo-line-row]');
            if (!row) return;

            if (input && input.matches && input.matches('[data-wo-itemnumber]')) {
                doItemSearch(row, input.value);
            }

            if (input && input.matches && (input.matches('[data-wo-qty]') || input.matches('[data-wo-price]'))) {
                recomputeRow(row);
                recomputeTotals();
            }
        });

        document.body.addEventListener('change', function(e) {
            var input = e.target;
            if (input && input.matches && input.matches('[name="discount_type"]')) {
                recomputeTotals();
            }
        });

        document.body.addEventListener('focusin', function(e) {
            var input = e.target;
            if (input && input.matches && input.matches('[data-wo-qty], [data-wo-price], [name="discount_value"]')) {
                setTimeout(function() { input.select(); }, 0);
            }
        });

        document.body.addEventListener('click', function(e) {
            var addBtn = closest(e.target, '[data-wo-add-line]');
            if (addBtn) {
                var newRow = createBlankRow();
                if (newRow) {
                    var partInput = newRow.querySelector('[data-wo-itemnumber]');
                    if (partInput) partInput.focus();
                }
                recomputeTotals();
                return;
            }

            var removeBtn = closest(e.target, '[data-wo-remove-line]');
            if (removeBtn) {
                var row = closest(removeBtn, '[data-wo-line-row]');
                var tbody = findTableBody();
                if (!row || !tbody) return;
                var rows = tbody.querySelectorAll('[data-wo-line-row]');
                if (rows.length <= 1) {
                    row.querySelectorAll('input').forEach(function(i) {
                        if (i.name === 'line_qty') i.value = '1.00';
                        else if (i.name === 'line_price') i.value = '0.00';
                        else i.value = '';
                    });
                    var amt = row.querySelector('[data-wo-amount]');
                    if (amt) amt.textContent = '0.00';
                } else {
                    row.remove();
                }
                recomputeTotals();
                return;
            }

            var itemBtn = closest(e.target, '[data-wo-item-select]');
            if (itemBtn && itemBtn._item) {
                var row2 = closest(itemBtn, '[data-wo-line-row]');
                if (!row2) return;

                var item = itemBtn._item;
                var itemidEl = row2.querySelector('[data-wo-itemid]');
                var itemnumEl = row2.querySelector('[data-wo-itemnumber]');
                var descEl = row2.querySelector('[data-wo-description]');
                var priceEl = row2.querySelector('[data-wo-price]');
                var resultsEl = row2.querySelector('[data-wo-item-results]');

                if (itemidEl) itemidEl.value = item.itemid;
                if (itemnumEl) itemnumEl.value = item.itemnumber || '';
                if (descEl) descEl.value = item.salesdesc || '';
                if (priceEl) priceEl.value = fmtMoney(parseMoney(item.price));
                if (resultsEl) hide(resultsEl);

                recomputeRow(row2);
                recomputeTotals();

                var qtyEl = row2.querySelector('[data-wo-qty]');
                if (qtyEl) {
                    qtyEl.focus();
                    setTimeout(function() { qtyEl.select(); }, 0);
                }

                createBlankRow();

                return;
            }

            var openResults = document.querySelectorAll('[data-wo-item-results]:not(.hidden)');
            if (openResults && openResults.length) {
                openResults.forEach(function(el) {
                    if (!closest(e.target, '[data-wo-item-results]') && !closest(e.target, '[data-wo-itemnumber]')) {
                        hide(el);
                    }
                });
            }
        });

        var _totalsRequestId = 0;

        function gatherTotalsPayload() {
            var rows = document.querySelectorAll('[data-wo-line-row]');
            var lineItems = [];
            rows.forEach(function(r) {
                var qtyEl = r.querySelector('[data-wo-qty]');
                var priceEl = r.querySelector('[data-wo-price]');
                lineItems.push({
                    qty: String(qtyEl ? parseMoney(qtyEl.value) : 0),
                    price: String(priceEl ? parseMoney(priceEl.value) : 0)
                });
            });

            var discountTypeEl = document.querySelector('input[name="discount_type"]:checked') || document.querySelector('[name="discount_type"]');
            var discountValueEl = document.querySelector('[name="discount_value"]');

            return {
                line_items: lineItems,
                discount_type: discountTypeEl ? discountTypeEl.value : 'amount',
                discount_value: String(discountValueEl ? parseMoney(discountValueEl.value) : 0),
                tax_rate: String(currentTaxRate)
            };
        }

        function applyTotalsFromServer(data) {
            var subtotalEl = document.querySelector('[data-wo-subtotal]');
            var discountEl = document.querySelector('[data-wo-discount-amount]');
            var taxEl = document.querySelector('[data-wo-tax-amount]');
            var totalEl = document.querySelector('[data-wo-total]');
            if (subtotalEl) subtotalEl.textContent = fmtMoney(parseFloat(data.subtotal));
            if (discountEl) discountEl.textContent = fmtMoney(parseFloat(data.discount_amount));
            if (taxEl) taxEl.textContent = fmtMoney(parseFloat(data.tax_amount));
            if (totalEl) totalEl.textContent = fmtMoney(parseFloat(data.total));
        }

        function _fetchTotals() {
            var url = GTS.urls.workOrderComputeTotalsUrl ? GTS.urls.workOrderComputeTotalsUrl() : '';
            if (!url) return;

            var payload = gatherTotalsPayload();
            var requestId = ++_totalsRequestId;

            var totalsSection = document.querySelector('[data-wo-totals-section]');
            if (totalsSection) totalsSection.style.opacity = '0.5';

            safeFetchJson(url, {
                method: 'POST',
                headers: GTS.csrf && GTS.csrf.headers
                    ? GTS.csrf.headers({ 'Content-Type': 'application/json' })
                    : { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(function(data) {
                if (requestId !== _totalsRequestId) return;
                applyTotalsFromServer(data);
            }).catch(function() {
                if (requestId !== _totalsRequestId) return;
            }).then(function() {
                if (requestId !== _totalsRequestId) return;
                if (totalsSection) totalsSection.style.opacity = '';
            });
        }

        var recomputeTotals = debounce(_fetchTotals, 300);

        window.__woRecomputeTotals = recomputeTotals;
    }

    // =========================================================================
    // Totals UI (initial computation)
    // =========================================================================

    function initTotalsUI() {
        var snapshotEl = document.querySelector('[data-wo-tax-rate-snapshot]');
        if (snapshotEl) {
            var snapshotRate = parseFloat(snapshotEl.value);
            if (!isNaN(snapshotRate) && snapshotRate > 0) {
                currentTaxRate = snapshotRate;
            }
        }

        var rows = document.querySelectorAll('[data-wo-line-row]');
        rows.forEach(function(r) {
            var qtyEl = r.querySelector('[data-wo-qty]');
            var priceEl = r.querySelector('[data-wo-price]');
            var amtEl = r.querySelector('[data-wo-amount]');
            if (!qtyEl || !priceEl || !amtEl) return;
            var qty = parseMoney(qtyEl.value);
            var price = parseMoney(priceEl.value);
            amtEl.textContent = fmtMoney(qty * price);
        });

        if (typeof window.__woRecomputeTotals === 'function') {
            window.__woRecomputeTotals();
        }

        updateTaxExemptIndicator();
    }

    // =========================================================================
    // Save Guard (require customer before save)
    // =========================================================================

    function initSaveGuard() {
        var form = document.querySelector('[data-wo-main-form]');
        var orgIdInput = document.querySelector('[data-wo-customer-org-id]');
        var saveBtn = document.querySelector('[data-wo-save-btn]');
        var searchInput = document.querySelector('[data-wo-customer-search]');

        if (!form || !orgIdInput || !saveBtn) return;

        function hasAtLeastOneLineItem() {
            var itemIdInputs = document.querySelectorAll('input[name="line_itemid"]');
            for (var i = 0; i < itemIdInputs.length; i++) {
                if (itemIdInputs[i].value && itemIdInputs[i].value.trim() !== '') {
                    return true;
                }
            }
            return false;
        }

        function updateSaveButtonState() {
            var hasCustomer = orgIdInput.value && orgIdInput.value.trim() !== '';
            saveBtn.disabled = !hasCustomer;
        }

        updateSaveButtonState();

        var lastValue = orgIdInput.value;
        var checkInterval = setInterval(function() {
            if (orgIdInput.value !== lastValue) {
                lastValue = orgIdInput.value;
                updateSaveButtonState();
            }
        }, 100);

        document.addEventListener('wo-customer-changed', function() {
            updateSaveButtonState();
        });

        form.addEventListener('submit', function(e) {
            var hasCustomer = orgIdInput.value && orgIdInput.value.trim() !== '';
            if (!hasCustomer) {
                e.preventDefault();
                if (GTS && GTS.showToast) {
                    GTS.showToast('Select a customer before saving.', 'error');
                }
                if (searchInput) {
                    searchInput.focus();
                }
                return false;
            }

            if (!hasAtLeastOneLineItem()) {
                e.preventDefault();
                if (GTS && GTS.showToast) {
                    GTS.showToast('At least one line item is required.', 'error');
                }
                return false;
            }
        });

        window.__woUpdateSaveButton = updateSaveButtonState;
    }

    // =========================================================================
    // Unsaved Changes Guard (prompt on Back click)
    // =========================================================================

    function initUnsavedChangesGuard() {
        var form = document.querySelector('[data-wo-main-form]');
        var modal = document.querySelector('[data-wo-unsaved-modal]');
        var backdrop = document.querySelector('[data-wo-unsaved-backdrop]');
        var panel = document.querySelector('[data-wo-unsaved-panel]');
        var cancelBtn = document.querySelector('[data-wo-unsaved-cancel]');
        var discardBtn = document.querySelector('[data-wo-unsaved-discard]');
        var saveBackBtn = document.querySelector('[data-wo-unsaved-save-back]');
        var closeBtn = document.querySelector('[data-wo-unsaved-close]');
        var afterSaveInput = document.querySelector('[data-wo-after-save]');
        var actualBackLink = document.querySelector('[data-wo-back-link]');

        if (!form || !actualBackLink || !modal) return;

        var isDirty = false;
        var backHref = null;
        var lastActiveElement = null;
        var modalKeydownHandler = null;

        // Track initial form state
        var initialFormData = new FormData(form);
        var initialFormString = Array.from(initialFormData.entries()).map(function(pair) {
            return pair[0] + '=' + (pair[1] || '');
        }).sort().join('&');

        function checkDirty() {
            var currentFormData = new FormData(form);
            var currentFormString = Array.from(currentFormData.entries()).map(function(pair) {
                return pair[0] + '=' + (pair[1] || '');
            }).sort().join('&');
            isDirty = currentFormString !== initialFormString;
        }

        function showModal() {
            if (!modal || !modal.classList.contains('hidden')) return;
            lastActiveElement = document.activeElement;
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            attachModalKeydown();
            if (panel) {
                panel.focus();
            }
        }

        function hideModal() {
            if (!modal || modal.classList.contains('hidden')) return;
            modal.classList.add('hidden');
            document.body.style.overflow = '';
            detachModalKeydown();
            if (lastActiveElement && typeof lastActiveElement.focus === 'function') {
                lastActiveElement.focus();
            }
        }

        function attachModalKeydown() {
            if (modalKeydownHandler) return;
            modalKeydownHandler = function(e) {
                if (e.key === 'Escape') {
                    hideModal();
                }
            };
            document.addEventListener('keydown', modalKeydownHandler);
        }

        function detachModalKeydown() {
            if (modalKeydownHandler) {
                document.removeEventListener('keydown', modalKeydownHandler);
                modalKeydownHandler = null;
            }
        }

        // Track form changes (only for fields with name attribute, ignore search)
        form.addEventListener('input', function(e) {
            var target = e.target;
            if (target && target.matches && target.matches('[data-wo-customer-search]')) {
                return; // Ignore search input
            }
            if (target && target.hasAttribute && target.hasAttribute('name')) {
                checkDirty();
            }
        });

        form.addEventListener('change', function(e) {
            var target = e.target;
            if (target && target.hasAttribute && target.hasAttribute('name')) {
                checkDirty();
            }
        });

        // Intercept Back link click
        if (actualBackLink) {
            actualBackLink.addEventListener('click', function(e) {
                checkDirty();
                if (isDirty) {
                    e.preventDefault();
                    backHref = actualBackLink.href;
                    showModal();
                }
            });
        }

        // Modal actions
        if (cancelBtn) {
            cancelBtn.addEventListener('click', hideModal);
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', hideModal);
        }
        if (backdrop) {
            backdrop.addEventListener('click', hideModal);
        }

        if (discardBtn) {
            discardBtn.addEventListener('click', function() {
                isDirty = false;
                hideModal();
                if (backHref) {
                    window.location.href = backHref;
                }
            });
        }

        if (saveBackBtn && afterSaveInput) {
            saveBackBtn.addEventListener('click', function() {
                afterSaveInput.value = 'back';
                hideModal();
                // Use requestSubmit to trigger normal validation and submit handlers
                if (form.requestSubmit) {
                    form.requestSubmit();
                } else {
                    form.submit();
                }
            });
        }

        // Reset dirty state on successful form submission
        form.addEventListener('submit', function() {
            isDirty = false;
        });
    }
})();

