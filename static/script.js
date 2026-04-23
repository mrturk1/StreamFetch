document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('url-input');
    const downloadBtn = document.getElementById('download-btn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.getElementById('loading-spinner');
    const messageBox = document.getElementById('message-box');
    const fileList = document.getElementById('file-list');
    
    // Progress elements
    const progressContainer = document.getElementById('progress-container');
    const progressStatus = document.getElementById('progress-status');
    const progressPercent = document.getElementById('progress-percent');
    const progressBarFill = document.getElementById('progress-bar-fill');

    let progressInterval;

    // Load initial files
    fetchFiles();

    downloadBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        const format = document.querySelector('input[name="format"]:checked').value;
        const downloadId = Date.now().toString();

        if (!url) {
            showMessage('Please enter a valid URL', 'error');
            return;
        }

        // Set loading state
        setLoading(true);
        showMessage('', '');
        
        // Show progress UI
        progressContainer.classList.remove('hidden');
        progressStatus.textContent = 'Preparing...';
        progressPercent.textContent = '0%';
        progressBarFill.style.width = '0%';

        // Start polling for progress
        progressInterval = setInterval(() => checkProgress(downloadId), 500);

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, format, download_id: downloadId }),
            });

            const data = await response.json();
            clearInterval(progressInterval);
            
            // Final progress update
            progressPercent.textContent = '100%';
            progressBarFill.style.width = '100%';
            
            setTimeout(() => {
                progressContainer.classList.add('hidden');
            }, 2000);

            if (response.ok) {
                showMessage(`Successfully downloaded: ${data.filename}`, 'success');
                urlInput.value = '';
                fetchFiles();
            } else {
                showMessage(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            clearInterval(progressInterval);
            progressContainer.classList.add('hidden');
            showMessage('An error occurred. Please try again.', 'error');
        } finally {
            setLoading(false);
        }
    });

    async function checkProgress(downloadId) {
        try {
            const response = await fetch(`/progress/${downloadId}`);
            if (response.ok) {
                const data = await response.json();
                
                if (data.status === 'downloading') {
                    progressStatus.textContent = 'Downloading...';
                    progressPercent.textContent = data.percent;
                    progressBarFill.style.width = data.percent;
                } else if (data.status === 'processing') {
                    progressStatus.textContent = 'Processing (Converting Audio/Video)...';
                    progressPercent.textContent = '100%';
                    progressBarFill.style.width = '100%';
                }
            }
        } catch (error) {
            console.error('Progress error:', error);
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            downloadBtn.disabled = true;
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');
        } else {
            downloadBtn.disabled = false;
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    }

    function showMessage(text, type) {
        if (!text) {
            messageBox.classList.add('hidden');
            return;
        }
        
        messageBox.textContent = text;
        messageBox.className = `message ${type}`;
        messageBox.classList.remove('hidden');
    }

    async function fetchFiles() {
        try {
            const response = await fetch('/files');
            const files = await response.json();
            
            fileList.innerHTML = '';
            
            if (files.length === 0) {
                fileList.innerHTML = '<div class="file-item"><span class="file-name">No downloaded files yet.</span></div>';
                return;
            }

            files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                const fileName = document.createElement('span');
                fileName.className = 'file-name';
                fileName.textContent = file;
                
                const folderBtn = document.createElement('button');
                folderBtn.className = 'folder-btn';
                folderBtn.title = 'Open file location';
                folderBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                    </svg>
                `;
                
                folderBtn.addEventListener('click', async () => {
                    try {
                        await fetch(`/open_folder/${encodeURIComponent(file)}`, { method: 'POST' });
                    } catch (error) {
                        console.error('Failed to open folder:', error);
                    }
                });
                
                fileItem.appendChild(fileName);
                fileItem.appendChild(folderBtn);
                fileList.appendChild(fileItem);
            });
        } catch (error) {
            console.error('Error loading files:', error);
        }
    }
});
