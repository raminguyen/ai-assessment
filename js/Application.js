/**
 * Application - Main application controller
 * Orchestrates all other classes and handles user interactions
 */
class Application {
    /**
     * Initialize Application with all required components
     */
    constructor() {
        // Create instances of all major classes
        this.dataManager = new DataManager();
        this.fileProcessor = new FileProcessor(this.dataManager);
        this.gitHubLoader = new GitHubLoader(this.dataManager);
        this.uiRenderer = new UIRenderer(this.dataManager);
        
        // Initialize the application
        this.init();
    }
    /**
     * Initialize the application
     * @private
     */
    init() {
        this.setupEventListeners();
        this.setupFolderPicker();
    }
    /**
     * Setup event listeners for all UI interactions
     * @private
     */
    setupEventListeners() {
        // Upload box click
        this.uiRenderer.elements.uploadBox.addEventListener('click', () => {
            this.uiRenderer.elements.fileInput.click();
        });
        // File input change
        this.uiRenderer.elements.fileInput.addEventListener('change', (e) => {
            this.handleLocalFileUpload(e.target.files);
        });
        // Drag over
        this.uiRenderer.elements.uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uiRenderer.elements.uploadBox.classList.add('drag-over');
        });
        // Drag leave
        this.uiRenderer.elements.uploadBox.addEventListener('dragleave', () => {
            this.uiRenderer.elements.uploadBox.classList.remove('drag-over');
        });
        // Drop
        this.uiRenderer.elements.uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uiRenderer.elements.uploadBox.classList.remove('drag-over');
            this.handleLocalFileUpload(e.dataTransfer.files);
        });
        // GitHub button
        this.uiRenderer.elements.githubBtn.addEventListener('click', () => {
            this.handleGitHubLoad();
        });
    }
    /**
     * Setup folder picker button listener
     * @private
     */
    setupFolderPicker() {
        const loadFolderBtn = document.getElementById('loadFolderBtn');
        
        if (loadFolderBtn) {
            loadFolderBtn.addEventListener('click', async () => {
                try {
                    // Check if File System Access API is supported
                    if (!window.showDirectoryPicker) {
                        alert('Folder picker not supported in your browser. Please use Chrome or Firefox.');
                        return;
                    }
                    
                    loadFolderBtn.disabled = true;
                    loadFolderBtn.textContent = '📁 Loading...';
                    
                    // Process parent folder and all subfolders
                    const filesLoaded = await this.processParentFolder();
                    
                    // Update UI
                    this.uiRenderer.setupFilters();
                    this.uiRenderer.displayEssayList();
                    this.uiRenderer.showNotification('Loaded ' + filesLoaded + ' files from folder!');
                    
                    loadFolderBtn.textContent = '📁 Load from Folder';
                    loadFolderBtn.disabled = false;
                    
                } catch (error) {
                    console.error('Error loading folder:', error);
                    this.uiRenderer.showNotification('Error: ' + error.message);
                    loadFolderBtn.textContent = '📁 Load from Folder';
                    loadFolderBtn.disabled = false;
                }
            });
        }
    }

    /**
     * Process parent folder and all subfolders recursively
     * Loads JSON files from parent folder and all subfolders
     * @private
     */
    async processParentFolder() {
        try {
            const handle = await window.showDirectoryPicker();
            const files = [];
            
            // Recursively collect JSON files from folder and subfolders
            await this.collectJsonFilesRecursive(handle, files);
            
            if (files.length === 0) {
                throw new Error('No JSON files found in folder or subfolders!');
            }
            
            // Process all files
            let filesRead = 0;
            return new Promise((resolve, reject) => {
                files.forEach(({file, path}) => {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        try {
                            const data = JSON.parse(e.target.result);
                            // Use folder from JSON, or guess from subfolder name
                            const folderGuess = data.folder || this.guessFolderFromPath(path);
                            this.fileProcessor.processData(data, folderGuess);
                            filesRead++;
                            if (filesRead === files.length) {
                                resolve(filesRead);
                            }
                        } catch (error) {
                            reject('Error reading ' + file.name + ': ' + error.message);
                        }
                    };
                    reader.readAsText(file);
                });
            });
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Folder selection cancelled');
            }
            throw error;
        }
    }

    /**
     * Recursively collect JSON files from folder and all subfolders
     * @private
     */
    async collectJsonFilesRecursive(handle, files, path = '') {
        for await (const entry of handle.values()) {
            const currentPath = path ? path + '/' + entry.name : entry.name;
            
            if (entry.kind === 'file' && entry.name.endsWith('.json')) {
                const file = await entry.getFile();
                files.push({file, path: currentPath});
            } else if (entry.kind === 'directory') {
                // Recursively process subdirectories
                await this.collectJsonFilesRecursive(entry, files, currentPath);
            }
        }
    }

    /**
     * Guess folder name from file path
     * Examples:
     * "critical_thinking/a1_gen.json" -> "critical_thinking"
     * "data/oral_communication/a1_tune.json" -> "oral_communication"
     * @private
     */
    guessFolderFromPath(path) {
        // Extract folder name from path
        const parts = path.split('/');
        
        // Check each part of the path
        for (let part of parts) {
            if (part.includes('critical')) {
                return 'critical_thinking';
            } else if (part.includes('oral')) {
                return 'oral_communication';
            }
        }
        
        // If no match, use first folder name
        if (parts.length > 1) {
            return parts[0];
        }
        
        return null;
    }
    /**
     * Handle local file upload
     * @private
     * @param {FileList} files - Files to upload
     */
    async handleLocalFileUpload(files) {
        try {
            const count = await this.fileProcessor.processLocalFiles(files);
            this.uiRenderer.setupFilters();
            this.uiRenderer.displayEssayList();
            this.uiRenderer.showNotification('✓ ' + count + ' files added!');
        } catch (error) {
            alert(error);
        }
    }
    /**
     * Handle GitHub loading
     * @private
     */
    async handleGitHubLoad() {
        try {
            this.uiRenderer.showNotification('Loading files from GitHub...');
            const count = await this.gitHubLoader.loadFromGitHub();
            this.uiRenderer.setupFilters();
            this.uiRenderer.displayEssayList();
            this.uiRenderer.showNotification('✓ Loaded ' + count + ' files from GitHub!');
        } catch (error) {
            alert('Failed to load from GitHub: ' + error.message);
        }
    }
    /**
     * Copy essay text to clipboard
     * Called by copy button in ContentRenderer
     */
    copyEssayText() {
        const text = document.getElementById('essayText').innerText;
        this.copyToClipboard(text);
    }
    /**
     * Copy evaluation text to clipboard
     * Called by copy button in ContentRenderer
     */
    copyEvaluationText() {
        const text = document.getElementById('evaluationText').innerText;
        this.copyToClipboard(text);
    }
    /**
     * Copy text to clipboard using browser API
     * @private
     * @param {string} text - Text to copy
     */
    copyToClipboard(text) {
        navigator.clipboard.writeText(text)
            .then(() => {
                this.uiRenderer.showNotification('✓ Copied to clipboard!');
            })
            .catch(() => {
                alert('Failed to copy');
            });
    }
}
// ============================================
// Initialize Application
// ============================================
const app = new Application();