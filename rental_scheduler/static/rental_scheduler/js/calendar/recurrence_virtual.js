/**
 * Calendar Recurrence Virtual Module
 * 
 * Handles virtual occurrence materialization for recurring events.
 * Registers: materializeAndOpenJob, materializeAndShowCallReminder
 */
(function() {
    'use strict';

    GTS.calendar.register('recurrence_virtual', function(proto) {
        /**
         * Materialize a virtual occurrence and open the resulting job
         * Virtual occurrences are generated on-the-fly for "forever" recurring series
         */
        proto.materializeAndOpenJob = function(event) {
            var self = this;
            var props = event.extendedProps || {};
            var parentId = props.recurrence_parent_id;
            var originalStart = props.recurrence_original_start;

            if (!parentId || !originalStart) {
                console.error('Missing parent_id or original_start for virtual job');
                this.showError('Unable to open this occurrence. Please try again.');
                return;
            }

            console.log('Materializing virtual occurrence:', parentId, originalStart);
            this.showLoading();

            fetch(GTS.urls.materializeOccurrence, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    parent_id: parentId,
                    original_start: originalStart
                })
            })
                .then(function(response) {
                    if (!response.ok) {
                        return response.json().then(function(errorData) {
                            throw new Error(errorData.error || 'Failed to materialize occurrence');
                        });
                    }
                    return response.json();
                })
                .then(function(data) {
                    var jobId = data.job_id;

                    console.log('Materialized occurrence, job ID:', jobId, 'created:', data.created);

                    // Now open the real job
                    if (window.JobWorkspace) {
                        window.JobWorkspace.openJob(jobId, {
                            customerName: props.display_name || event.title || 'Job',
                            trailerColor: props.trailer_color || '',
                            calendarColor: props.calendar_color || '#3B82F6'
                        });
                    } else if (window.JobPanel) {
                        window.JobPanel.setTitle('Edit Job');
                        window.JobPanel.load(GTS.urls.jobCreatePartial({ edit: jobId }));
                        if (window.JobPanel.setCurrentJobId) {
                            window.JobPanel.setCurrentJobId(jobId);
                        }
                    }

                    // Refetch events to update the calendar (virtual occurrence is now real)
                    if (data.created) {
                        self.debouncedRefetch();
                    }
                })
                .catch(function(error) {
                    console.error('Error materializing virtual occurrence:', error);
                    self.showError('Unable to open this occurrence. Please try again.');
                })
                .finally(function() {
                    self.hideLoading();
                });
        };

        /**
         * Materialize a virtual call reminder occurrence and show the reminder panel
         */
        proto.materializeAndShowCallReminder = function(event) {
            var self = this;
            var props = event.extendedProps || {};
            var parentId = props.recurrence_parent_id;
            var originalStart = props.recurrence_original_start;

            if (!parentId || !originalStart) {
                console.error('Missing parent_id or original_start for virtual call reminder');
                this.showError('Unable to open this reminder. Please try again.');
                return;
            }

            console.log('Materializing virtual call reminder:', parentId, originalStart);
            this.showLoading();

            fetch(GTS.urls.materializeOccurrence, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    parent_id: parentId,
                    original_start: originalStart
                })
            })
                .then(function(response) {
                    if (!response.ok) {
                        return response.json().then(function(errorData) {
                            throw new Error(errorData.error || 'Failed to materialize occurrence');
                        });
                    }
                    return response.json();
                })
                .then(function(data) {
                    var jobId = data.job_id;

                    console.log('Materialized for call reminder, job ID:', jobId);

                    // Update the event's extendedProps with the real job_id so showCallReminderPanel works
                    var updatedEvent = {
                        title: event.title,
                        start: event.start,
                        end: event.end,
                        allDay: event.allDay,
                        backgroundColor: event.backgroundColor,
                        extendedProps: Object.assign({}, props, {
                            job_id: jobId,
                            type: 'call_reminder'  // Change type to real call reminder
                        })
                    };

                    // Show the call reminder panel for the materialized job
                    self.showCallReminderPanel(updatedEvent);

                    // Refetch events to update the calendar
                    if (data.created) {
                        self.debouncedRefetch();
                    }
                })
                .catch(function(error) {
                    console.error('Error materializing virtual call reminder:', error);
                    self.showError('Unable to open this reminder. Please try again.');
                })
                .finally(function() {
                    self.hideLoading();
                });
        };
    });

})();
