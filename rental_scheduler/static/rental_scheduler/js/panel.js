// rental_scheduler/static/rental_scheduler/js/panel.js
(function () {
  function clamp(n, min, max){ return Math.max(min, Math.min(max, n)); }
  const STORAGE_KEY = 'jobPanelState';

  // Initialize global API immediately
  let panelInstance = null;
  let isAlpineMode = false;
  
  // Queue for operations before panel is ready
  let operationQueue = [];
  
  function executeOperation(op) {
    if (panelInstance) {
      op();
    } else {
      operationQueue.push(op);
    }
  }
  
  function flushQueue() {
    while (operationQueue.length > 0) {
      const op = operationQueue.shift();
      op();
    }
  }
  
  // Vanilla JS fallback implementation
  function createVanillaPanel() {
    const panelEl = document.getElementById('job-panel');
    if (!panelEl) {
      console.error('Panel element not found');
      return null;
    }
    
    const st = load() || {};
    const panel = {
      isOpen: st.isOpen || false,
      title: st.title || 'Job',
      x: st.x || 80,
      y: st.y || 80,
      w: st.w || 520,
      h: st.h || null,
      docked: st.docked || false,
      dragging: false,
      sx: 0,
      sy: 0,
      currentJobId: null, // Track current job for workspace integration
      
      updateVisibility() {
        if (this.isOpen) {
          panelEl.classList.remove('hidden');
          panelEl.classList.add('block');
        } else {
          panelEl.classList.add('hidden');
          panelEl.classList.remove('block');
        }
      },
      
      updatePosition() {
        if (this.docked) {
          panelEl.style.top = '80px';
          panelEl.style.right = '16px';
          panelEl.style.left = 'auto';
          panelEl.style.transform = 'none';
        } else {
          panelEl.style.top = '0';
          panelEl.style.left = '0';
          panelEl.style.transform = `translate(${this.x}px, ${this.y}px)`;
        }
        this.constrainToViewport();
      },
      
      constrainToViewport() {
        const rect = panelEl.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // If panel extends beyond bottom of viewport, constrain its height
        if (rect.bottom > viewportHeight) {
          const availableHeight = viewportHeight - rect.top - 20; // 20px margin
          if (availableHeight > 100) { // min-height
            panelEl.style.height = availableHeight + 'px';
            panelEl.style.maxHeight = availableHeight + 'px';
          } else {
            // Move panel up if there's not enough space
            const newY = Math.max(20, viewportHeight - parseInt(panelEl.style.height || 200) - 20);
            this.y = newY;
            panelEl.style.transform = `translate(${this.x}px, ${this.y}px)`;
          }
        }
        
        // Ensure panel doesn't exceed viewport width
        if (rect.right > viewportWidth) {
          const availableWidth = viewportWidth - rect.left - 20;
          if (availableWidth > 200) { // min-width
            panelEl.style.width = availableWidth + 'px';
          }
        }
      },
      
      open() {
        this.isOpen = true;
        this.updateVisibility();
        save(this);
      },
      
      close(skipUnsavedCheck) {
        // Check for unsaved changes before closing (unless explicitly skipped)
        if (!skipUnsavedCheck && this.hasUnsavedChanges()) {
          if (!confirm('You have unsaved changes. Are you sure you want to close without saving?')) {
            return; // User cancelled, don't close
          }
        }
        
        this.isOpen = false;
        this.updateVisibility();
        this.currentJobId = null; // Clear current job ID when closing
        this.updateMinimizeButton(); // Hide minimize button
        save(this);
      },
      
      setTitle(t) {
        this.title = t || 'Job';
        const titleEl = document.getElementById('job-panel-title');
        if (titleEl) titleEl.textContent = this.title;
        save(this);
      },
      
      setCurrentJobId(jobId) {
        this.currentJobId = jobId;
        this.updateMinimizeButton();
      },
      
      updateMinimizeButton() {
        const minimizeBtn = document.getElementById('panel-workspace-minimize-btn');
        if (!minimizeBtn) return;
        
        // Show minimize button only if this job is in the workspace
        if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
          minimizeBtn.style.display = 'inline-flex';
        } else {
          minimizeBtn.style.display = 'none';
        }
      },
      
      toggleDock() {
        this.docked = !this.docked;
        this.updatePosition();
        save(this);
      },
      
      setupDragging() {
        const header = panelEl.querySelector('.panel-header');
        if (!header) return;
        
        const onMouseDown = (e) => {
          if (this.docked) return;
          const p = e.touches?.[0] ?? e;
          this.dragging = true;
          this.sx = p.clientX - this.x;
          this.sy = p.clientY - this.y;
          
          document.addEventListener('mousemove', onMouseMove);
          document.addEventListener('mouseup', onMouseUp);
          document.addEventListener('touchmove', onMouseMove, {passive: false});
          document.addEventListener('touchend', onMouseUp);
        };
        
        const onMouseMove = (ev) => {
          if (!this.dragging) return;
          const p = ev.touches?.[0] ?? ev;
          const maxX = window.innerWidth - 200;
          const maxY = window.innerHeight - 48;
          this.x = clamp(p.clientX - this.sx, 8, maxX);
          this.y = clamp(p.clientY - this.sy, 8, maxY);
          this.updatePosition();
          ev.preventDefault();
        };
        
        const onMouseUp = () => {
          this.dragging = false;
          document.removeEventListener('mousemove', onMouseMove);
          document.removeEventListener('mouseup', onMouseUp);
          document.removeEventListener('touchmove', onMouseMove);
          document.removeEventListener('touchend', onMouseUp);
          save(this);
        };
        
        header.addEventListener('mousedown', onMouseDown);
        header.addEventListener('touchstart', onMouseDown, {passive: true});
      },
      
      hasUnsavedChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return false;
        
        // Check for any form inputs that have been modified
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        for (const input of inputs) {
          // Skip hidden inputs and buttons
          if (input.type === 'hidden' || input.type === 'submit' || input.type === 'button') {
            continue;
          }
          
          // Check if the current value differs from the original value
          if (input.hasAttribute('data-original-value')) {
            const originalValue = input.getAttribute('data-original-value');
            const currentValue = input.value;
            if (originalValue !== currentValue) {
              return true;
            }
          } else if (input.value !== '') {
            // If no original value stored but input has a value, it might be a change
            // This is a fallback for inputs that weren't tracked from the start
            return true;
          }
        }
        
        return false;
      },
      
      trackFormChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return;
        
        // Store original values for all form inputs
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },
      
      clearUnsavedChanges() {
        // Reset tracking by updating all original values to current values
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return;
        
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },
      
      saveForm(callback) {
        // Find the form in the panel body and submit it
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) {
          console.warn('Panel body not found');
          if (callback) callback();
          return;
        }
        
        const form = panelBody.querySelector('form');
        if (!form) {
          console.warn('Form not found in panel');
          if (callback) callback();
          return;
        }
        
        // Trigger HTMX form submission if available
        if (typeof htmx !== 'undefined') {
          // Set up a one-time listener for after the request completes
          const afterRequestHandler = (event) => {
            if (event.detail.successful) {
              // Clear unsaved changes tracking
              this.clearUnsavedChanges();
              // Execute callback
              if (callback) callback();
            } else {
              console.error('Form submission failed');
              if (callback) callback(); // Still execute callback even on error
            }
            // Remove the event listener
            form.removeEventListener('htmx:afterRequest', afterRequestHandler);
          };
          
          form.addEventListener('htmx:afterRequest', afterRequestHandler);
          
          // Trigger HTMX request
          htmx.trigger(form, 'submit');
        } else {
          // Fallback: regular form submission
          form.submit();
          if (callback) callback();
        }
      },
      
      setupButtons() {
        // Close button
        const closeBtn = panelEl.querySelector('.panel-header .btn-close');
        if (closeBtn) {
          closeBtn.addEventListener('click', () => {
            // If there are unsaved changes, save first
            if (this.hasUnsavedChanges()) {
              this.saveForm(() => {
                // After saving, close/remove from workspace
                if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
                  window.JobWorkspace.closeJob(this.currentJobId);
                } else {
                  this.close(true);
                }
              });
            } else {
              // No unsaved changes, just close
              if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
                window.JobWorkspace.closeJob(this.currentJobId);
              } else {
                this.close(true);
              }
            }
          });
        }
        
        // Workspace minimize button
        const workspaceMinimizeBtn = document.getElementById('panel-workspace-minimize-btn');
        if (workspaceMinimizeBtn) {
          workspaceMinimizeBtn.addEventListener('click', () => {
            // If there are unsaved changes, save first
            if (this.hasUnsavedChanges()) {
              this.saveForm(() => {
                // After saving, minimize
                if (this.currentJobId && window.JobWorkspace) {
                  window.JobWorkspace.minimizeJob(this.currentJobId);
                }
              });
            } else {
              // No unsaved changes, just minimize
              if (this.currentJobId && window.JobWorkspace) {
                window.JobWorkspace.minimizeJob(this.currentJobId);
              }
            }
          });
        }
        
        // Delete button is handled by the global API via setDeleteCallback
        
        // ESC key
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && this.isOpen) {
            // If there are unsaved changes, save first
            if (this.hasUnsavedChanges()) {
              this.saveForm(() => {
                // After saving, close/remove from workspace
                if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
                  window.JobWorkspace.closeJob(this.currentJobId);
                } else {
                  this.close(true);
                }
              });
            } else {
              // No unsaved changes, just close
              if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
                window.JobWorkspace.closeJob(this.currentJobId);
              } else {
                this.close(true);
              }
            }
          }
        });
        
        // Enter key navigation within panel
        document.addEventListener('keydown', (e) => {
          // Only apply when panel is open
          if (!panelEl || !this.isOpen) return;
          
          // Check if the focused element is inside the panel
          if (!panelEl.contains(e.target)) return;
          
          if (e.key === 'Enter') {
            const target = e.target;
            
            // Allow normal Enter in textarea (for new lines) unless Shift is pressed
            if (target.tagName === 'TEXTAREA' && !e.shiftKey) {
              return;
            }
            
            // Prevent default Enter behavior
            e.preventDefault();
            
            // Get all focusable fields within the panel
            const fields = Array.from(panelEl.querySelectorAll('input, select, textarea, button'))
              .filter(el => {
                // Filter out hidden, disabled, or invisible elements
                return !el.disabled && 
                       el.offsetParent !== null && 
                       el.type !== 'hidden' &&
                       !el.hasAttribute('readonly');
              });
            
            const idx = fields.indexOf(target);
            
            if (idx > -1 && idx < fields.length - 1) {
              // Move to next field
              fields[idx + 1].focus();
            } else if (idx === fields.length - 1 && target.form) {
              // Last field → submit the form
              target.form.requestSubmit();
            }
          }
        });
      },
      
      init() {
        this.updatePosition();
        this.updateVisibility();
        this.setupDragging();
        this.setupButtons();
      }
    };
    
    panel.init();
    return panel;
  }
  
  window.JobPanel = {
    open: () => {
      executeOperation(() => panelInstance.open());
    },
    close: (skipUnsavedCheck) => {
      executeOperation(() => panelInstance.close(skipUnsavedCheck));
    },
    setTitle: (t) => {
      executeOperation(() => panelInstance.setTitle(t));
    },
    setCurrentJobId: (jobId) => {
      executeOperation(() => panelInstance.setCurrentJobId(jobId));
    },
    updateMinimizeButton: () => {
      executeOperation(() => panelInstance.updateMinimizeButton());
    },
    setDeleteCallback: (callback) => {
      const deleteBtn = document.getElementById('panel-delete-btn');
      if (deleteBtn) {
        deleteBtn.style.display = callback ? 'inline-block' : 'none';
        deleteBtn.onclick = callback;
      }
    },
    hideDelete: () => {
      const deleteBtn = document.getElementById('panel-delete-btn');
      if (deleteBtn) deleteBtn.style.display = 'none';
    },
    load: (url) => {
      const target = document.querySelector('#job-panel .panel-body');
      if (!target) return;
      target.setAttribute('hx-get', url);
      target.setAttribute('hx-target', 'this');
      target.setAttribute('hx-swap', 'innerHTML');
      htmx.ajax('GET', url, { 
        target: target, 
        swap: 'innerHTML',
        'hx-on::after-settle': 'if(window.JobPanel && window.JobPanel.trackFormChanges) window.JobPanel.trackFormChanges()'
      });
      executeOperation(() => panelInstance.open());
    },
    showContent: (html) => {
      const target = document.querySelector('#job-panel .panel-body');
      if (!target) return;
      target.innerHTML = html;
      executeOperation(() => {
        panelInstance.open();
        panelInstance.trackFormChanges();
      });
    },
    trackFormChanges: () => {
      executeOperation(() => panelInstance.trackFormChanges());
    },
    clearUnsavedChanges: () => {
      executeOperation(() => panelInstance.clearUnsavedChanges());
    },
    saveForm: (callback) => {
      executeOperation(() => panelInstance.saveForm(callback));
    }
  };

  window.jobPanel = function jobPanel(){
    return {
      isOpen: false,
      title: 'Job',
      x: 80, y: 80, w: 520, h: null,
      docked: false,
      dragging: false, sx: 0, sy: 0,
      currentJobId: null, // Track current job for workspace integration
      get panelStyle(){
        if (this.docked){
          return `top:80px; right:16px; left:auto; transform:none;`;
        }
        return `top:0; left:0; transform: translate(${this.x}px, ${this.y}px);`;
      },
      open(){ this.isOpen = true; save(this); },
      close(skipUnsavedCheck){ 
        // Check for unsaved changes before closing (unless explicitly skipped)
        if (!skipUnsavedCheck && this.hasUnsavedChanges()) {
          if (!confirm('You have unsaved changes. Are you sure you want to close without saving?')) {
            return; // User cancelled, don't close
          }
        }
        
        this.isOpen = false;
        this.currentJobId = null; // Clear current job ID when closing
        this.updateMinimizeButton(); // Hide minimize button
        save(this); 
      },
      setTitle(t){ this.title = t || 'Job'; save(this); },
      setCurrentJobId(jobId){ 
        this.currentJobId = jobId;
        this.updateMinimizeButton();
      },
      updateMinimizeButton() {
        const minimizeBtn = document.getElementById('panel-workspace-minimize-btn');
        if (!minimizeBtn) return;
        
        // Show minimize button only if this job is in the workspace
        if (this.currentJobId && window.JobWorkspace && window.JobWorkspace.hasJob(this.currentJobId)) {
          minimizeBtn.style.display = 'inline-flex';
        } else {
          minimizeBtn.style.display = 'none';
        }
      },
      toggleDock(){ this.docked = !this.docked; save(this); },
      hasUnsavedChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return false;
        
        // Check for any form inputs that have been modified
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        for (const input of inputs) {
          // Skip hidden inputs and buttons
          if (input.type === 'hidden' || input.type === 'submit' || input.type === 'button') {
            continue;
          }
          
          // Check if the current value differs from the original value
          if (input.hasAttribute('data-original-value')) {
            const originalValue = input.getAttribute('data-original-value');
            const currentValue = input.value;
            if (originalValue !== currentValue) {
              return true;
            }
          } else if (input.value !== '') {
            // If no original value stored but input has a value, it might be a change
            // This is a fallback for inputs that weren't tracked from the start
            return true;
          }
        }
        
        return false;
      },
      trackFormChanges() {
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return;
        
        // Store original values for all form inputs
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },
      clearUnsavedChanges() {
        // Reset tracking by updating all original values to current values
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) return;
        
        const inputs = panelBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
          if (input.type !== 'hidden' && input.type !== 'submit' && input.type !== 'button') {
            input.setAttribute('data-original-value', input.value);
          }
        });
      },
      saveForm(callback) {
        // Find the form in the panel body and submit it
        const panelBody = document.querySelector('#job-panel .panel-body');
        if (!panelBody) {
          console.warn('Panel body not found');
          if (callback) callback();
          return;
        }
        
        const form = panelBody.querySelector('form');
        if (!form) {
          console.warn('Form not found in panel');
          if (callback) callback();
          return;
        }
        
        // Trigger HTMX form submission if available
        if (typeof htmx !== 'undefined') {
          // Set up a one-time listener for after the request completes
          const afterRequestHandler = (event) => {
            if (event.detail.successful) {
              // Clear unsaved changes tracking
              this.clearUnsavedChanges();
              // Execute callback
              if (callback) callback();
            } else {
              console.error('Form submission failed');
              if (callback) callback(); // Still execute callback even on error
            }
            // Remove the event listener
            form.removeEventListener('htmx:afterRequest', afterRequestHandler);
          };
          
          form.addEventListener('htmx:afterRequest', afterRequestHandler);
          
          // Trigger HTMX request
          htmx.trigger(form, 'submit');
        } else {
          // Fallback: regular form submission
          form.submit();
          if (callback) callback();
        }
      },
      startDrag(e){
        if (this.docked) return;
        const p = e.touches?.[0] ?? e;
        this.dragging = true;
        this.sx = p.clientX - this.x;
        this.sy = p.clientY - this.y;
        window.addEventListener('mousemove', this._move);
        window.addEventListener('mouseup', this._stop);
        window.addEventListener('touchmove', this._move, {passive:false});
        window.addEventListener('touchend', this._stop);
      },
      _move: null,
      _stop: null,
      init(){
        const self = this;
        panelInstance = this; // Store reference for global API
        const st = load() || {};
        Object.assign(this, st);
        this._move = function(ev){
          if(!self.dragging) return;
          const p = ev.touches?.[0] ?? ev;
          const maxX = window.innerWidth - 200; // keep header on-screen
          const maxY = window.innerHeight - 48;
          self.x = clamp(p.clientX - self.sx, 8, maxX);
          self.y = clamp(p.clientY - self.sy, 8, maxY);
          ev.preventDefault();
        };
        this._stop = function(){
          self.dragging = false;
          window.removeEventListener('mousemove', self._move);
          window.removeEventListener('mouseup', self._stop);
          window.removeEventListener('touchmove', self._move);
          window.removeEventListener('touchend', self._stop);
          save(self);
        };
        // Execute any queued operations now that panel is ready
        flushQueue();
      }
    };
  };

  function save(vm){
    const st = { x:vm.x, y:vm.y, w:vm.w, h:vm.h, docked:vm.docked, title:vm.title, isOpen:vm.isOpen };
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(st)); } catch(e){}
  }
  function load(){
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); } catch(e){ return null; }
  }
  
  // Initialize panel when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPanel);
  } else {
    // DOM already loaded
    initPanel();
  }
  
  function initPanel() {
    // Wait a bit for Alpine to potentially load
    setTimeout(() => {
      const hasAlpine = typeof Alpine !== 'undefined' && Alpine !== null && typeof Alpine.start === 'function';
      if (hasAlpine) {
        isAlpineMode = true;
        // Alpine will call init() on the component
        // Wait a bit more for Alpine to initialize the component
        setTimeout(() => {
          if (!panelInstance) {
            panelInstance = createVanillaPanel();
            if (panelInstance) {
              flushQueue();
            }
          }
        }, 500);
      } else {
        isAlpineMode = false;
        panelInstance = createVanillaPanel();
        if (panelInstance) {
          flushQueue();
        }
      }
    }, 100);
  }
})();
