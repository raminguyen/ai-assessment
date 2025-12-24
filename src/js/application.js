class Application {
    constructor() {
        this.dataManager = new Data();
        this.fileProcessor = new File(this.dataManager);
        this.gitHubLoader = new LoadGitHub(this.dataManager);
        this.uiRenderer = new Renderer(this.dataManager);
        
        this.setup_buttons();
        this.setup_drag_and_drop();
        this.setup_folder_picker();
    }

    setup_buttons() {
        const browseFilesBtn = document.getElementById('browseFilesBtn');
        const browseFoldersBtn = document.getElementById('browseFoldersBtn');
        const folderInput = document.getElementById('folderInput');

        browseFilesBtn.addEventListener('click', () => {
            this.uiRenderer.elements.fileInput.click();
        });

        browseFoldersBtn.addEventListener('click', () => {
            folderInput.click();
        });

        this.uiRenderer.elements.fileInput.addEventListener('change', (e) => {
            this.upload_files(e.target.files);
        });

        folderInput.addEventListener('change', (e) => {
            this.upload_files(e.target.files);
        });

        this.uiRenderer.elements.githubBtn.addEventListener('click', () => {
            this.load_from_github();
        });
    }

    setup_drag_and_drop() {
        const box = this.uiRenderer.elements.uploadBox;

        box.addEventListener('dragover', (e) => {
            e.preventDefault();
            box.classList.add('drag-over');
        });

        box.addEventListener('dragleave', () => {
            box.classList.remove('drag-over');
        });

        box.addEventListener('drop', async (e) => {
            e.preventDefault();
            box.classList.remove('drag-over');

            const items = e.dataTransfer.items;
            if (!items) {
                this.upload_files(e.dataTransfer.files);
                return;
            }

            const files = [];
            for (let i = 0; i < items.length; i++) {
                const item = items[i].webkitGetAsEntry();
                if (item) {
                    await this.scan_item(item, files);
                }
            }

            if (files.length > 0) {
                await this.read_all_files(files);
                this.uiRenderer.setup_filters();
                this.uiRenderer.display_essay_list();
                this.uiRenderer.show_notification(`✓ Added ${files.length} files!`);
            }
        });
    }

    async scan_item(item, files) {
        if (item.isFile && item.name.endsWith('.json')) {
            const file = await new Promise(resolve => item.file(resolve));
            files.push({ file, path: item.fullPath });
        } else if (item.isDirectory) {
            const reader = item.createReader();
            const entries = await new Promise(resolve => reader.readEntries(resolve));
            for (const entry of entries) {
                await this.scan_item(entry, files);
            }
        }
    }

    setup_folder_picker() {
        const button = document.getElementById('loadFolderBtn');
        if (!button) return;
        
        button.addEventListener('click', async () => {
            if (!window.showDirectoryPicker) {
                alert('Your browser does not support folder picking. Please use Chrome or Edge.');
                return;
            }
            
            button.disabled = true;
            button.textContent = 'Loading...';
            
            const count = await this.load_folder();

            this.uiRenderer.setup_filters();
            this.uiRenderer.display_essay_list();
            this.uiRenderer.show_notification(`✓ Loaded ${count} files!`);
            
            button.textContent = 'Load from Folder';
            button.disabled = false;
        });
    }

    async load_folder() {
        const folderHandle = await window.showDirectoryPicker();
        
        const jsonFiles = [];
        await this.find_json_files(folderHandle, jsonFiles, '');
        
        await this.read_all_files(jsonFiles);
        
        return jsonFiles.length;
    }

    async find_json_files(folderHandle, filesList, currentPath) {
        for await (const entry of folderHandle.values()) {
            const path = currentPath ? `${currentPath}/${entry.name}` : entry.name;
            
            if (entry.kind === 'file' && entry.name.endsWith('.json')) {
                const file = await entry.getFile();
                filesList.push({ file, path });
            } else if (entry.kind === 'directory') {
                await this.find_json_files(entry, filesList, path);
            }
        }
    }

    async read_all_files(filesList) {
        for (const { file, path } of filesList) {
            const text = await file.text();
            const data = JSON.parse(text);
            const folder = data.folder || this.guess_folder(path);
            this.fileProcessor.processData(data, folder);
        }
    }

    guess_folder(path) {
        if (path.includes('critical')) return 'critical_thinking';
        if (path.includes('oral')) return 'oral_communication';
        
        const firstFolder = path.split('/')[0];
        return firstFolder !== path ? firstFolder : null;
    }

    async upload_files(files) {
        const count = await this.fileProcessor.process_local_files(files);
        this.uiRenderer.setup_filters();
        this.uiRenderer.display_essay_list();
        this.uiRenderer.show_notification(`✓ Added ${count} files!`);
    }

    async load_from_github() {
        this.uiRenderer.show_notification('Loading from GitHub...');
        const count = await this.gitHubLoader.load_from_github();
        this.uiRenderer.setup_filters();
        this.uiRenderer.display_essay_list();
        this.uiRenderer.show_notification(`✓ Loaded ${count} files!`);
    }

    copy_essay_text() {
        const text = document.getElementById('essayText').innerText;
        this.copy_text(text);
    }

    copy_evaluation_text() {
        const text = document.getElementById('evaluationText').innerText;
        this.copy_text(text);
    }

    copy_text(text) {
        navigator.clipboard.writeText(text);
        this.uiRenderer.show_notification('✓ Copied!');
    }
}

const app = new Application();