document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");
    const uploadProgress = document.getElementById("upload-progress");
    const uploadStatusText = document.getElementById("upload-status-text");
    const docList = document.getElementById("doc-list");
    const docCount = document.getElementById("doc-count");
    
    const searchForm = document.getElementById("search-form");
    const queryInput = document.getElementById("query-input");
    const searchButton = document.getElementById("search-button");
    const loadingState = document.getElementById("loading-state");
    const resultsContainer = document.getElementById("results-container");
    
    const chatbotAnswerText = document.getElementById("chatbot-answer-text");
    const sourcesSection = document.getElementById("sources-section");
    const sourcesList = document.getElementById("sources-list");
    const semanticResultsList = document.getElementById("semantic-results-list");
    
    const errorBanner = document.getElementById("error-banner");
    const errorMessage = document.getElementById("error-message");
    const errorClose = document.getElementById("error-close");
    const healthStatus = document.getElementById("health-status");

    // Initialize Application
    startHeartbeat();
    checkHealth();
    loadDocuments();

    function startHeartbeat() {
        const sendPing = () => {
            fetch("/api/heartbeat", { method: "POST" }).catch(() => {});
        };
        sendPing();
        setInterval(sendPing, 4000);

        window.addEventListener("pagehide", () => {
            if (navigator.sendBeacon) {
                navigator.sendBeacon("/api/shutdown");
            } else {
                fetch("/api/shutdown", { method: "POST", keepalive: true }).catch(() => {});
            }
        });
        window.addEventListener("beforeunload", () => {
            if (navigator.sendBeacon) {
                navigator.sendBeacon("/api/shutdown");
            }
        });
    }

    // Event Listeners for Upload Dropzone
    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    // Error Close
    errorClose.addEventListener("click", () => {
        errorBanner.classList.add("hidden");
    });

    // Search Form Submission
    searchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        hideError();
        showLoading(true);
        resultsContainer.classList.add("hidden");

        try {
            const response = await fetch("/api/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: query,
                    session_id: "default",
                    top_k: 5
                })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Server returned status ${response.status}`);
            }

            const data = await response.json();
            renderResults(data);
        } catch (err) {
            showError(`Query failed: ${err.message}`);
        } finally {
            showLoading(false);
        }
    });

    // --- HELPER FUNCTIONS ---

    async function checkHealth() {
        try {
            const res = await fetch("/api/health");
            if (res.ok) {
                healthStatus.textContent = "Online";
                healthStatus.previousElementSibling.className = "status-dot green";
            } else {
                throw new Error();
            }
        } catch {
            healthStatus.textContent = "Offline / Issues";
            healthStatus.previousElementSibling.className = "status-dot red";
        }
    }

    async function loadDocuments() {
        try {
            const res = await fetch("/api/documents");
            if (!res.ok) return;
            const data = await res.json();
            renderDocuments(data.documents || []);
        } catch (err) {
            console.error("Failed to load documents:", err);
        }
    }

    function renderDocuments(docs) {
        docCount.textContent = `${docs.length} ${docs.length === 1 ? 'file' : 'files'}`;
        if (docs.length === 0) {
            docList.innerHTML = '<div class="empty-docs">No documents uploaded yet.</div>';
            return;
        }

        docList.innerHTML = docs.map(doc => `
            <div class="doc-item" data-id="${doc.document_id}">
                <div class="doc-info">
                    <div class="doc-icon">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                    </div>
                    <div class="doc-details">
                        <span class="doc-name" title="${doc.filename}">${escapeHtml(doc.filename)}</span>
                        <span class="doc-meta">${doc.total_pages} pages</span>
                    </div>
                </div>
                <button class="btn-delete" title="Delete document" onclick="deleteDoc('${doc.document_id}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
        `).join('');
    }

    window.deleteDoc = async function(docId) {
        if (!confirm("Are you sure you want to delete this document from both intelligence systems?")) return;
        try {
            const res = await fetch(`/api/documents/${docId}`, { method: "DELETE" });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Delete failed");
            }
            loadDocuments();
        } catch (err) {
            showError(err.message);
        }
    };

    async function handleFileUpload(file) {
        if (!file.name.toLowerCase().endsWith(".pdf")) {
            showError("Invalid file. Please upload a PDF document.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        uploadProgress.classList.remove("hidden");
        uploadStatusText.textContent = `Processing "${file.name}" across dual engines...`;
        hideError();

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || "Upload failed");
            }

            fileInput.value = "";
            loadDocuments();
        } catch (err) {
            showError(`Upload error: ${err.message}`);
        } finally {
            uploadProgress.classList.add("hidden");
        }
    }

    function renderResults(data) {
        const chatbot = data.chatbot || {};
        const semantic = data.semantic_search || {};

        // 1. AI ANSWER
        chatbotAnswerText.textContent = chatbot.answer || "No response received.";

        // 2. SOURCES
        const sources = chatbot.sources || [];
        if (sources.length > 0) {
            sourcesSection.classList.remove("hidden");
            sourcesList.innerHTML = sources.map(s => `
                <div class="source-card">
                    <div class="source-header">
                        <span class="source-doc" title="${s.document}">${escapeHtml(s.document)}</span>
                        <span class="source-page">Page ${s.page}</span>
                    </div>
                    <div class="source-snippet">"${escapeHtml(s.text)}"</div>
                </div>
            `).join('');
        } else {
            sourcesSection.classList.add("hidden");
        }

        // 3. SEMANTIC SEARCH RESULTS
        const results = semantic.results || [];
        if (results.length > 0) {
            semanticResultsList.innerHTML = results.map(r => `
                <div class="semantic-card">
                    <div class="semantic-header">
                        <div class="semantic-left">
                            <span class="rank-pill">#${r.rank}</span>
                            <span class="semantic-doc">${escapeHtml(r.document)}</span>
                        </div>
                        <div class="semantic-right">
                            <span class="page-badge">Page ${r.page}</span>
                            <span class="score-badge">Similarity: ${(r.score * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                    <div class="semantic-text">${escapeHtml(r.text)}</div>
                </div>
            `).join('');
        } else {
            semanticResultsList.innerHTML = '<div class="empty-docs">No matching semantic passages found.</div>';
        }

        resultsContainer.classList.remove("hidden");
    }

    function showLoading(isLoading) {
        if (isLoading) {
            loadingState.classList.remove("hidden");
            searchButton.disabled = true;
        } else {
            loadingState.classList.add("hidden");
            searchButton.disabled = false;
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorBanner.classList.remove("hidden");
    }

    function hideError() {
        errorBanner.classList.add("hidden");
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>"']/g, function(m) {
            return {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }[m];
        });
    }
});
