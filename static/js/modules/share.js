// share.js - Fixed version with proper suggestion selection
let debounceTimer;
let isSelectingSuggestion = false; // Flag to track if we're clicking a suggestion

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('shareUsername');
    if (usernameInput) {
        usernameInput.addEventListener('input', handleUsernameInput);
        usernameInput.addEventListener('blur', function() {
            // Only hide if we're not clicking on a suggestion
            setTimeout(() => {
                if (!isSelectingSuggestion) {
                    document.getElementById('suggestionsGrid').style.display = 'none';
                }
            }, 200);
        });
    }
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function(event) {
        const usernameInput = document.getElementById('shareUsername');
        const suggestionsGrid = document.getElementById('suggestionsGrid');
        
        if (usernameInput && suggestionsGrid && 
            !usernameInput.contains(event.target) && 
            !suggestionsGrid.contains(event.target)) {
            suggestionsGrid.style.display = 'none';
        }
    });
});

// Handle username input for suggestions
function handleUsernameInput() {
    clearTimeout(debounceTimer);
    const query = this.value.trim();
    
    if (query.length < 2) {
        document.getElementById('suggestionsGrid').style.display = 'none';
        return;
    }
    
    debounceTimer = setTimeout(() => {
        fetchUsernameSuggestions(query);
    }, 300);
}

// Fetch username suggestions
async function fetchUsernameSuggestions(query) {
    try {
        const res = await fetch(`/api/users/suggest?q=${encodeURIComponent(query)}`);
        if (!res.ok) return;
        
        const usernames = await res.json();
        displaySuggestions(usernames);
    } catch (err) {
        console.error('Error fetching suggestions:', err);
    }
}

// Display suggestions in grid
function displaySuggestions(usernames) {
    const grid = document.getElementById('suggestionsGrid');
    
    if (!usernames || usernames.length === 0) {
        grid.style.display = 'none';
        return;
    }
    
    grid.innerHTML = usernames.map(username => 
        `<div class="suggestion-chip" 
              onmousedown="event.preventDefault()" 
              onclick="selectUsername('${username}')">
            ${username}
         </div>`
    ).join('');
    
    grid.style.display = 'grid';
}

// Select username from suggestion
function selectUsername(username) {
    isSelectingSuggestion = true; // Set flag
    
    const usernameInput = document.getElementById('shareUsername');
    usernameInput.value = username;
    
    // Hide suggestions grid
    const suggestionsGrid = document.getElementById('suggestionsGrid');
    suggestionsGrid.style.display = 'none';
    
    // Focus back on input for better UX
    usernameInput.focus();
    
    // Reset flag after a short delay
    setTimeout(() => {
        isSelectingSuggestion = false;
    }, 100);
    
    // Optional: Trigger any additional validation or UI updates
    console.log('Username selected:', username);
}

// Submit share form
async function submitShare() {
    let fileId;
    
    // Get file ID from either hidden input or dropdown
    const selectedFileId = document.getElementById("selectedFileId");
    if (selectedFileId) {
        fileId = selectedFileId.value;
    } else {
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

    // Get expiry (for future implementation)
    const expiryOption = document.querySelector('input[name="expiry"]:checked');
    const expiryDays = expiryOption ? expiryOption.value : null;

    // Disable button to prevent double submission
    const shareBtn = document.getElementById('shareBtn');
    shareBtn.disabled = true;
    shareBtn.textContent = 'Sharing...';

    try {
        const res = await fetch("/api/share", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                file_id: parseInt(fileId),
                username: username,
                expiry_days: expiryDays
            })
        });

        const data = await res.json();
        shareBtn.disabled = false;
        shareBtn.textContent = 'Share File';

        if (res.ok) {
            showToast("File shared successfully!");
            
            // Clear the form
            document.getElementById("shareUsername").value = "";
            
            // If from dropdown, reset it
            const fileSelect = document.getElementById("fileSelect");
            if (fileSelect) {
                fileSelect.value = "";
            }
            
            // Refresh both lists
            loadSharesWithMe();
            loadRecentShares();
        } else {
            if (res.status === 401) {
                showToast("Session expired. Please log in again.", "error");
                setTimeout(() => window.location.href = "/login", 1500);
            } else {
                showToast(data.error || "Share failed", "error");
            }
        }
    } catch (err) {
        console.error("Share error:", err);
        shareBtn.disabled = false;
        shareBtn.textContent = 'Share File';
        showToast("Network error", "error");
    }
}

// Load files shared with me
async function loadSharesWithMe() {
    const container = document.getElementById("sharedWithMe");
    if (!container) return;

    try {
        const res = await fetch("/api/shares/with-me");
        if (!res.ok) {
            if (res.status === 401) {
                // Handle unauthorized - maybe redirect to login
                return;
            }
            throw new Error('Failed to load');
        }

        const shares = await res.json();

        if (!shares || shares.length === 0) {
            container.innerHTML = '<div class="empty-list">No files shared with you yet</div>';
            return;
        }

        container.innerHTML = shares.map(share => `
            <div class="share-item">
                <div class="share-item-icon">
                    ${getFileIcon(share.original_filename)}
                </div>
                <div class="share-item-details">
                    <div class="share-item-name">${share.original_filename}</div>
                    <div class="share-item-meta">
                        From: ${share.shared_by} • ${formatDate(share.shared_at)}
                    </div>
                </div>
                <a href="/file/download/${share.file_id}" class="share-item-action">Download</a>
            </div>
        `).join('');
    } catch (err) {
        console.error("Error loading shares:", err);
        container.innerHTML = '<div class="empty-list">Error loading shares</div>';
    }
}

// Load recent shares by me
async function loadRecentShares() {
    const container = document.getElementById("recentlySharedByMe");
    if (!container) return;

    try {
        const res = await fetch("/api/shares/recent");
        if (!res.ok) {
            if (res.status === 401) {
                return;
            }
            throw new Error('Failed to load');
        }

        const shares = await res.json();

        if (!shares || shares.length === 0) {
            container.innerHTML = '<div class="empty-list">You haven\'t shared any files yet</div>';
            return;
        }

        container.innerHTML = shares.map(share => `
            <div class="share-item">
                <div class="share-item-icon">
                    ${getFileIcon(share.original_filename)}
                </div>
                <div class="share-item-details">
                    <div class="share-item-name">${share.original_filename}</div>
                    <div class="share-item-meta">
                        With: ${share.shared_with} • ${formatDate(share.shared_at)}
                    </div>
                </div>
                <span class="share-item-action" style="color: #666;">Shared</span>
            </div>
        `).join('');
    } catch (err) {
        console.error("Error loading recent shares:", err);
        container.innerHTML = '<div class="empty-list">Error loading recent shares</div>';
    }
}

// Helper function to get file icon
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toUpperCase().substring(0, 3);
    return ext;
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Make functions available globally
window.submitShare = submitShare;
window.selectUsername = selectUsername;
window.loadSharesWithMe = loadSharesWithMe;
window.loadRecentShares = loadRecentShares;