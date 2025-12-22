/**
 * Calendar Events Module
 * 
 * Handles event fetching, caching (stale-while-revalidate), and refresh logic.
 * Registers: _buildEventsCacheKey, _computeEventsSignature, _getCachedEvents,
 *            _setCachedEvents, _touchCacheTimestamp, _cleanupEventCache,
 *            fetchEvents, _backgroundRefetch, invalidateEventsCache, debouncedRefetch,
 *            refreshCalendar, loadCalendarData, showLoading, hideLoading,
 *            updateNoCalendarsOverlay
 */
(function() {
    'use strict';

    GTS.calendar.register('events', function(proto) {
        /**
         * Build a cache key for localStorage event caching
         */
        proto._buildEventsCacheKey = function(startStr, endStr, calendarIds, statusFilter, searchFilter) {
            // Normalize the key components
            var parts = [
                'cal-events-cache',
                startStr.split('T')[0], // Date only
                endStr.split('T')[0],
                calendarIds || '',
                statusFilter || '',
                searchFilter || ''
            ];
            return parts.join(':');
        };

        /**
         * Compute a stable signature/hash for an events array.
         * Used to detect if cached events differ from fresh events.
         */
        proto._computeEventsSignature = function(events) {
            if (!events || events.length === 0) return 'empty';

            // Build a signature from key event properties
            // Sort by id first for stability
            var sorted = events.slice().sort(function(a, b) {
                var aId = String(a.id || '');
                var bId = String(b.id || '');
                return aId.localeCompare(bId);
            });

            // Create signature string from essential properties
            var parts = sorted.map(function(ev) {
                var id = ev.id || '';
                var start = ev.start || '';
                var end = ev.end || '';
                var title = ev.title || '';
                var bg = ev.backgroundColor || '';
                return id + '|' + start + '|' + end + '|' + title + '|' + bg;
            });

            // Simple hash: join and compute a numeric hash
            var str = parts.join(';;');
            var hash = 0;
            for (var i = 0; i < str.length; i++) {
                var char = str.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash; // Convert to 32-bit integer
            }
            return 'sig:' + events.length + ':' + hash;
        };

        /**
         * Try to get cached events from localStorage
         * Returns object with { events, signature } or null if no valid cache found
         */
        proto._getCachedEvents = function(cacheKey) {
            try {
                var cached = localStorage.getItem(cacheKey);
                if (!cached) return null;

                var data = JSON.parse(cached);
                var events = data.events;
                var signature = data.signature;
                var timestamp = data.timestamp;

                // Cache valid for 5 minutes (300000ms)
                var maxAge = 5 * 60 * 1000;
                if (Date.now() - timestamp > maxAge) {
                    localStorage.removeItem(cacheKey);
                    return null;
                }

                return { events: events, signature: signature };
            } catch (e) {
                return null;
            }
        };

        /**
         * Store events in localStorage cache with signature
         */
        proto._setCachedEvents = function(cacheKey, events, signature) {
            try {
                // Compute signature if not provided
                var sig = signature || this._computeEventsSignature(events);

                var cacheData = {
                    events: events,
                    signature: sig,
                    timestamp: Date.now()
                };
                localStorage.setItem(cacheKey, JSON.stringify(cacheData));

                // Clean up old cache entries (keep only last 5 to limit storage use)
                this._cleanupEventCache(cacheKey);
            } catch (e) {
                // Ignore storage errors (quota exceeded, etc.)
                console.debug('[PERF] Cache write failed:', e.message);
            }
        };

        /**
         * Update only the timestamp on an existing cache entry (no re-render needed)
         */
        proto._touchCacheTimestamp = function(cacheKey) {
            try {
                var cached = localStorage.getItem(cacheKey);
                if (!cached) return;

                var data = JSON.parse(cached);
                data.timestamp = Date.now();
                localStorage.setItem(cacheKey, JSON.stringify(data));
            } catch (e) {
                // Ignore errors
            }
        };

        /**
         * Clean up old event cache entries
         */
        proto._cleanupEventCache = function(currentKey) {
            try {
                var cacheKeys = [];
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    if (key && key.startsWith('cal-events-cache:') && key !== currentKey) {
                        cacheKeys.push(key);
                    }
                }

                // Keep only the 4 most recent (plus current = 5 total)
                if (cacheKeys.length > 4) {
                    // Sort by timestamp (oldest first)
                    cacheKeys.sort(function(a, b) {
                        try {
                            var aData = JSON.parse(localStorage.getItem(a) || '{}');
                            var bData = JSON.parse(localStorage.getItem(b) || '{}');
                            return (aData.timestamp || 0) - (bData.timestamp || 0);
                        } catch (e) {
                            return 0;
                        }
                    });

                    // Remove oldest entries
                    var toRemove = cacheKeys.slice(0, cacheKeys.length - 4);
                    toRemove.forEach(function(k) {
                        localStorage.removeItem(k);
                    });
                }
            } catch (e) {
                // Ignore cleanup errors
            }
        };

        /**
         * Fetch events from the server
         * OPTIMIZED: Uses localStorage cache with stale-while-revalidate for instant page reload
         */
        proto.fetchEvents = function(info, successCallback, failureCallback) {
            var self = this;
            // Performance instrumentation
            var perfEnabled = typeof performance !== 'undefined' && performance.mark;
            if (perfEnabled) {
                performance.mark('cal-fetch-start');
            }

            // If no calendars are selected, return empty events immediately (no network request)
            if (!this.selectedCalendars || this.selectedCalendars.size === 0) {
                successCallback([]);
                this.updateNoCalendarsOverlay(true);
                return;
            }

            // Hide the no-calendars overlay since we have calendars selected
            this.updateNoCalendarsOverlay(false);

            // Build params with selected calendars
            var params = new URLSearchParams({
                start: info.startStr,
                end: info.endStr
            });

            // Add selected calendars as comma-separated string
            var calendarIds = Array.from(this.selectedCalendars).join(',');
            params.append('calendar', calendarIds);

            // Add other filters
            if (this.currentFilters.status) {
                params.append('status', this.currentFilters.status);
            }
            if (this.currentFilters.search) {
                params.append('search', this.currentFilters.search);
            }

            // Build cache key
            var cacheKey = this._buildEventsCacheKey(
                info.startStr, info.endStr, calendarIds,
                this.currentFilters.status, this.currentFilters.search
            );

            // Check for one-shot override from background revalidation (avoids double-fetch)
            if (this._overrideEventsOnce && this._overrideEventsOnce[cacheKey]) {
                var overrideEvents = this._overrideEventsOnce[cacheKey];
                delete this._overrideEventsOnce[cacheKey];
                if (perfEnabled) {
                    console.debug('[PERF] Calendar: ' + overrideEvents.length + ' events from override (no network)');
                }
                // Yield a frame before heavy render work
                requestAnimationFrame(function() {
                    successCallback(overrideEvents);
                });
                return;
            }

            // STALE-WHILE-REVALIDATE: Check cache first
            var cachedData = this._getCachedEvents(cacheKey);
            if (cachedData && !this._forceRefresh) {
                var cachedEvents = cachedData.events;
                var cachedSignature = cachedData.signature;
                // Return cached data via rAF to yield a frame before heavy render work
                if (perfEnabled) {
                    console.debug('[PERF] Calendar: ' + cachedEvents.length + ' events from cache (instant)');
                }
                requestAnimationFrame(function() {
                    successCallback(cachedEvents);
                });

                // Still fetch in background to revalidate (but don't show spinner)
                this._backgroundRefetch(info, cacheKey, cachedSignature, perfEnabled);
                return;
            }

            // No cache or forced refresh - show loading and fetch
            this.showLoading();

            // Use the calendar events URL from GTS.urls (canonical source)
            var apiUrl = GTS.urls.calendarEvents;
            if (!apiUrl) {
                console.error('[Calendar] No calendar events URL configured');
                failureCallback('Calendar events URL not configured');
                return;
            }

            var fullUrl = apiUrl + '?' + params;

            // Abort any in-flight request before starting a new one
            if (this.fetchAbortController) {
                this.fetchAbortController.abort();
            }
            this.fetchAbortController = new AbortController();

            fetch(fullUrl, {
                headers: {
                    'Accept': 'application/json'
                },
                signal: this.fetchAbortController.signal
            })
                .then(function(response) {
                    // Mark when response headers arrive
                    if (perfEnabled) {
                        performance.mark('cal-response-received');
                    }

                    return response.text().then(function(text) {
                        var contentType = response.headers.get('content-type') || '';

                        // Check for non-OK status
                        if (!response.ok) {
                            var snippet = text.substring(0, 200);
                            console.error('JobCalendar: HTTP ' + response.status + ' from ' + fullUrl);
                            console.error('  Content-Type: ' + contentType);
                            console.error('  Body snippet: ' + snippet);
                            throw new Error('Server returned HTTP ' + response.status);
                        }

                        // Check for empty body
                        if (!text || text.trim() === '') {
                            console.error('JobCalendar: Empty response from ' + fullUrl);
                            console.error('  Content-Type: ' + contentType);
                            // Return empty events rather than failing
                            return { status: 'success', events: [] };
                        }

                        // Try to parse JSON
                        try {
                            if (perfEnabled) {
                                performance.mark('cal-json-parse-start');
                            }
                            var data = JSON.parse(text);
                            if (perfEnabled) {
                                performance.mark('cal-json-parse-end');
                            }
                            return data;
                        } catch (parseError) {
                            var snippet2 = text.substring(0, 200);
                            console.error('JobCalendar: JSON parse failed for ' + fullUrl);
                            console.error('  Content-Type: ' + contentType);
                            console.error('  Body snippet: ' + snippet2);
                            console.error('  Parse error: ' + parseError.message);
                            throw new Error('Invalid JSON response from server');
                        }
                    });
                })
                .then(function(data) {
                    if (data.status === 'success') {
                        var events = data.events || [];

                        // Cache the events for future instant loads
                        self._setCachedEvents(cacheKey, events);

                        // Performance logging
                        if (perfEnabled) {
                            performance.mark('cal-data-ready');
                            console.debug('[PERF] Calendar: ' + events.length + ' events received (network)');
                        }

                        // Hide loading overlay BEFORE handing events to FullCalendar
                        self.hideLoading();

                        requestAnimationFrame(function() {
                            successCallback(events);
                        });
                    } else {
                        self.hideLoading();
                        console.error('JobCalendar: API error', data.error);
                        failureCallback(data.error || 'Unknown API error');
                    }
                })
                .catch(function(error) {
                    self.hideLoading();
                    // Ignore abort errors (expected when navigation happens during fetch)
                    if (error.name === 'AbortError') {
                        console.debug('JobCalendar: Fetch aborted (superseded by newer request)');
                        return;
                    }
                    console.error('JobCalendar: Fetch failed', error);
                    // Return empty events so calendar doesn't break completely
                    successCallback([]);
                });
        };

        /**
         * Background refetch for stale-while-revalidate
         * Fetches fresh data silently and updates calendar ONLY if data changed
         */
        proto._backgroundRefetch = function(info, cacheKey, cachedSignature, perfEnabled) {
            var self = this;
            // Use the calendar events URL from GTS.urls (canonical source)
            var apiUrl = GTS.urls.calendarEvents;
            if (!apiUrl) {
                console.error('[Calendar] No calendar events URL configured for background refetch');
                return;
            }

            // Build params
            var params = new URLSearchParams({
                start: info.startStr,
                end: info.endStr
            });
            var calendarIds = Array.from(this.selectedCalendars).join(',');
            params.append('calendar', calendarIds);
            if (this.currentFilters.status) params.append('status', this.currentFilters.status);
            if (this.currentFilters.search) params.append('search', this.currentFilters.search);

            var fullUrl = apiUrl + '?' + params;

            // Use a separate AbortController for background fetch
            var bgController = new AbortController();

            fetch(fullUrl, {
                headers: { 'Accept': 'application/json' },
                signal: bgController.signal
            })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.status === 'success') {
                        var freshEvents = data.events || [];
                        var freshSignature = self._computeEventsSignature(freshEvents);

                        if (perfEnabled) {
                            console.debug('[PERF] Background revalidation: ' + freshEvents.length + ' events');
                        }

                        // Compare signatures to detect if data actually changed
                        if (freshSignature === cachedSignature) {
                            // Data unchanged - just refresh the cache timestamp, NO re-render
                            self._touchCacheTimestamp(cacheKey);
                            if (perfEnabled) {
                                console.debug('[PERF] Background revalidation: data unchanged, skipping re-render');
                            }
                            return;
                        }

                        // Data changed - update cache with fresh data and signature
                        self._setCachedEvents(cacheKey, freshEvents, freshSignature);

                        if (perfEnabled) {
                            console.debug('[PERF] Background revalidation: data CHANGED, triggering re-render');
                        }

                        // Check if current view still matches this fetch
                        if (self.calendar) {
                            var currentView = self.calendar.view;
                            if (currentView && currentView.activeStart && currentView.activeEnd) {
                                var viewStart = currentView.activeStart.toISOString();
                                var viewEnd = currentView.activeEnd.toISOString();

                                // Only update if view hasn't changed
                                if (viewStart.split('T')[0] === info.startStr.split('T')[0] &&
                                    viewEnd.split('T')[0] === info.endStr.split('T')[0]) {
                                    // Use one-shot override to avoid double-fetch
                                    if (!self._overrideEventsOnce) {
                                        self._overrideEventsOnce = {};
                                    }
                                    self._overrideEventsOnce[cacheKey] = freshEvents;

                                    // Trigger re-render (fetchEvents will use override, not network)
                                    self.calendar.refetchEvents();
                                }
                            }
                        }
                    }
                })
                .catch(function(error) {
                    // Silently ignore background fetch errors
                    if (error.name !== 'AbortError') {
                        console.debug('[PERF] Background revalidation failed:', error.message);
                    }
                });
        };

        /**
         * Invalidate the events cache
         * Call this after mutations (job create/update/delete)
         */
        proto.invalidateEventsCache = function() {
            try {
                // Clear all event cache entries
                var keysToRemove = [];
                for (var i = 0; i < localStorage.length; i++) {
                    var key = localStorage.key(i);
                    if (key && key.startsWith('cal-events-cache:')) {
                        keysToRemove.push(key);
                    }
                }
                keysToRemove.forEach(function(k) {
                    localStorage.removeItem(k);
                });
                console.debug('[PERF] Events cache invalidated');
            } catch (e) {
                // Ignore errors
            }
        };

        /**
         * Debounced refetch - prevents rapid successive refetch calls
         */
        proto.debouncedRefetch = function() {
            var self = this;
            if (this.refetchDebounceTimer) {
                clearTimeout(this.refetchDebounceTimer);
            }
            this.refetchDebounceTimer = setTimeout(function() {
                self.refetchDebounceTimer = null;
                if (self.calendar) {
                    // Force fresh fetch, bypassing cache
                    self._forceRefresh = true;
                    self.calendar.refetchEvents();
                    self._forceRefresh = false;
                }
            }, this.refetchDebounceMs);
        };

        /**
         * Refresh the calendar data
         */
        proto.refreshCalendar = function() {
            if (this.calendar) {
                this._forceRefresh = true;
                this.invalidateEventsCache();
                this.calendar.refetchEvents();
                this._forceRefresh = false;
            }
        };

        /**
         * Load calendar data (legacy method - now handled by FullCalendar)
         */
        proto.loadCalendarData = function() {
            if (this.calendar) {
                this.calendar.refetchEvents();
            }
        };

        /**
         * Show loading indicator
         */
        proto.showLoading = function() {
            if (this.loadingEl) {
                this.loadingEl.classList.remove('hidden');
            }
        };

        /**
         * Hide loading indicator
         */
        proto.hideLoading = function() {
            if (this.loadingEl) {
                this.loadingEl.classList.add('hidden');
            }
        };

        /**
         * Update the no-calendars overlay visibility
         * @param {boolean} show - Whether to show the overlay
         */
        proto.updateNoCalendarsOverlay = function(show) {
            if (!this.noCalendarsOverlay) {
                this.noCalendarsOverlay = document.getElementById('calendar-no-calendars');
            }
            if (this.noCalendarsOverlay) {
                if (show) {
                    this.noCalendarsOverlay.classList.remove('hidden');
                } else {
                    this.noCalendarsOverlay.classList.add('hidden');
                }
            }
        };
    });

})();
