// upload.js - Simple and reliable version
function uploadFile() {
    console.log("uploadFile function called");
    
    const input = document.getElementById("fileInput");
    if (!input || !input.files.length) {
        showToast("Please select a file", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", input.files[0]);

    console.log("Sending upload request...");

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => {
        console.log("Response status:", res.status);
        if (res.status === 413) {
            throw new Error("File too large (max 10MB)");
        }
        return res.json();
    })
    .then(data => {
        console.log("Response data:", data);
        if (data.error) {
            throw new Error(data.error);
        }
        showToast("File uploaded successfully");
        input.value = "";
        
        // Reload file list
        if (window.loadMyFiles && typeof window.loadMyFiles === 'function') {
            window.loadMyFiles();
        }
    })
    .catch(err => {
        console.error("Upload error:", err);
        showToast(err.message || "Upload failed", "error");
    });
}

// Make available globally
window.uploadFile = uploadFile;
console.log("uploadFile function registered to window");