/**
 * Panel Shell Entrypoint
 * 
 * Extracted from includes/panel.html inline script.
 * Handles:
 * - htmx:load "refresh" binding for .panel-body
 * - Panel resize handles (right, bottom, corner)
 * - Persistence to localStorage (gts-panel-width, gts-panel-height)
 * 
 * Note: Main panel logic (open/close, dragging, etc.) is in panel.js
 * 
 * Requires: GTS.initOnce
 */
(function() {
    'use strict';

    GTS.onDomReady(function() {
        initPanelRefreshBinding();
        initPanelResize();
    });

    // ========================================================================
    // HTMX REFRESH BINDING
    // ========================================================================

    function initPanelRefreshBinding() {
        GTS.initOnce('panel_shell_refresh', function() {
            document.addEventListener('htmx:load', function() {
                document.querySelectorAll('#job-panel .panel-body').forEach(function(el) {
                    el.addEventListener('refresh', function() {
                        const hxGet = el.getAttribute('hx-get');
                        if (hxGet) {
                            htmx.ajax('GET', hxGet, { target: el });
                        }
                    });
                });
            });
        });
    }

    // ========================================================================
    // PANEL RESIZE
    // ========================================================================

    function initPanelResize() {
        GTS.initOnce('panel_shell_resize', function() {
            const panel = document.getElementById('job-panel');
            const handleRight = document.getElementById('panel-resize-handle-right');
            const handleBottom = document.getElementById('panel-resize-handle-bottom');
            const handleCorner = document.getElementById('panel-resize-handle-corner');

            if (!panel || !handleRight || !handleBottom || !handleCorner) return;

            const STORAGE_KEY_WIDTH = 'gts-panel-width';
            const STORAGE_KEY_HEIGHT = 'gts-panel-height';
            const MIN_WIDTH = 200;
            const MAX_WIDTH = window.innerWidth * 0.95;
            const MIN_HEIGHT = 100;
            const MAX_HEIGHT = window.innerHeight * 0.99;

            // Load saved dimensions
            const savedWidth = localStorage.getItem(STORAGE_KEY_WIDTH);
            const savedHeight = localStorage.getItem(STORAGE_KEY_HEIGHT);
            if (savedWidth) {
                panel.style.width = savedWidth + 'px';
            }
            if (savedHeight) {
                panel.style.height = savedHeight + 'px';
            }

            let isResizing = false;
            let resizeDirection = '';
            let startX = 0;
            let startY = 0;
            let startWidth = 0;
            let startHeight = 0;

            // Right edge resize
            handleRight.addEventListener('mousedown', function(e) {
                startResize(e, 'right');
            });

            // Bottom edge resize
            handleBottom.addEventListener('mousedown', function(e) {
                startResize(e, 'bottom');
            });

            // Corner resize (both directions)
            handleCorner.addEventListener('mousedown', function(e) {
                startResize(e, 'corner');
            });

            function startResize(e, direction) {
                isResizing = true;
                resizeDirection = direction;
                startX = e.clientX;
                startY = e.clientY;
                startWidth = panel.offsetWidth;
                startHeight = panel.offsetHeight;

                if (direction === 'right' || direction === 'corner') {
                    handleRight.classList.add('active');
                }
                if (direction === 'bottom' || direction === 'corner') {
                    handleBottom.classList.add('active');
                }

                document.body.style.cursor = direction === 'right' ? 'ew-resize' :
                    direction === 'bottom' ? 'ns-resize' :
                    'nwse-resize';
                document.body.style.userSelect = 'none';
                e.preventDefault();
                e.stopPropagation();
            }

            document.addEventListener('mousemove', function(e) {
                if (!isResizing) return;

                if (resizeDirection === 'right' || resizeDirection === 'corner') {
                    const deltaX = e.clientX - startX;
                    let newWidth = startWidth + deltaX;
                    newWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, newWidth));
                    panel.style.width = newWidth + 'px';
                }

                if (resizeDirection === 'bottom' || resizeDirection === 'corner') {
                    const deltaY = e.clientY - startY;
                    let newHeight = startHeight + deltaY;
                    newHeight = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT, newHeight));
                    panel.style.height = newHeight + 'px';
                }
            });

            document.addEventListener('mouseup', function() {
                if (isResizing) {
                    isResizing = false;
                    handleRight.classList.remove('active');
                    handleBottom.classList.remove('active');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';

                    // Constrain panel to viewport after resize
                    constrainPanelToViewport();

                    // Save dimensions to localStorage
                    localStorage.setItem(STORAGE_KEY_WIDTH, panel.offsetWidth);
                    localStorage.setItem(STORAGE_KEY_HEIGHT, panel.offsetHeight);
                }
            });

            /**
             * Constrain panel to viewport bounds
             */
            function constrainPanelToViewport() {
                const rect = panel.getBoundingClientRect();
                const viewportHeight = window.innerHeight;
                const viewportWidth = window.innerWidth;

                // If panel extends beyond bottom of viewport, constrain its height
                if (rect.bottom > viewportHeight - 20) {
                    const availableHeight = viewportHeight - rect.top - 20;
                    if (availableHeight > MIN_HEIGHT) {
                        panel.style.height = availableHeight + 'px';
                        panel.style.maxHeight = availableHeight + 'px';
                    }
                }

                // Ensure panel doesn't exceed viewport width
                if (rect.right > viewportWidth - 20) {
                    const availableWidth = viewportWidth - rect.left - 20;
                    if (availableWidth > MIN_WIDTH) {
                        panel.style.width = availableWidth + 'px';
                    }
                }
            }

            // Observe when panel becomes visible and constrain it
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        if (!panel.classList.contains('hidden')) {
                            // Panel just became visible, constrain to viewport
                            setTimeout(constrainPanelToViewport, 10);
                        }
                    }
                });
            });
            observer.observe(panel, { attributes: true });
        });
    }

})();
