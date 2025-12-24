class Application {
    constructor() {
        this.dataManager = new Data();
        this.fileProcessor = new File(this.dataManager);
        this.gitHubLoader = new LoadGitHub(this.dataManager);
        this.uiRenderer = new Renderer(this.dataManager);
        
        this.setupButtons();
        this.setupDragAndDrop();
        this.setupFolderPicker();
    }

    setupButtons() {
        this.uiRenderer.elements.uploadBox.addEventListener('click', () => {
            this.uiRenderer.elements.fileInput.click();
        });
        
        this.uiRenderer.elements.fileInput.addEventListener('change', (e) => {
            this.uploadFiles(e.target.files);
        });
        
        this.uiRenderer.elements.githubBtn.addEventListener('click', () => {
            this.loadFromGitHub();
        });
    }

    setupDragAndDrop() {
        const box = this.uiRenderer.elements.uploadBox;
        
        box.addEventListener('dragover', (e) => {
            e.preventDefault();
            box.classList.add('drag-over');
        });
        
        box.addEventListener('dragleave', () => {
            box.classList.remove('drag-over');
        });
        
        box.addEventListener('drop', (e) => {
            e.preventDefault();
            box.classList.remove('drag-over');
            this.uploadFiles(e.dataTransfer.files);
        });
    }

    setupFolderPicker() {
        const button = document.getElementById('loadFolderBtn');
        if (!button) return;
        
        button.addEventListener('click', async () => {
            if (!window.showDirectoryPicker) {
                alert('Your browser does not support folder picking. Please use Chrome or Edge.');
                return;
            }
            
            button.disabled = true;
            button.textContent = '📁 Loading...';
            
            const count = await this.loadFolder();
            
            this.uiRenderer.setupFilters();
            this.uiRenderer.displayEssayList();
            this.uiRenderer.showNotification(`✓ Loaded ${count} files!`);
            
            button.textContent = '📁 Load from Folder';
            button.disabled = false;
        });
    }

    async loadFolder() {
        const folderHandle = await window.showDirectoryPicker();
        
        const jsonFiles = [];
        await this.findJsonFiles(folderHandle, jsonFiles, '');
        
        await this.readAllFiles(jsonFiles);
        
        return jsonFiles.length;
    }

    async findJsonFiles(folderHandle, filesList, currentPath) {
        for await (const entry of folderHandle.values()) {
            const path = currentPath ? `${currentPath}/${entry.name}` : entry.name;
            
            if (entry.kind === 'file' && entry.name.endsWith('.json')) {
                const file = await entry.getFile();
                filesList.push({ file, path });
            } else if (entry.kind === 'directory') {
                await this.findJsonFiles(entry, filesList, path);
            }
        }
    }

    async readAllFiles(filesList) {
        for (const { file, path } of filesList) {
            const text = await file.text();
            const data = JSON.parse(text);
            const folder = data.folder || this.guessFolder(path);
            this.fileProcessor.processData(data, folder);
        }
    }

    guessFolder(path) {
        if (path.includes('critical')) return 'critical_thinking';
        if (path.includes('oral')) return 'oral_communication';
        
        const firstFolder = path.split('/')[0];
        return firstFolder !== path ? firstFolder : null;
    }

    async uploadFiles(files) {
        const count = await this.fileProcessor.processLocalFiles(files);
        this.uiRenderer.setupFilters();
        this.uiRenderer.displayEssayList();
        this.uiRenderer.showNotification(`✓ Added ${count} files!`);
    }

    async loadFromGitHub() {
        this.uiRenderer.showNotification('Loading from GitHub...');
        const count = await this.gitHubLoader.loadFromGitHub();
        this.uiRenderer.setupFilters();
        this.uiRenderer.displayEssayList();
        this.uiRenderer.showNotification(`✓ Loaded ${count} files!`);
    }

    copyEssayText() {
        const text = document.getElementById('essayText').innerText;
        this.copyText(text);
    }

    copyEvaluationText() {
        const text = document.getElementById('evaluationText').innerText;
        this.copyText(text);
    }

    copyText(text) {
        navigator.clipboard.writeText(text);
        this.uiRenderer.showNotification('✓ Copied!');
    }
}

const app = new Application();