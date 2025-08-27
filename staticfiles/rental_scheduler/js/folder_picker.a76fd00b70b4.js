/**
 * FolderPicker - Manages folder browsing and selection functionality
 * Handles modal display, folder navigation, and API interactions
 */

// Wrap in IIFE to avoid global conflicts
(function () {
    'use strict';

    // Defensive loading - only declare FolderPicker if it doesn't already exist
    if (typeof window.FolderPicker === 'undefined') {

        class FolderPicker {
            constructor(inputElement, selectButton) {
                this.inputElement = inputElement;
                this.selectButton = selectButton;
                this.currentPath = '';  // Will be set by first API call
                this.pathHistory = [];
                this.currentHistoryIndex = -1;
                this.modal = null;
                this.setupEventListeners();
                window.Logger?.debug('FolderPicker initialized with:', { inputElement, selectButton });
            }

            setupEventListeners() {
                window.Logger?.debug('Setting up event listeners');
                this.selectButton.addEventListener('click', () => {
                    window.Logger?.debug('Select button clicked');
                    this.showModal();
                });
            }

            async showModal() {
                // Create modal HTML
                this.modal = document.createElement('div');
                this.modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
                this.modal.innerHTML = `
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900">Select Folder</h3>
                    <button class="text-gray-400 hover:text-gray-500" onclick="folderPicker.closeModal()">
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                
                <div class="flex items-center mb-4">
                    <button class="mr-2 text-gray-600 hover:text-gray-800" onclick="folderPicker.goBack()">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                        </svg>
                    </button>
                    <div class="flex-1 text-sm text-gray-600 truncate" id="current-path"></div>
                    <button class="ml-2 text-gray-600 hover:text-gray-800" onclick="folderPicker.goForward()">
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                    </button>
                </div>

                <div class="mb-4">
                    <input type="text" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                           placeholder="Search folders..."
                           onkeyup="folderPicker.filterFolders(this.value)">
                </div>

                <div class="max-h-96 overflow-y-auto mb-4" id="folder-list">
                    <div class="flex justify-center items-center h-32 text-gray-500">
                        Loading folders...
                    </div>
                </div>

                <div class="flex justify-end space-x-3">
                    <button class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            onclick="folderPicker.closeModal()">
                        Cancel
                    </button>
                    <button class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            onclick="folderPicker.selectCurrentFolder()">
                        Select
                    </button>
                </div>
            </div>
        `;

                document.body.appendChild(this.modal);
                await this.loadFolders('');  // Start with empty path to get current directory
            }

            closeModal() {
                if (this.modal) {
                    this.modal.remove();
                    this.modal = null;
                }
            }

            async loadFolders(path) {
                try {
                    const response = await fetch(
                        `${window.RentalConfig?.getApiUrl('browseFolders') || '/api/browse-folders/'}?path=${encodeURIComponent(path)}`,
                        {
                            headers: window.RentalConfig?.getApiHeaders() || {}
                        }
                    );
                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || 'Failed to load folders');
                    }

                    this.currentPath = data.current_path;
                    document.getElementById('current-path').textContent = this.currentPath;

                    const folderList = document.getElementById('folder-list');
                    folderList.innerHTML = '';

                    if (data.items.length === 0) {
                        folderList.innerHTML = `
                    <div class="flex justify-center items-center h-32 text-gray-500">
                        No folders found
                    </div>
                `;
                        return;
                    }

                    data.items.forEach(item => {
                        const folderElement = document.createElement('div');
                        folderElement.className = 'flex items-center p-2 hover:bg-gray-100 cursor-pointer rounded-md';
                        folderElement.innerHTML = `
                    <svg class="h-5 w-5 text-gray-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    <span class="text-sm text-gray-700">${item.name}</span>
                `;
                        folderElement.addEventListener('click', () => this.navigateToFolder(item.path));
                        folderList.appendChild(folderElement);
                    });
                } catch (error) {
                    window.Logger.error('Error loading folders:', error);
                    const folderList = document.getElementById('folder-list');
                    folderList.innerHTML = `
                <div class="flex justify-center items-center h-32 text-red-500">
                    Error: ${error.message}
                </div>
            `;
                }
            }

            navigateToFolder(path) {
                this.pathHistory = this.pathHistory.slice(0, this.currentHistoryIndex + 1);
                this.pathHistory.push(this.currentPath);
                this.currentHistoryIndex++;
                this.loadFolders(path);
            }

            async goBack() {
                if (this.currentHistoryIndex >= 0) {
                    this.currentHistoryIndex--;
                    await this.loadFolders(this.pathHistory[this.currentHistoryIndex]);
                }
            }

            async goForward() {
                if (this.currentHistoryIndex < this.pathHistory.length - 1) {
                    this.currentHistoryIndex++;
                    await this.loadFolders(this.pathHistory[this.currentHistoryIndex]);
                }
            }

            filterFolders(searchTerm) {
                const folderList = document.getElementById('folder-list');
                const folders = folderList.getElementsByClassName('flex');

                Array.from(folders).forEach(folder => {
                    const folderName = folder.querySelector('span').textContent.toLowerCase();
                    folder.style.display = folderName.includes(searchTerm.toLowerCase()) ? 'flex' : 'none';
                });
            }

            selectCurrentFolder() {
                this.inputElement.value = this.currentPath;
                this.closeModal();
            }
        }

        // Initialize the folder picker when the document is loaded
        document.addEventListener('DOMContentLoaded', () => {
            window.Logger.debug('DOM Content Loaded');
            const licensePathInput = document.getElementById('id_license_scan_path');
            const selectPathButton = document.getElementById('select-path-button');

            window.Logger.debug('Found elements:', { licensePathInput, selectPathButton });

            if (licensePathInput && selectPathButton) {
                window.folderPicker = new FolderPicker(licensePathInput, selectPathButton);
            } else {
                window.Logger?.error('Could not find required elements:', {
                    licensePathInput: !!licensePathInput,
                    selectPathButton: !!selectPathButton
                });
            }
        });

        // Export FolderPicker class to global scope
        window.FolderPicker = FolderPicker;

    } else {
        window.Logger?.debug('FolderPicker already exists, skipping initialization');
    }

})(); // End of IIFE 