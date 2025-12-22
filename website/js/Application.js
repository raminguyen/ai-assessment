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
     * Handle local file upload
     * @private
     * @param {FileList} files - Files to upload
     */
    async handleLocalFileUpload(files) {
        try {
            const count = await this.fileProcessor.processLocalFiles(files);
            this.uiRenderer.setupFilters();
            this.uiRenderer.displayEssayList();
            this.uiRenderer.showNotification(`✓ ${count} files added!`);
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
            this.uiRenderer.showNotification(`✓ Loaded ${count} files from GitHub!`);
        } catch (error) {
            alert(`Failed to load from GitHub: ${error.message}`);
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
                alert('✓ Copied to clipboard!');
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
