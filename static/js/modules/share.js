// share.js - UPDATED VERSION
async function submitShare() {
  let fileId;
  
  // Get file ID from either hidden input (direct share) or dropdown (general share)
  const selectedFileId = document.getElementById("selectedFileId");
  if (selectedFileId) {
    // Direct share from dashboard
    fileId = selectedFileId.value;
  } else {
    // General share from menu
    const fileSelect = document.getElementById("fileSelect");
    fileId = fileSelect.value;
    
    if (!fileId) {
      showToast("Please select a file", "error");
      return;
    }
  }
  
  const username = document.getElementById("shareUsername").value.trim();
  
  if (!username) {
    showToast("Username required", "error");
    return;
  }

  try {
    const res = await fetch("/api/share", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        file_id: parseInt(fileId),
        username: username
      })
    });

    const data = await res.json();

    if (res.ok) {
      showToast("File shared successfully!");
      
      // Clear the form
      document.getElementById("shareUsername").value = "";
      
      // If from dropdown, reset it
      const fileSelect = document.getElementById("fileSelect");
      if (fileSelect) {
        fileSelect.value = "";
      }
    } else {
      showToast(data.error || "Share failed", "error");
    }
  } catch (err) {
    console.error("Share error:", err);
    showToast("Network error", "error");
  }
}

window.submitShare = submitShare;