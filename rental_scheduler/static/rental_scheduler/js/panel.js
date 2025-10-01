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
    console.log('Creating vanilla JS panel (Alpine not available)');
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
      },
      
      open() {
        console.log('Vanilla panel: opening');
        this.isOpen = true;
        this.updateVisibility();
        save(this);
      },
      
      close() {
        console.log('Vanilla panel: closing');
        this.isOpen = false;
        this.updateVisibility();
        save(this);
      },
      
      setTitle(t) {
        this.title = t || 'Job';
        const titleEl = document.getElementById('job-panel-title');
        if (titleEl) titleEl.textContent = this.title;
        save(this);
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
      
      setupButtons() {
        // Close button
        const closeBtn = panelEl.querySelector('.panel-header .btn-close');
        if (closeBtn) closeBtn.addEventListener('click', () => this.close());
        
        // Delete button is handled by the global API via setDeleteCallback
        
        // ESC key
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && this.isOpen) this.close();
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
        console.log('Vanilla panel: initializing');
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
    close: () => {
      executeOperation(() => panelInstance.close());
    },
    setTitle: (t) => {
      executeOperation(() => panelInstance.setTitle(t));
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
      htmx.ajax('GET', url, { target: target, swap: 'innerHTML' });
      executeOperation(() => panelInstance.open());
    }
  };

  window.jobPanel = function jobPanel(){
    console.log('jobPanel() function called - Alpine is initializing component');
    return {
      isOpen: false,
      title: 'Job',
      x: 80, y: 80, w: 520, h: null,
      docked: false,
      dragging: false, sx: 0, sy: 0,
      get panelStyle(){
        if (this.docked){
          return `top:80px; right:16px; left:auto; transform:none;`;
        }
        return `top:0; left:0; transform: translate(${this.x}px, ${this.y}px);`;
      },
      open(){ this.isOpen = true; save(this); },
      close(){ this.isOpen = false; save(this); },
      setTitle(t){ this.title = t || 'Job'; save(this); },
      toggleDock(){ this.docked = !this.docked; save(this); },
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
        console.log('Panel instance ready, flushing queue...');
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
    console.log('Initializing panel...');
    // Wait a bit for Alpine to potentially load
    setTimeout(() => {
      const hasAlpine = typeof Alpine !== 'undefined' && Alpine !== null && typeof Alpine.start === 'function';
      if (hasAlpine) {
        console.log('Alpine detected and functional, using Alpine mode');
        isAlpineMode = true;
        // Alpine will call init() on the component
        // Wait a bit more for Alpine to initialize the component
        setTimeout(() => {
          if (!panelInstance) {
            console.warn('Alpine did not initialize panel, falling back to vanilla JS');
            panelInstance = createVanillaPanel();
            if (panelInstance) {
              flushQueue();
            }
          }
        }, 500);
      } else {
        console.log('Alpine not detected or not functional, using vanilla JS mode');
        isAlpineMode = false;
        panelInstance = createVanillaPanel();
        if (panelInstance) {
          flushQueue();
        }
      }
    }, 100);
  }
})();
