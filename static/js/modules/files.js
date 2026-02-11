// files.js
async function loadMyFiles() {
  const list = document.getElementById("fileList");
  if (!list) return;

  list.innerHTML = "";

  try {
    const res = await fetch("/api/files/my");
    if (!res.ok) {
      console.error("Failed to load files:", res.status);
      return;
    }

    const files = await res.json();

    if (!files || !files.length) {
      list.innerHTML = "<li>No uploads yet</li>";
      return;
    }

    files.forEach(file => {
      const li = document.createElement("li");
      li.className = "file-item";

      li.innerHTML = `
        <span class="file-name">
          ${file.original_filename}
          <small>${new Date(file.uploaded_at).toLocaleString()}</small>
        </span>

        <div class="file-actions">
          <div class="icon download" title="Download" onclick="downloadFile(${file.id})"></div>
          <div class="icon share" title="Share" onclick="goToShare(${file.id})"></div>
          <div class="icon archive" title="Archive" onclick="archiveFile(${file.id})"></div>
        </div>
      `;

      list.appendChild(li);
    });
  } catch (err) {
    console.error("Load files error:", err);
    showToast("Failed to load files", "error");
  }
}

async function loadSharedFiles() {
  const list = document.getElementById("sharedList");
  if (!list) return;

  list.innerHTML = "";

  try {
    // You need to create this endpoint in files.py
    const res = await fetch("/api/files/shared");
    if (!res.ok) {
      console.error("Failed to load shared files:", res.status);
      list.innerHTML = "<li>No shared files</li>";
      return;
    }

    const files = await res.json();

    if (!files || !files.length) {
      list.innerHTML = "<li>No shared files</li>";
      return;
    }

    files.forEach(file => {
      const li = document.createElement("li");
      li.className = "file-item";
      li.innerHTML = `
        <span>${file.original_filename}
          <small>from ${file.owner}</small>
        </span>
      `;
      list.appendChild(li);
    });
  } catch (err) {
    console.error("Load shared files error:", err);
    list.innerHTML = "<li>Error loading shared files</li>";
  }
}

function downloadFile(id) {
  window.location.href = `/file/download/${id}`;
}

function goToShare(id) {
  window.location.href = `/share?file=${id}`;
}

async function archiveFile(fileId) {
  try {
    const res = await fetch("/file/archive", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_id: fileId })
    });

    const data = await res.json();

    if (res.ok) {
      showToast("Archived");
      loadMyFiles();
    } else {
      showToast(data.error || "Archive failed", "error");
    }
  } catch (err) {
    console.error("Archive error:", err);
    showToast("Network error", "error");
  }
}

// Make functions available globally
window.loadMyFiles = loadMyFiles;
window.loadSharedFiles = loadSharedFiles;
window.downloadFile = downloadFile;
window.goToShare = goToShare;
window.archiveFile = archiveFile;

// Auto-load files when page loads
document.addEventListener('DOMContentLoaded', function() {
  if (typeof loadMyFiles === 'function') {
    loadMyFiles();
  }
  if (typeof loadSharedFiles === 'function') {
    loadSharedFiles();
  }
});
