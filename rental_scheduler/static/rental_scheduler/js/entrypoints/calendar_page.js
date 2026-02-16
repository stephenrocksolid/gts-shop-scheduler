/**
 * Calendar Page Entrypoint
 * 
 * Extracted from calendar.html inline script.
 * Handles:
 * - Sidebar resize with localStorage persistence (gts-sidebar-width)
 * - Scroll prevention and wheel routing for calendar areas
 * - Search panel behaviors (dropdown, form submit, keyboard navigation, row click)
 * - Popover repositioning within viewport
 * 
 * Requires: GTS.initOnce, window.calendarConfig, window.JobPanel, window.jobCalendar
 */
(function() {
    'use strict';

    /**
     * Initialize the calendar page behaviors.
     * Uses GTS.initOnce to prevent duplicate bindings.
     */
    function initCalendarPage() {
        initSidebarResize();
        GTS.onDomReady(function() {
            initScrollPrevention();
            initPopoverObserver();
            initSearchPanel();
        });
    }

    // ========================================================================
    // SIDEBAR RESIZE
    // ========================================================================

    function initSidebarResize() {
        GTS.initOnce('calendar_sidebar_resize', function() {
            const sidebar = document.getElementById('todaySidebar');
            const resizeHandle = document.getElementById('sidebarResizeHandle');

            if (!sidebar || !resizeHandle) {
                return;
            }

            const STORAGE_KEY = 'gts-sidebar-width';
            const MIN_WIDTH = 10;
            const MAX_WIDTH = 1200;

            // Load saved width
            const savedWidth = GTS.storage.getRaw(STORAGE_KEY);
            if (savedWidth) {
                sidebar.style.width = savedWidth + 'px';
            }

            let isResizing = false;
            let startX = 0;
            let startWidth = 0;

            resizeHandle.addEventListener('mousedown', function(e) {
                isResizing = true;
                startX = e.clientX;
                startWidth = sidebar.offsetWidth;
                resizeHandle.classList.add('active');
                document.body.style.cursor = 'ew-resize';
                document.body.style.userSelect = 'none';
                e.preventDefault();
                e.stopPropagation();
            });

            document.addEventListener('mousemove', function(e) {
                if (!isResizing) return;

                // Calculate new width (subtract because we're dragging from the left edge)
                const delta = startX - e.clientX;
                let newWidth = startWidth + delta;

                // Clamp to min/max
                newWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, newWidth));

                sidebar.style.width = newWidth + 'px';
            });

            document.addEventListener('mouseup', function() {
                if (isResizing) {
                    isResizing = false;
                    resizeHandle.classList.remove('active');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';

                    // Save width to localStorage
                    GTS.storage.setRaw(STORAGE_KEY, sidebar.offsetWidth);

                    // Trigger calendar resize event so it adjusts
                    if (window.jobCalendar && window.jobCalendar.calendar) {
                        window.jobCalendar.calendar.updateSize();
                        window.jobCalendar.forceEqualWeekHeights();
                    }
                }
            });
        });
    }

    // ========================================================================
    // SCROLL PREVENTION
    // ========================================================================

    function initScrollPrevention() {
        GTS.initOnce('calendar_scroll_prevention', function() {
            const todayList = document.getElementById('todayList');
            const todaySidebar = document.getElementById('todaySidebar');
            const calendarWrap = document.getElementById('calendar-wrap');
            const calendarPage = document.getElementById('calendarPage');
            const searchResultsContainer = document.getElementById('search-results-container');

            // Allow scrolling ONLY in the Today sidebar's list
            if (todayList) {
                todayList.addEventListener('wheel', function(e) {
                    const scrollTop = todayList.scrollTop;
                    const scrollHeight = todayList.scrollHeight;
                    const height = todayList.clientHeight;
                    const delta = e.deltaY;

                    // Prevent scroll chaining when at top or bottom
                    if ((delta < 0 && scrollTop <= 0) ||
                        (delta > 0 && scrollTop + height >= scrollHeight)) {
                        e.preventDefault();
                    }

                    // Always stop propagation to prevent calendar scroll
                    e.stopPropagation();
                }, { passive: false });
            }

            // Allow scrolling in search results container
            if (searchResultsContainer) {
                searchResultsContainer.addEventListener('wheel', function(e) {
                    e.stopPropagation();
                }, { passive: false });
            }

            // Prevent ALL scrolling on the calendar area
            if (calendarWrap) {
                calendarWrap.addEventListener('wheel', function(e) {
                    // Check if the event target is inside the today sidebar
                    if (todaySidebar && todaySidebar.contains(e.target)) {
                        // Allow scrolling in the sidebar
                        return;
                    }
                    // Prevent scrolling everywhere else
                    e.preventDefault();
                    e.stopPropagation();
                }, { passive: false });
            }

            // Also prevent on the calendar page container
            if (calendarPage) {
                calendarPage.addEventListener('wheel', function(e) {
                    // Check if the event target is inside the today sidebar
                    if (todaySidebar && todaySidebar.contains(e.target)) {
                        // Allow scrolling in the sidebar
                        return;
                    }
                    // Check if the event target is inside a FullCalendar popover
                    const popover = e.target.closest('.fc-popover');
                    if (popover) {
                        // Allow scrolling in the popover
                        const popoverBody = popover.querySelector('.fc-popover-body');
                        if (popoverBody && popoverBody.contains(e.target)) {
                            // Stop propagation to prevent calendar scroll
                            e.stopPropagation();
                            return;
                        }
                    }
                    // Prevent scrolling everywhere else
                    e.preventDefault();
                    e.stopPropagation();
                }, { passive: false });
            }
        });
    }

    // ========================================================================
    // POPOVER OBSERVER
    // ========================================================================

    function initPopoverObserver() {
        GTS.initOnce('calendar_popover_observer', function() {
            const calendarWrap = document.getElementById('calendar-wrap');
            if (!calendarWrap) return;

            // Use MutationObserver to detect when popovers are added and configure them
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1 && node.classList && node.classList.contains('fc-popover')) {
                            const popoverBody = node.querySelector('.fc-popover-body');
                            if (popoverBody) {
                                // Add scroll event listener to popover body
                                popoverBody.addEventListener('wheel', function(e) {
                                    e.stopPropagation();
                                }, { passive: false });
                            }

                            // Reposition popover to stay within viewport
                            setTimeout(function() {
                                repositionPopover(node);
                            }, 10);
                        }
                    });
                });
            });

            observer.observe(calendarWrap, { childList: true, subtree: true });
        });
    }

    /**
     * Reposition a popover to stay within the viewport
     */
    function repositionPopover(popover) {
        const rect = popover.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;

        let newTop = rect.top;
        let newLeft = rect.left;
        let needsRepositioning = false;

        // Check if popover extends beyond bottom of viewport
        if (rect.bottom > viewportHeight - 20) {
            // Position it so bottom edge is 20px from viewport bottom
            newTop = viewportHeight - rect.height - 20;
            needsRepositioning = true;

            // If it's still too tall and would go above viewport, pin to top
            if (newTop < 20) {
                newTop = 20;
                // Constrain height
                popover.style.maxHeight = (viewportHeight - 40) + 'px';
                const popoverBody = popover.querySelector('.fc-popover-body');
                if (popoverBody) {
                    popoverBody.style.maxHeight = (viewportHeight - 90) + 'px';
                }
            }
        }

        // Check if popover extends beyond right edge
        if (rect.right > viewportWidth - 20) {
            newLeft = viewportWidth - rect.width - 20;
            needsRepositioning = true;
        }

        // Check if popover extends beyond left edge
        if (rect.left < 20) {
            newLeft = 20;
            needsRepositioning = true;
        }

        // Check if popover extends beyond top edge
        if (rect.top < 20) {
            newTop = 20;
            needsRepositioning = true;
        }

        // Apply new position if needed
        if (needsRepositioning) {
            popover.style.top = newTop + 'px';
            popover.style.left = newLeft + 'px';
        }
    }

    // ========================================================================
    // SEARCH PANEL
    // ========================================================================

    function initSearchPanel() {
        GTS.initOnce('calendar_search_panel', function() {
            const searchCalendarDropdownBtn = document.getElementById('search-calendar-dropdown-btn');
            const searchCalendarDropdown = document.getElementById('search-calendar-dropdown');
            const searchCalendarCheckboxes = document.querySelectorAll('.search-calendar-checkbox');
            const searchCalendarAllCheckbox = document.getElementById('search-calendar-all-checkbox');
            const searchCalendarSelectedText = document.getElementById('search-calendar-selected-text');
            const searchForm = document.getElementById('calendar-search-form');
            const searchResults = document.getElementById('search-results');
            const searchResultsContainer = document.getElementById('search-results-container');
            const searchInput = document.getElementById('calendar-search-input');

            // Keyboard navigation state
            let currentHighlightIndex = -1;
            let jobRows = [];
            let hasSubmitted = false;

            /**
             * Updates the search calendar UI:
             * - Sets button label based on selection count
             * - Sets select-all checkbox checked/indeterminate state
             */
            function updateSearchCalendarUI() {
                const checkedCount = document.querySelectorAll('.search-calendar-checkbox:checked').length;
                const totalCount = searchCalendarCheckboxes.length;

                // Update button label
                if (searchCalendarSelectedText) {
                    if (checkedCount === 0) {
                        searchCalendarSelectedText.textContent = 'No Calendars';
                    } else if (checkedCount === totalCount) {
                        searchCalendarSelectedText.textContent = 'All Calendars';
                    } else {
                        searchCalendarSelectedText.textContent = checkedCount + ' calendar(s) selected';
                    }
                }

                // Update select-all checkbox state
                if (searchCalendarAllCheckbox) {
                    searchCalendarAllCheckbox.checked = checkedCount === totalCount;
                    searchCalendarAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
                }
            }

            // Update job rows after search
            function updateJobRows() {
                jobRows = searchResults ? Array.from(searchResults.querySelectorAll('.job-row')) : [];
                currentHighlightIndex = -1;
            }

            // Highlight a specific row
            function highlightRow(index) {
                // Remove previous highlights
                jobRows.forEach(function(row) {
                    row.classList.remove('bg-blue-100', 'ring-2', 'ring-blue-500');
                    row.style.backgroundColor = '';
                });

                if (index >= 0 && index < jobRows.length) {
                    const row = jobRows[index];
                    row.classList.add('bg-blue-100', 'ring-2', 'ring-blue-500');

                    // Scroll the row into view smoothly within the search results container
                    row.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }

            // Toggle calendar dropdown
            if (searchCalendarDropdownBtn) {
                searchCalendarDropdownBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (searchCalendarDropdown) {
                        searchCalendarDropdown.classList.toggle('hidden');
                    }
                });
            }

            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (searchCalendarDropdownBtn && searchCalendarDropdown &&
                    !searchCalendarDropdownBtn.contains(e.target) &&
                    !searchCalendarDropdown.contains(e.target)) {
                    searchCalendarDropdown.classList.add('hidden');
                }
            });

            // Handle select-all checkbox change
            if (searchCalendarAllCheckbox) {
                searchCalendarAllCheckbox.addEventListener('change', function() {
                    const isChecked = this.checked;
                    // Clear indeterminate when user explicitly clicks
                    this.indeterminate = false;
                    // Check/uncheck all individual calendar checkboxes
                    searchCalendarCheckboxes.forEach(function(cb) {
                        cb.checked = isChecked;
                    });
                    updateSearchCalendarUI();
                });
            }

            // Update UI when individual checkboxes change
            if (searchCalendarCheckboxes) {
                searchCalendarCheckboxes.forEach(function(checkbox) {
                    checkbox.addEventListener('change', function() {
                        updateSearchCalendarUI();
                    });
                });
            }

            // Initialize search calendar checkboxes on page load
            (function initSearchCalendarDefaults() {
                const urlParams = new URLSearchParams(window.location.search);
                const calendarParams = urlParams.getAll('calendars');

                if (calendarParams.length > 0) {
                    // URL has specific calendars - check only those
                    searchCalendarCheckboxes.forEach(function(cb) {
                        cb.checked = calendarParams.includes(cb.value);
                    });
                } else {
                    // No URL params - default to all calendars checked
                    searchCalendarCheckboxes.forEach(function(cb) {
                        cb.checked = true;
                    });
                }

                // Update UI to reflect initial state
                updateSearchCalendarUI();
            })();

            // Get calendar instance function
            function getCalendarInstance() {
                if (window.jobCalendar && window.jobCalendar.calendar) {
                    return window.jobCalendar.calendar;
                }
                return null;
            }

            // Update hidden date inputs when "Events in Current View" is selected
            function updateCurrentViewDates() {
                const currentViewRadio = document.querySelector('.search-date-filter-radio[value="current_view"]');
                if (currentViewRadio && currentViewRadio.checked) {
                    const calendar = getCalendarInstance();
                    if (calendar && calendar.view) {
                        const startDate = calendar.view.currentStart;
                        const endDate = calendar.view.currentEnd;

                        // Format dates as YYYY-MM-DD
                        const formatDate = function(date) {
                            const year = date.getFullYear();
                            const month = String(date.getMonth() + 1).padStart(2, '0');
                            const day = String(date.getDate()).padStart(2, '0');
                            return year + '-' + month + '-' + day;
                        };

                        const startInput = document.getElementById('search-view-start-date');
                        const endInput = document.getElementById('search-view-end-date');
                        if (startInput) startInput.value = formatDate(startDate);
                        if (endInput) endInput.value = formatDate(endDate);
                    }
                }
            }

            // Handle Enter key navigation
            if (searchInput) {
                searchInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();

                        // If search hasn't been submitted yet or input has changed
                        if (!hasSubmitted || this.value !== this.getAttribute('data-last-search')) {
                            // Submit the form
                            this.setAttribute('data-last-search', this.value);
                            hasSubmitted = true;
                            currentHighlightIndex = -1;

                            // Trigger form submission
                            if (searchForm) {
                                const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                                searchForm.dispatchEvent(submitEvent);
                            }
                            return;
                        }

                        // Otherwise, navigate through results
                        if (jobRows.length > 0) {
                            currentHighlightIndex = (currentHighlightIndex + 1) % jobRows.length;
                            highlightRow(currentHighlightIndex);
                        }
                    }
                });

                // Track if search value changes
                searchInput.addEventListener('input', function() {
                    hasSubmitted = false;
                });
            }

            // Handle clear button click
            const clearSearchBtn = document.getElementById('calendar-clear-search-btn');
            if (clearSearchBtn) {
                clearSearchBtn.addEventListener('click', function() {
                    // Clear search input
                    if (searchInput) {
                        searchInput.value = '';
                    }

                    // Check all calendar checkboxes (reset to default: all calendars selected)
                    document.querySelectorAll('.search-calendar-checkbox').forEach(function(cb) {
                        cb.checked = true;
                    });

                    // Reset select-all checkbox to checked (not indeterminate)
                    if (searchCalendarAllCheckbox) {
                        searchCalendarAllCheckbox.checked = true;
                        searchCalendarAllCheckbox.indeterminate = false;
                    }

                    // Update UI via helper
                    updateSearchCalendarUI();

                    // Reset date filter to "All Events"
                    const allEventsRadio = document.querySelector('.search-date-filter-radio[value="all"]');
                    if (allEventsRadio) {
                        allEventsRadio.checked = true;
                    }

                    // Clear search results
                    if (searchResults) {
                        searchResults.innerHTML = '<div class="text-center text-gray-500 py-8">Enter search criteria and click Search to see results.</div>';
                    }

                    // Reset keyboard navigation
                    currentHighlightIndex = -1;
                    hasSubmitted = false;
                });
            }

            // Handle close search area button click
            const closeSearchBtn = document.getElementById('calendar-close-search-btn');
            if (closeSearchBtn) {
                closeSearchBtn.addEventListener('click', function() {
                    if (window.jobCalendar && window.jobCalendar.searchPanelOpen) {
                        window.jobCalendar.toggleSearchPanel();
                    }
                });
            }

            // Handle "Select All Calendars" button click (from no-calendars overlay)
            const selectAllBtn = document.getElementById('calendar-select-all-btn');
            if (selectAllBtn) {
                selectAllBtn.addEventListener('click', function() {
                    if (window.jobCalendar) {
                        window.jobCalendar.selectAllCalendars();
                    }
                });
            }

            // Handle search form submission
            if (searchForm) {
                searchForm.addEventListener('submit', function(e) {
                    e.preventDefault();

                    // Update current view dates if that option is selected
                    updateCurrentViewDates();

                    // Build query parameters
                    const formData = new FormData(searchForm);
                    const params = new URLSearchParams();

                    // Add search term
                    const searchTerm = formData.get('search');
                    if (searchTerm) {
                        params.append('search', searchTerm);
                    }

                    // Add selected calendars
                    const selectedCalendars = [];
                    document.querySelectorAll('.search-calendar-checkbox:checked').forEach(function(cb) {
                        selectedCalendars.push(cb.value);
                    });

                    // If no calendars are selected, show a friendly message and don't search
                    if (selectedCalendars.length === 0) {
                        if (searchResults) {
                            searchResults.innerHTML = '<div class="text-center text-gray-500 py-8"><p class="text-lg font-medium mb-2">No calendars selected</p><p class="text-sm">Please select one or more calendars to search for jobs.</p></div>';
                        }
                        updateJobRows();
                        return;
                    }

                    selectedCalendars.forEach(function(calId) {
                        params.append('calendars', calId);
                    });

                    // Add date filter
                    const dateFilter = document.querySelector('.search-date-filter-radio:checked');
                    if (dateFilter && dateFilter.value !== 'all') {
                        params.append('date_filter', dateFilter.value);

                        if (dateFilter.value === 'current_view') {
                            // Use custom date filter on backend but with current view dates
                            params.set('date_filter', 'custom');
                            const startDate = formData.get('start_date');
                            const endDate = formData.get('end_date');
                            if (startDate) params.append('start_date', startDate);
                            if (endDate) params.append('end_date', endDate);
                        }
                    }

                    // Show loading state
                    if (searchResults) {
                        searchResults.innerHTML = '<div class="text-center text-gray-500 py-8">Searching...</div>';
                    }

                    // Make AJAX request to job list table partial endpoint (no HTML scraping needed)
                    var jobListTableUrl = GTS.urls.jobListTablePartial + '?' + params.toString();
                    fetch(jobListTableUrl, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                        .then(function(response) { return response.text(); })
                        .then(function(html) {
                            // Inject the table fragment directly (no DOMParser needed)
                            if (searchResults) {
                                searchResults.innerHTML = html;

                                // Process HTMX attributes in the injected HTML so load-more button works
                                if (window.htmx && typeof window.htmx.process === 'function') {
                                    window.htmx.process(searchResults);
                                }

                                // Update job rows for keyboard navigation
                                updateJobRows();

                                // Use event delegation for row clicks and hover (more efficient)
                                bindSearchResultsHandlers();

                                // Focus search input after results load
                                if (searchInput) {
                                    searchInput.focus();
                                }
                            }
                        })
                        .catch(function(error) {
                            console.error('Search error:', error);
                            if (searchResults) {
                                searchResults.innerHTML = '<div class="text-center text-red-500 py-8">Error performing search. Please try again.</div>';
                            }
                            updateJobRows();
                        });
                });
            }

            // Bind handlers for search results using event delegation
            function bindSearchResultsHandlers() {
                if (!searchResults) return;

                // Use event delegation - attach once to searchResults container
                if (!GTS.isElInitialized(searchResults, 'search_row_handlers')) {
                    GTS.markElInitialized(searchResults, 'search_row_handlers');

                    searchResults.addEventListener('click', function(e) {
                        const seriesHeaderRow = e.target.closest('.series-header-row');
                        const expandBtn = e.target.closest('.expand-occurrences-btn');
                        const showMoreBtn = e.target.closest('.show-more-occurrences-btn');
                        const showMoreSeriesBtn = e.target.closest('.show-more-series-btn');
                        const jobRow = e.target.closest('.job-row');

                        // Handle grouped-search series header expand/collapse
                        if (seriesHeaderRow) {
                            e.stopPropagation();
                            handleSeriesHeaderClick(seriesHeaderRow);
                            return;
                        }

                        // Handle "Show more" for grouped-search series occurrences
                        if (showMoreSeriesBtn) {
                            e.stopPropagation();
                            handleShowMoreSeriesOccurrences(showMoreSeriesBtn);
                            return;
                        }

                        // Handle expand/collapse button for forever series
                        if (expandBtn) {
                            e.stopPropagation();
                            handleExpandOccurrences(expandBtn, searchResults);
                            return;
                        }

                        // Handle "Show more" button
                        if (showMoreBtn) {
                            e.stopPropagation();
                            handleShowMoreOccurrences(showMoreBtn, searchResults);
                            return;
                        }

                        if (!jobRow) {
                            return;
                        }

                        // Don't navigate if user clicked on an action link or button
                        if (e.target.tagName === 'A' || e.target.closest('a') ||
                            e.target.tagName === 'BUTTON' || e.target.closest('button')) {
                            return;
                        }

                        // Check if this is a virtual occurrence row
                        if (jobRow.getAttribute('data-virtual') === '1') {
                            handleVirtualRowClick(jobRow);
                            return;
                        }

                        const jobId = jobRow.getAttribute('data-job-id');
                        if (jobId && window.JobPanel) {
                            window.JobPanel.setTitle('Edit Job');
                            window.JobPanel.load(GTS.urls.jobCreatePartial({ edit: jobId }));
                        }
                    });

                    searchResults.addEventListener('mouseover', function(e) {
                        const row = e.target.closest('.job-row');
                        if (row && !row.classList.contains('bg-blue-100')) {
                            row.style.backgroundColor = '#f9fafb';
                        }
                    });

                    searchResults.addEventListener('mouseout', function(e) {
                        const row = e.target.closest('.job-row');
                        if (row && !row.classList.contains('bg-blue-100')) {
                            row.style.backgroundColor = '';
                        }
                    });

                    // Listen for HTMX swaps to refresh keyboard navigation cache
                    // This handles load-more appends
                    document.body.addEventListener('htmx:afterSwap', function(event) {
                        // Check if the swap target was the job table body (load-more append)
                        if (event.detail && event.detail.target && 
                            (event.detail.target.id === 'job-table-body' || 
                             (event.detail.target.querySelector && event.detail.target.querySelector('#job-table-body')))) {
                            // Refresh the cached job rows for keyboard navigation
                            updateJobRows();
                        }
                    });
                }
            }

            // ========================================================================
            // SERIES HEADER EXPAND/COLLAPSE (Grouped Search Mode)
            // Uses shared GTS.seriesOccurrencesUI module
            // ========================================================================

            function getSeriesSearchQuery() {
                const direct = (searchInput && typeof searchInput.value === 'string') ? searchInput.value : '';
                if (direct) return direct;
                const urlParams = new URLSearchParams(window.location.search);
                return urlParams.get('search') || '';
            }

            /**
             * Handle click on a series header row to expand/collapse occurrences
             */
            function handleSeriesHeaderClick(headerRow) {
                var promise = GTS.seriesOccurrencesUI.toggle(headerRow, {
                    count: 5,
                    getSearchQuery: getSeriesSearchQuery,
                    rootEl: searchResults || document
                });
                // Update job rows cache after expand completes
                if (promise && typeof promise.then === 'function') {
                    promise.then(function() {
                        updateJobRows();
                    });
                } else {
                    // Collapse is synchronous
                    updateJobRows();
                }
            }

            function handleShowMoreSeriesOccurrences(btn) {
                GTS.seriesOccurrencesUI.showMore(btn, {
                    count: 5,
                    rootEl: searchResults || document
                }).then(function() {
                    updateJobRows();
                });
            }

            /**
             * Handle expand button click to fetch and show virtual occurrences
             */
            function handleExpandOccurrences(btn, container) {
                const parentId = btn.getAttribute('data-parent-id');
                const isExpanded = btn.getAttribute('data-expanded') === 'true';

                if (isExpanded) {
                    collapseOccurrences(parentId, btn, container);
                } else {
                    expandOccurrences(parentId, btn, 5, container);
                }
            }

            /**
             * Expand to show virtual occurrences for a parent
             */
            function expandOccurrences(parentId, btn, count, container) {
                const icon = btn.querySelector('.expand-icon');
                const label = btn.querySelector('.expand-label');
                
                btn.disabled = true;
                if (icon) icon.style.opacity = '0.5';

                const previewUrl = GTS.urls.recurrencePreview + '?parent_id=' + parentId + '&count=' + count;
                
                fetch(previewUrl, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                    .then(function(response) {
                        if (!response.ok) throw new Error('Failed to fetch occurrences');
                        return response.text();
                    })
                    .then(function(html) {
                        const parentRow = container.querySelector('#job-row-' + parentId);
                        if (!parentRow) return;

                        removeVirtualRows(parentId, container);
                        parentRow.insertAdjacentHTML('afterend', html);

                        btn.setAttribute('data-expanded', 'true');
                        btn.setAttribute('aria-expanded', 'true');
                        if (label) label.textContent = 'Hide upcoming';
                        if (icon) {
                            icon.style.transform = 'rotate(180deg)';
                            icon.style.opacity = '1';
                        }
                        btn.title = 'Hide occurrences';
                    })
                    .catch(function(error) {
                        console.error('Error fetching occurrences:', error);
                    })
                    .finally(function() {
                        btn.disabled = false;
                        if (icon) icon.style.opacity = '1';
                    });
            }

            /**
             * Collapse (hide) virtual occurrences for a parent
             */
            function collapseOccurrences(parentId, btn, container) {
                removeVirtualRows(parentId, container);

                const icon = btn.querySelector('.expand-icon');
                const label = btn.querySelector('.expand-label');
                btn.setAttribute('data-expanded', 'false');
                btn.setAttribute('aria-expanded', 'false');
                if (label) label.textContent = 'Show upcoming';
                if (icon) {
                    icon.style.transform = 'rotate(0deg)';
                }
                btn.title = 'Show upcoming occurrences';
            }

            /**
             * Remove all virtual occurrence rows for a given parent
             */
            function removeVirtualRows(parentId, container) {
                const virtualRows = container.querySelectorAll(
                    '.virtual-occurrence-row[data-parent-row-id="job-row-' + parentId + '"]'
                );
                virtualRows.forEach(function(row) {
                    row.remove();
                });
            }

            /**
             * Handle "Show more" button click
             */
            function handleShowMoreOccurrences(btn, container) {
                const parentId = btn.getAttribute('data-parent-id');
                const currentCount = parseInt(btn.getAttribute('data-current-count'), 10) || 5;
                const newCount = currentCount + 5;

                const expandBtn = container.querySelector('.expand-occurrences-btn[data-parent-id="' + parentId + '"]');
                if (expandBtn) {
                    expandOccurrences(parentId, expandBtn, newCount, container);
                }
            }

            /**
             * Handle click on a virtual occurrence row (materialize + open)
             */
            function handleVirtualRowClick(row) {
                const parentId = row.getAttribute('data-recurrence-parent-id');
                const originalStart = row.getAttribute('data-recurrence-original-start');

                if (!parentId || !originalStart) {
                    console.error('Missing parent_id or original_start for virtual row');
                    return;
                }

                row.style.opacity = '0.6';
                row.style.pointerEvents = 'none';

                var csrfToken = '';
                var csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfEl) {
                    csrfToken = csrfEl.value;
                } else {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = cookies[i].trim();
                        if (cookie.startsWith('csrftoken=')) {
                            csrfToken = cookie.substring(10);
                            break;
                        }
                    }
                }

                fetch(GTS.urls.materializeOccurrence, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        parent_id: parseInt(parentId, 10),
                        original_start: originalStart
                    })
                })
                    .then(function(response) {
                        if (!response.ok) {
                            return response.json().then(function(data) {
                                throw new Error(data.error || 'Failed to materialize occurrence');
                            });
                        }
                        return response.json();
                    })
                    .then(function(data) {
                        var jobId = data.job_id;

                        if (window.JobWorkspace) {
                            window.JobWorkspace.openJob(jobId, {
                                customerName: 'Job',
                                trailerColor: '',
                                calendarColor: '#3B82F6'
                            });
                        } else if (window.JobPanel) {
                            window.JobPanel.setTitle('Edit Job');
                            window.JobPanel.load(GTS.urls.jobCreatePartial({ edit: jobId }));
                        }

                        if (data.created) {
                            row.remove();
                        }
                    })
                    .catch(function(error) {
                        console.error('Error materializing virtual occurrence:', error);
                        row.style.opacity = '1';
                        row.style.pointerEvents = '';
                    });
            }
        });
    }

    // ========================================================================
    // ENTRY POINT
    // ========================================================================

    // Initialize when DOM is ready
    GTS.onDomReady(initCalendarPage);

})();
