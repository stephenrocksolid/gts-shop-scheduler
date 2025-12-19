/**
 * Calendar Call Reminders Module
 * 
 * Handles call reminder panel and actions.
 * Registers: showCallReminderPanel, markCallReminderComplete, saveJobReminderNotes,
 *            openJobFromReminder, saveStandaloneReminderNotes, markStandaloneReminderComplete,
 *            deleteStandaloneReminder
 */
(function() {
    'use strict';

    GTS.calendar.register('call_reminders', function(proto) {
        /**
         * Show call reminder panel with options
         */
        proto.showCallReminderPanel = function(event) {
            var self = this;
            var props = event.extendedProps || {};
            var isStandalone = props.type === 'standalone_call_reminder';
            var jobId = props.job_id;
            var reminderId = props.reminder_id;

            var html = '<div style="padding: 8px;">';

            // Header
            html += '<div style="margin-bottom: 8px;">' +
                '<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">' +
                '<div style="width: 32px; height: 32px; background-color: ' + event.backgroundColor + '; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 16px;">📞</div>' +
                '<div style="flex: 1;"><h3 style="margin: 0; font-size: 14px; font-weight: 600; color: #111827;">Call Reminder</h3>';

            if (!isStandalone && props.weeks_prior) {
                var weeksText = props.weeks_prior === 2 ? '1 week' : '2 weeks';
                html += '<p style="margin: 2px 0 0 0; font-size: 12px; color: #6b7280;">' + weeksText + ' before job</p>';
            } else if (props.reminder_date) {
                html += '<p style="margin: 2px 0 0 0; font-size: 12px; color: #6b7280;">' + props.reminder_date + '</p>';
            }

            html += '</div></div>';

            // Job details (only for job-related reminders)
            if (!isStandalone && jobId) {
                var jobDate = new Date(props.job_date);
                var formattedDate = this.calendar.formatDate(jobDate, {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                });

                html += '<div style="background-color: #f9fafb; border-radius: 6px; padding: 8px; margin-bottom: 8px;">' +
                    '<div style="margin-bottom: 6px;"><div style="font-weight: 600; color: #374151; margin-bottom: 2px; font-size: 12px;">Job Details</div>' +
                    '<div style="color: #6b7280; font-size: 12px;"><strong style="color: #111827;">' + (props.business_name || 'No business name') + '</strong>' +
                    (props.contact_name ? '<br>' + props.contact_name : '') +
                    (props.phone ? '<br>📱 ' + props.phone : '') +
                    '</div></div>' +
                    '<div style="padding-top: 6px; border-top: 1px solid #e5e7eb;">' +
                    '<div style="font-weight: 600; color: #374151; margin-bottom: 2px; font-size: 12px;">Job Date</div>' +
                    '<div style="color: #6b7280; font-size: 12px;">' + formattedDate + '</div></div></div>';
            }

            // Notes section
            var notesValue = props.notes || props.notes_preview || '';
            html += '<div style="margin-bottom: 8px;">' +
                '<label style="font-weight: 600; color: #374151; margin-bottom: 4px; display: block; font-size: 12px;">Notes</label>' +
                '<textarea id="reminder-notes" data-testid="call-reminder-notes" ' +
                'style="width: 100%; min-height: 60px; padding: 4px 8px; border: 1px solid #d1d5db; border-radius: 6px; font-family: inherit; font-size: 12px; resize: vertical;" ' +
                'placeholder="Add notes about this call reminder...">' + notesValue + '</textarea></div></div>';

            // Action buttons
            html += '<div style="display: flex; gap: 4px; justify-content: center;">';

            if (isStandalone && reminderId) {
                html += '<button onclick="jobCalendar.saveStandaloneReminderNotes(' + reminderId + ')" data-testid="call-reminder-save" ' +
                    'style="flex: 1; padding: 6px 12px; background-color: #3b82f6; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;" ' +
                    'onmouseover="this.style.backgroundColor=\'#2563eb\'" onmouseout="this.style.backgroundColor=\'#3b82f6\'">💾 Save & Close</button>' +
                    '<button onclick="jobCalendar.markStandaloneReminderComplete(' + reminderId + ')" data-testid="call-reminder-complete" ' +
                    'style="flex: 1; padding: 6px 12px; background-color: #10b981; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;" ' +
                    'onmouseover="this.style.backgroundColor=\'#059669\'" onmouseout="this.style.backgroundColor=\'#10b981\'">✓ Complete</button>' +
                    '<button onclick="jobCalendar.deleteStandaloneReminder(' + reminderId + ')" data-testid="call-reminder-delete" ' +
                    'style="padding: 6px 12px; background-color: #ef4444; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;" ' +
                    'onmouseover="this.style.backgroundColor=\'#dc2626\'" onmouseout="this.style.backgroundColor=\'#ef4444\'">🗑️</button>';
            } else if (jobId) {
                html += '<button onclick="jobCalendar.saveJobReminderNotes(' + jobId + ')" data-testid="call-reminder-save" ' +
                    'style="flex: 1; padding: 6px 12px; background-color: #3b82f6; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;" ' +
                    'onmouseover="this.style.backgroundColor=\'#2563eb\'" onmouseout="this.style.backgroundColor=\'#3b82f6\'">💾 Save & Close</button>' +
                    '<button onclick="jobCalendar.markCallReminderComplete(' + jobId + ')" data-testid="call-reminder-complete" ' +
                    'style="flex: 1; padding: 6px 12px; background-color: #10b981; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;" ' +
                    'onmouseover="this.style.backgroundColor=\'#059669\'" onmouseout="this.style.backgroundColor=\'#10b981\'">✓ Mark Complete</button>' +
                    '<button onclick="jobCalendar.openJobFromReminder(' + jobId + ')" data-testid="call-reminder-view-job" ' +
                    'style="flex: 1; padding: 6px 12px; background-color: #6b7280; color: white; border: none; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer;" ' +
                    'onmouseover="this.style.backgroundColor=\'#4b5563\'" onmouseout="this.style.backgroundColor=\'#6b7280\'">View Job</button>';
            }

            html += '</div></div>';

            if (window.JobPanel) {
                window.JobPanel.setTitle('📞 Call Reminder');
                window.JobPanel.showContent(html);
            }
        };

        /**
         * Mark call reminder as complete
         */
        proto.markCallReminderComplete = function(jobId) {
            var self = this;
            fetch('/api/jobs/' + jobId + '/mark-call-reminder-complete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            })
                .then(function(response) {
                    if (response.ok) {
                        if (window.JobPanel) window.JobPanel.close();
                        self.calendar.refetchEvents();
                        self.showSuccess('Call reminder marked as complete');
                    } else {
                        return response.json().then(function(data) {
                            self.showError(data.error || 'Failed to mark reminder as complete');
                        });
                    }
                })
                .catch(function(error) {
                    console.error('Error marking call reminder complete:', error);
                    self.showError('Failed to mark reminder as complete');
                });
        };

        /**
         * Save notes for job-related call reminder and close the dialog
         */
        proto.saveJobReminderNotes = function(jobId) {
            var self = this;
            var notesEl = document.getElementById('reminder-notes');
            var notes = notesEl ? notesEl.value : '';

            fetch('/jobs/' + jobId + '/call-reminder/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ notes: notes })
            })
                .then(function(response) {
                    if (response.ok) {
                        if (window.JobPanel && window.JobPanel.clearUnsavedChanges) {
                            window.JobPanel.clearUnsavedChanges();
                        }
                        if (window.JobPanel) window.JobPanel.close(true);
                        self.calendar.refetchEvents();
                    } else {
                        return response.json().then(function(data) {
                            self.showError(data.error || 'Failed to save notes');
                        });
                    }
                })
                .catch(function(error) {
                    console.error('Error saving reminder notes:', error);
                    self.showError('Failed to save notes. Please try again.');
                });
        };

        /**
         * Open the job detail/edit from a call reminder
         */
        proto.openJobFromReminder = function(jobId) {
            if (window.JobPanel) {
                window.JobPanel.setTitle('Edit Job');
                window.JobPanel.load('/jobs/new/partial/?edit=' + jobId);
            }
        };

        /**
         * Save notes for standalone call reminder
         */
        proto.saveStandaloneReminderNotes = function(reminderId) {
            var self = this;
            var notesEl = document.getElementById('reminder-notes');
            var notes = notesEl ? notesEl.value : '';

            fetch('/call-reminders/' + reminderId + '/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ notes: notes })
            })
                .then(function(response) {
                    if (response.ok) {
                        if (window.JobPanel) {
                            window.JobPanel.clearUnsavedChanges();
                            window.JobPanel.close(true);
                        }
                        self.calendar.refetchEvents();
                    } else {
                        return response.json().then(function(data) {
                            self.showError(data.error || 'Failed to save notes');
                        });
                    }
                })
                .catch(function(error) {
                    console.error('Error saving reminder notes:', error);
                    self.showError('Failed to save notes');
                });
        };

        /**
         * Mark standalone call reminder as complete
         */
        proto.markStandaloneReminderComplete = function(reminderId) {
            var self = this;
            fetch('/call-reminders/' + reminderId + '/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ completed: true })
            })
                .then(function(response) {
                    if (response.ok) {
                        if (window.JobPanel) window.JobPanel.close();
                        self.calendar.refetchEvents();
                        self.showSuccess('Call reminder marked as complete');
                    } else {
                        return response.json().then(function(data) {
                            self.showError(data.error || 'Failed to mark reminder as complete');
                        });
                    }
                })
                .catch(function(error) {
                    console.error('Error marking reminder complete:', error);
                    self.showError('Failed to mark reminder as complete');
                });
        };

        /**
         * Delete standalone call reminder
         */
        proto.deleteStandaloneReminder = function(reminderId) {
            var self = this;
            if (!confirm('Are you sure you want to delete this call reminder?')) {
                return;
            }

            fetch('/call-reminders/' + reminderId + '/delete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            })
                .then(function(response) {
                    if (response.ok) {
                        if (window.JobPanel) window.JobPanel.close();
                        self.calendar.refetchEvents();
                        self.showSuccess('Call reminder deleted successfully');
                    } else {
                        return response.json().then(function(data) {
                            self.showError(data.error || 'Failed to delete reminder');
                        });
                    }
                })
                .catch(function(error) {
                    console.error('Error deleting reminder:', error);
                    self.showError('Failed to delete reminder');
                });
        };
    });

})();
