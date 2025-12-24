/**
 * GTS Shared DOM Module
 * 
 * Provides safe event binding and delegation helpers.
 * 
 * Usage:
 *   GTS.dom.on(el, 'click', handler, options?)           // Direct binding
 *   GTS.dom.on(el, 'click', '.selector', handler, options?)  // Delegated binding
 *   GTS.dom.closest(el, selector) -> element|null
 *   GTS.dom.stop(event) -> void  // preventDefault + stopPropagation
 */
(function() {
    'use strict';

    // Ensure GTS namespace exists
    window.GTS = window.GTS || {};

    /**
     * Add an event listener with optional delegation.
     * 
     * Signatures:
     *   on(el, eventName, handler, options?)           // Direct
     *   on(el, eventName, selector, handler, options?) // Delegated
     * 
     * @param {HTMLElement|Document} el - Element to attach listener to
     * @param {string} eventName - Event name (e.g., 'click', 'change')
     * @param {string|Function} selectorOrHandler - CSS selector for delegation, or handler function
     * @param {Function|Object} [handlerOrOptions] - Handler function (if delegated), or options
     * @param {Object} [options] - addEventListener options (passive, capture, once)
     */
    function on(el, eventName, selectorOrHandler, handlerOrOptions, options) {
        if (!el || !eventName) return;

        // Detect if this is delegated mode
        var isDelegated = typeof selectorOrHandler === 'string';
        var selector, handler, listenerOptions;

        if (isDelegated) {
            selector = selectorOrHandler;
            handler = handlerOrOptions;
            listenerOptions = options;
        } else {
            // Direct mode: selectorOrHandler is the handler
            handler = selectorOrHandler;
            listenerOptions = handlerOrOptions;
        }

        if (typeof handler !== 'function') {
            console.warn('GTS.dom.on: handler must be a function');
            return;
        }

        if (isDelegated) {
            // Delegated event handler
            el.addEventListener(eventName, function(e) {
                var target = e.target;
                if (!target) return;

                // Find the closest matching element
                var matchedEl = target.closest ? target.closest(selector) : null;
                if (matchedEl && el.contains(matchedEl)) {
                    handler.call(matchedEl, e, matchedEl);
                }
            }, listenerOptions);
        } else {
            // Direct event handler
            el.addEventListener(eventName, handler, listenerOptions);
        }
    }

    /**
     * Find the closest ancestor matching a selector.
     * Polyfill-safe wrapper around Element.closest().
     * 
     * @param {HTMLElement} el - Starting element
     * @param {string} selector - CSS selector
     * @returns {HTMLElement|null}
     */
    function closest(el, selector) {
        if (!el) return null;

        // Use native closest if available
        if (el.closest) {
            return el.closest(selector);
        }

        // Polyfill for older browsers
        var current = el;
        while (current && current !== document) {
            if (current.matches && current.matches(selector)) {
                return current;
            }
            current = current.parentElement;
        }
        return null;
    }

    /**
     * Stop event propagation and prevent default.
     * Convenience helper for common pattern.
     * 
     * @param {Event} e - Event object
     */
    function stop(e) {
        if (!e) return;
        if (e.preventDefault) e.preventDefault();
        if (e.stopPropagation) e.stopPropagation();
    }

    /**
     * Query a single element, optionally scoped to a root.
     * @param {string} selector
     * @param {HTMLElement} [root=document]
     * @returns {HTMLElement|null}
     */
    function qs(selector, root) {
        root = root || document;
        return root.querySelector(selector);
    }

    /**
     * Query all elements matching selector, optionally scoped to a root.
     * @param {string} selector
     * @param {HTMLElement} [root=document]
     * @returns {HTMLElement[]}
     */
    function qsa(selector, root) {
        root = root || document;
        return Array.from(root.querySelectorAll(selector));
    }

    // Expose the DOM module
    GTS.dom = {
        on: on,
        closest: closest,
        stop: stop,
        qs: qs,
        qsa: qsa
    };

})();
