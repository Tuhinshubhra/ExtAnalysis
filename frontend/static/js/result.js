function loadBasicInfo(analysisId) {
    fetch(`/api/result/${analysisId}/basic_info`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            updateBasicInfo(data);
        });
}

function loadFiles(analysisId) {
    fetch(`/api/result/${analysisId}/files`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            document.getElementById('files-container').innerHTML = data.files_table;
            updateFileCounts(data.counts);
        });
}

function loadUrls(analysisId) {
    fetch(`/api/result/${analysisId}/urls`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            document.getElementById('urls-container').innerHTML = data.urls_table;
        });
}

// Similar functions for other data types...

function loadAllData(analysisId) {
    loadBasicInfo(analysisId);
    loadFiles(analysisId);
    loadUrls(analysisId);
    loadPermissions(analysisId);
    loadDomains(analysisId);
    loadIps(analysisId);
    loadEmails(analysisId);
    loadBtc(analysisId);
    loadComments(analysisId);
    loadBase64(analysisId);
    loadManifest(analysisId);
}

// Helper functions
function updateBasicInfo(data) {
    document.getElementById('extension-name').textContent = data.name;
    document.getElementById('extension-version').textContent = data.version;
    document.getElementById('extension-author').textContent = data.author;
    document.getElementById('extension-description').textContent = data.description;
    document.getElementById('extension-type').innerHTML = data.extension_type;
}

function updateFileCounts(counts) {
    document.getElementById('js-count').textContent = counts.js;
    document.getElementById('css-count').textContent = counts.css;
    document.getElementById('html-count').textContent = counts.html;
    document.getElementById('json-count').textContent = counts.json;
    document.getElementById('other-count').textContent = counts.other;
    document.getElementById('static-count').textContent = counts.static;
}

function showError(message) {
    // Implement error display logic
    console.error(message);
} 