// rental_scheduler/static/rental_scheduler/js/all_day_toggle.js
(function(){
  function addDays(d, days){ const x = new Date(d.getTime()); x.setDate(x.getDate()+days); return x; }
  function atMidnight(d){ const x = new Date(d.getTime()); x.setHours(0,0,0,0); return x; }

  window.wireAllDayToggle = function({ allDaySel='#id_all_day', startSel='#id_start_dt', endSel='#id_end_dt', exclusiveEnd=true } = {}){
    const allDayEl = document.querySelector(allDaySel);
    const startEl  = document.querySelector(startSel);
    const endEl    = document.querySelector(endSel);
    
    console.log('wireAllDayToggle called', {allDayEl, startEl, endEl, hasTempusDominus: !!window.tempusDominus});
    
    if(!allDayEl || !startEl || !endEl || !window.tempusDominus){ 
      console.warn('All day toggle: Required elements or Tempus Dominus not found');
      return; 
    }

    const startPicker = tempusDominus.TempusDominus.getInstance(startEl);
    const endPicker   = tempusDominus.TempusDominus.getInstance(endEl);
    
    console.log('Tempus Dominus instances', {startPicker, endPicker});
    
    if(!startPicker || !endPicker) {
      console.warn('All day toggle: Tempus Dominus instances not found');
      return;
    }

    function ensureDate(picker, fallback){
      let d = picker.dates.picked[0];
      if(!d){ d = fallback || new Date(); picker.dates.setValue(d); }
      return d;
    }

    function applyAllDay(on){
      console.log('applyAllDay called with:', on);
      
      startPicker.updateOptions({ display: { components: { clock: !on ? true : false } }});
      endPicker.updateOptions({   display: { components: { clock: !on ? true : false } }});

      if(on){
        // normalize to midnight
        const s = atMidnight(ensureDate(startPicker));
        let e   = atMidnight(ensureDate(endPicker, s));
        if(exclusiveEnd){ e = atMidnight(addDays(e, 1)); }
        startPicker.dates.setValue(s, true);
        endPicker.dates.setValue(e, true);
        console.log('Set to all-day mode:', {start: s, end: e});
      } else {
        console.log('Set to time mode');
      }
    }

    // initial
    applyAllDay(allDayEl.checked);
    // toggle
    allDayEl.addEventListener('change', () => applyAllDay(allDayEl.checked));
  };
})();

