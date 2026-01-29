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
        return (Math.round(n * 100) / 100).toFixed(2);
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
    // Customer UI
    // =========================================================================

    function initCustomerUI() {
        var selected = null; // { org_id, name, phone, contact, email, address_* }
        var modalMode = 'create'; // create | edit

        function getEls() {
            return {
                orgIdInput: document.querySelector('[data-wo-customer-org-id]'),
                searchInput: document.querySelector('[data-wo-customer-search]'),
                results: document.querySelector('[data-wo-customer-results]'),
                selectedLabel: document.querySelector('[data-wo-customer-selected]'),
                createBtn: document.querySelector('[data-wo-customer-create]'),
                editBtn: document.querySelector('[data-wo-customer-edit]'),
                modal: document.querySelector('[data-wo-customer-modal]'),
                modalBackdrop: document.querySelector('[data-wo-modal-backdrop]'),
                modalClose: document.querySelector('[data-wo-customer-modal-close]'),
                modalCancel: document.querySelector('[data-wo-customer-modal-cancel]'),
                modalTitle: document.querySelector('[data-wo-customer-modal-title]'),
                modalForm: document.querySelector('[data-wo-customer-modal-form]'),
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

        function setSelected(org) {
            selected = org || null;
            var els = getEls();
            if (!els.orgIdInput) return;
            els.orgIdInput.value = selected ? String(selected.org_id) : '';
            if (els.selectedLabel) {
                els.selectedLabel.textContent = selected ? ('Selected: ' + (selected.name || '') + ' (#' + selected.org_id + ')') : '';
            }
            if (els.editBtn) {
                els.editBtn.disabled = !selected;
            }
        }

        function renderResults(list) {
            var els = getEls();
            if (!els.results) return;
            els.results.innerHTML = '';

            if (!list || list.length === 0) {
                els.results.innerHTML = '<div class="p-2 text-sm text-gray-600">No results</div>';
                show(els.results);
                return;
            }

            list.forEach(function(org) {
                var btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'block w-full text-left px-3 py-2 hover:bg-gray-50';
                btn.setAttribute('data-wo-customer-select', '1');
                btn.setAttribute('data-org-id', org.org_id);
                btn.textContent = (org.name || '') + '  (#' + org.org_id + ')';
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

        function openModal(mode) {
            var els = getEls();
            if (!els.modal) return;
            modalMode = mode;

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
            if (els.fieldState) els.fieldState.value = src.state || '';
            if (els.fieldZip) els.fieldZip.value = src.zip || '';

            show(els.modal);
        }

        function closeModal() {
            var els = getEls();
            hide(els.modal);
        }

        // Delegated interactions
        document.body.addEventListener('input', function(e) {
            var target = e.target;
            if (target && target.matches && target.matches('[data-wo-customer-search]')) {
                doSearch(target.value);
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

            var createBtn = closest(e.target, '[data-wo-customer-create]');
            if (createBtn) {
                openModal('create');
                return;
            }

            var editBtn = closest(e.target, '[data-wo-customer-edit]');
            if (editBtn && !editBtn.disabled) {
                openModal('edit');
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

            var payload = {
                name: els.fieldName.value || '',
                phone: els.fieldPhone ? els.fieldPhone.value : '',
                contact: els.fieldContact ? els.fieldContact.value : '',
                email: els.fieldEmail ? els.fieldEmail.value : '',
                address_line1: els.fieldAddr1 ? els.fieldAddr1.value : '',
                address_line2: els.fieldAddr2 ? els.fieldAddr2.value : '',
                city: els.fieldCity ? els.fieldCity.value : '',
                state: els.fieldState ? els.fieldState.value : '',
                zip: els.fieldZip ? els.fieldZip.value : '',
            };

            var url;
            if (modalMode === 'edit' && selected && selected.org_id) {
                if (!GTS.urls || !GTS.urls.accountingCustomerUpdate) {
                    GTS.showToast('Customer update URL is not configured.', 'error');
                    return;
                }
                url = GTS.urls.accountingCustomerUpdate(selected.org_id);
            } else {
                url = (GTS.urls && GTS.urls.accountingCustomerCreate) ? GTS.urls.accountingCustomerCreate : '';
                if (!url) {
                    GTS.showToast('Customer create URL is not configured.', 'error');
                    return;
                }
            }

            safeFetchJson(url, {
                method: 'POST',
                headers: GTS.csrf && GTS.csrf.headers ? GTS.csrf.headers({ 'Content-Type': 'application/json' }) : { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
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
                closeModal();
                GTS.showToast('Customer saved.', 'success');
            }).catch(function(err) {
                if (err && err.status === 503) {
                    GTS.showToast('Classic Accounting is not configured.', 'warning');
                } else {
                    GTS.showToast(err.message || 'Customer save failed.', 'error');
                }
            });
        });
    }

    // =========================================================================
    // Line items UI (items search/select, add/remove)
    // =========================================================================

    function initLineItemsUI() {
        function findTableBody() {
            var table = document.querySelector('table');
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

        function renderItemResults(container, items) {
            if (!container) return;
            container.innerHTML = '';
            if (!items || items.length === 0) {
                container.innerHTML = '<div class="p-2 text-sm text-gray-600">No results</div>';
                show(container);
                return;
            }
            items.forEach(function(item) {
                var btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'block w-full text-left px-3 py-2 hover:bg-gray-50';
                btn.setAttribute('data-wo-item-select', '1');
                btn._item = item;
                btn.textContent = (item.itemnumber || '') + ' — ' + (item.salesdesc || '');
                container.appendChild(btn);
            });
            show(container);
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
            var row = closest(input, '[data-wo-line-row]');
            if (!row) return;

            if (input && input.matches && input.matches('[data-wo-itemnumber]')) {
                doItemSearch(row, input.value);
            }

            if (input && input.matches && (input.matches('[data-wo-qty]') || input.matches('[data-wo-price]'))) {
                recomputeRow(row);
                recomputeTotals();
            }

            if (input && input.matches && input.matches('[name="discount_value"], [name="discount_type"]')) {
                recomputeTotals();
            }
        });

        document.body.addEventListener('click', function(e) {
            var addBtn = closest(e.target, '[data-wo-add-line]');
            if (addBtn) {
                var tbody = findTableBody();
                if (!tbody) return;
                var firstRow = tbody.querySelector('[data-wo-line-row]');
                if (!firstRow) return;
                var clone = firstRow.cloneNode(true);

                // Clear values
                var inputs = clone.querySelectorAll('input');
                inputs.forEach(function(i) {
                    if (i.name === 'line_qty') i.value = '1.00';
                    else if (i.name === 'line_price') i.value = '0.00';
                    else i.value = '';
                });
                var amtEl = clone.querySelector('[data-wo-amount]');
                if (amtEl) amtEl.textContent = '0.00';
                var resEl = clone.querySelector('[data-wo-item-results]');
                if (resEl) {
                    resEl.innerHTML = '';
                    hide(resEl);
                }
                tbody.appendChild(clone);
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
                    // Keep at least one row
                    var inputs2 = row.querySelectorAll('input');
                    inputs2.forEach(function(i) {
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
                return;
            }

            // Click outside item results closes dropdown
            var openResults = document.querySelectorAll('[data-wo-item-results]:not(.hidden)');
            if (openResults && openResults.length) {
                openResults.forEach(function(el) {
                    if (!closest(e.target, '[data-wo-item-results]') && !closest(e.target, '[data-wo-itemnumber]')) {
                        hide(el);
                    }
                });
            }
        });

        function recomputeTotals() {
            var subtotalEl = document.querySelector('[data-wo-subtotal]');
            var discountEl = document.querySelector('[data-wo-discount-amount]');
            var totalEl = document.querySelector('[data-wo-total]');

            if (!subtotalEl || !discountEl || !totalEl) return;

            var rows = document.querySelectorAll('[data-wo-line-row]');
            var subtotal = 0;
            rows.forEach(function(r) {
                var qtyEl = r.querySelector('[data-wo-qty]');
                var priceEl = r.querySelector('[data-wo-price]');
                var qty = qtyEl ? parseMoney(qtyEl.value) : 0;
                var price = priceEl ? parseMoney(priceEl.value) : 0;
                subtotal += qty * price;
            });

            var discountTypeEl = document.querySelector('[name="discount_type"]');
            var discountValueEl = document.querySelector('[name="discount_value"]');
            var discountType = discountTypeEl ? discountTypeEl.value : 'amount';
            var discountValue = discountValueEl ? parseMoney(discountValueEl.value) : 0;

            var discountAmount = 0;
            if (discountType === 'percent') {
                if (discountValue < 0) discountValue = 0;
                if (discountValue > 100) discountValue = 100;
                discountAmount = subtotal * (discountValue / 100);
            } else {
                if (discountValue < 0) discountValue = 0;
                if (discountValue > subtotal) discountValue = subtotal;
                discountAmount = discountValue;
            }

            var total = subtotal - discountAmount;

            subtotalEl.textContent = fmtMoney(subtotal);
            discountEl.textContent = fmtMoney(discountAmount);
            totalEl.textContent = fmtMoney(total);
        }

        // Expose for initTotalsUI to call once
        window.__woRecomputeTotals = recomputeTotals;
    }

    // =========================================================================
    // Totals UI (initial computation)
    // =========================================================================

    function initTotalsUI() {
        // Compute all existing row amounts once
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
    }
})();

