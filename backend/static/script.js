// ==============================
// TOAST HELPER
// ==============================
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("show"));

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ==============================
// UPLOAD LOGIC
// ==============================
async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const uploadBtn = document.getElementById("uploadBtn");

  if (!fileInput.files.length) {
    showToast("Please select a file", "error");
    return;
  }

  uploadBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const res = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    uploadBtn.disabled = false;

    if (res.ok) {
      showToast(data.message || "File uploaded successfully", "success");
      fileInput.value = "";
      loadMyFiles();
    } else {
      if (res.status === 401) {
        showToast("Session expired. Please log in again.", "error");
        setTimeout(() => window.location.href = "/login", 1200);
      } else {
        showToast(data.error || "Upload failed", "error");
      }
    }
  } catch {
    uploadBtn.disabled = false;
    showToast("Network error", "error");
  }
}

// ==============================
// DOWNLOAD FILE
// ==============================
async function downloadFile(fileId) {
  try {
    const res = await fetch(`/download/${fileId}`);

    if (res.status === 401) {
      showToast("Session expired. Please log in again.", "error");
      setTimeout(() => window.location.href = "/login", 1200);
      return;
    }

    if (res.status === 403) {
      showToast("You don't have access to this file.", "error");
      return;
    }

    if (!res.ok) {
      showToast("Access denied or file unavailable.", "error");
      return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "";
    document.body.appendChild(a);
    a.click();

    a.remove();
    window.URL.revokeObjectURL(url);

    showToast("Download started", "success");
  } catch {
    showToast("Network error while downloading", "error");
  }
}

// ==============================
// LOAD MY FILES
// ==============================
async function loadMyFiles() {
  const list = document.getElementById("fileList");
  if (!list) return;

  list.innerHTML = "";

  try {
    const res = await fetch("/api/files/my");
    if (!res.ok) return;

    const files = await res.json();

    if (!files.length) {
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
        <button onclick="downloadFile(${file.id})">Download</button>
      `;

      list.appendChild(li);
    });
  } catch {
    showToast("Failed to load files", "error");
  }
}

// ==============================
// LOAD SHARED FILES
// ==============================
async function loadSharedFiles() {
  const list = document.getElementById("sharedFileList");
  if (!list) return;

  list.innerHTML = "";

  try {
    const res = await fetch("/api/files/shared");
    if (!res.ok) return;

    const files = await res.json();

    if (!files.length) {
      list.innerHTML = "<li>No shared files</li>";
      return;
    }

    files.forEach(file => {
      const expired =
        file.expires_at && new Date(file.expires_at) < new Date();

      const li = document.createElement("li");
      li.className = "file-item";

      li.innerHTML = `
        <span class="file-name">
          ${file.original_filename}
          <small>Owner: ${file.owner}</small>
          <small class="${expired ? "expired" : ""}">
            ${expired
              ? "Expired"
              : "Expires: " + (file.expires_at || "Never")}
          </small>
        </span>
        <button onclick="downloadFile(${file.id})">
          Download
        </button>
      `;

      list.appendChild(li);
    });
  } catch {
    showToast("Failed to load shared files", "error");
  }
}

// ==============================
// INIT
// ==============================
document.addEventListener("DOMContentLoaded", () => {
  loadMyFiles();
  loadSharedFiles();
});
