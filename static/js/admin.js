console.log("load")

function getCSRFToken() {
    let cookieValue = null;
    const name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/* sidebar toggler */

const toggleBtn = document.getElementById("toggleSidebar");
      const sidebar = document.getElementById("sidebar");
      const main = document.getElementById("main");

      toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
        main.classList.toggle("collapsed");
      });


/* delete msg function */

function openDeleteModal(modelName, itemNameOrCount, url, isBulk = false) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const modalText = document.getElementById('modal-text');

    // 1. Handle IDs for Bulk
    form.querySelectorAll('input[name="ids"]').forEach(i => i.remove());
    
    if (isBulk) {
        const selected = Array.from(document.querySelectorAll('.row-checkbox:checked'))
                              .map(cb => cb.value);
        if (!selected.length) return alert("Select at least one item!");
        
        modalText.innerText = `Are you sure you want to delete ${selected.length} ${modelName}(s)?`;
        
        const idsInput = document.createElement('input');
        idsInput.type = 'hidden';
        idsInput.name = 'ids';
        idsInput.value = selected.join(',');
        form.appendChild(idsInput);
    } else {
        // 2. Handle Single Delete
        modalText.innerText = `Are you sure you want to delete "${itemNameOrCount}"?`;
    }

    // 3. Set Action and Show
    form.action = url;
    modal.style.display = 'flex';
    setTimeout(() => modal.classList.add('show'), 10);
}

    function closeDeleteModal() {
        const modal = document.getElementById('deleteModal');
        modal.classList.remove('show');
        setTimeout(() => modal.style.display = 'none', 300);
    }

    window.onclick = function(event) {
        const modal = document.getElementById('deleteModal');
        if (event.target === modal) closeDeleteModal();
    }





/* Message function */
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.message');

    if (alerts.length > 0) {
        alerts.forEach(function(alert) {
            // Wait 3 seconds
            setTimeout(function() {
                // Trigger the CSS transition
                alert.style.opacity = '0';

                // Remove from DOM after transition (0.6s)
                setTimeout(function() {
                    alert.style.display = 'none';
                }, 600); 
            }, 3000);
        });
    }
});



/* Preview image function */
document.addEventListener('DOMContentLoaded', function () {

    const imageInput = document.querySelector('input[type="file"]');
    const imagePreview = document.getElementById('imagePreview');
    const removeInput = document.getElementById('remove_image');
    const imageLabel = imageInput ? imageInput.previousElementSibling : null;

    if (!imageInput || !imagePreview) return;

    // Show the file input
    function hideImageInput() {
        imageInput.style.opacity = '0';
        imageInput.style.height = '0';
        imageInput.style.position = 'absolute';
        if (imageLabel) imageLabel.style.display = 'none';
    }

    function showImageInput() {
        imageInput.style.opacity = '1';
        imageInput.style.height = 'auto';
        imageInput.style.position = 'static';
        if (imageLabel) imageLabel.style.display = 'block';
    }

    // Clear preview and mark remove
    function clearPreview() {
        removeInput.value = '1';  // mark for removal
        imagePreview.innerHTML = '<p class="no-image">No image selected</p>';
        showImageInput();
        imageInput.value = ''; // clear file input
    }

    // Remove image when clicking ×
    imagePreview.addEventListener('click', function(e) {
        if (e.target.closest('.remove-image')) {
            e.preventDefault();
            clearPreview();
        }
    });

    // Upload new image
    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (!file) return;

        removeInput.value = '0'; // user uploaded new image
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.innerHTML = `
                <div class="preview-wrapper" style="position:relative; display:inline-block;">
                    <img src="${e.target.result}" 
                         style="max-width:200px; max-height:150px; border:1px solid #e5e7eb; border-radius:4px;">
                    <span class="remove-image" style="
                          position:absolute;
                          top:-5px;
                          right:-5px;
                          background:#ef4444;
                          color:white;
                          border-radius:50%;
                          width:20px;
                          height:20px;
                          text-align:center;
                          line-height:20px;
                          cursor:pointer;
                          font-weight:bold;">×</span>
                </div>
            `;
            hideImageInput();
        };
        reader.readAsDataURL(file);
    });

    // Initial state: hide input if image exists
    if (imagePreview.querySelector('img')) {
        hideImageInput();
    } else {
        showImageInput();
    }

});






/* generete slug function */

  function slugify(text) {
    return text
      .toString()
      .toLowerCase()
      .trim()
      .replace(/\s+/g, '-')        
      .replace(/[^\w\-]+/g, '')      
      .replace(/\-\-+/g, '-');        
  }

  document.addEventListener("DOMContentLoaded", function () {
    const titleInput = document.getElementById("id_title");
    const slugInput = document.getElementById("id_slug");

    if (!titleInput || !slugInput) return;

  
    let slugTouched = false;

    slugInput.addEventListener("input", function () {
      slugTouched = true;
    });

    titleInput.addEventListener("input", function () {
      if (!slugTouched) {
        slugInput.value = slugify(titleInput.value);
      }
    });
  });

  /* toggle status function */


function toggleStatus(el) {
    const url = el.dataset.url;
    const targetId = el.dataset.target;

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
        }
    })
    .then(res => res.json())
    .then(data => {
        const icon = el.querySelector("i");

        if (data.status) {
            icon.classList.remove("fa-toggle-off");
            icon.classList.add("fa-toggle-on");
            icon.style.color = "#22c55e";
        } else {
            icon.classList.remove("fa-toggle-on");
            icon.classList.add("fa-toggle-off");
            icon.style.color = "#9ca3af";
        }

        // ✅ Update status text in table
        if (targetId) {
            const statusCell = document.getElementById(targetId);
            if (statusCell) {
                statusCell.innerText = data.status ? "Active" : "Inactive";
                statusCell.className = data.status ? "status-active" : "status-inactive";
            }
        }
        if (data.message) {
            const container = document.getElementById('messages-container');
            if (container) {
                // Create the div
                const msgDiv = document.createElement("div");
                
                // Add classes: 'message' is your base, 'success' matches Django tags
                msgDiv.className = `message ${data.status ? 'success' : 'info'}`;
                msgDiv.innerText = data.message;

                // Append to the container
                container.appendChild(msgDiv);

                // Apply the same fade-out logic you use for standard messages
                setTimeout(() => {
                    msgDiv.style.opacity = '0';
                    setTimeout(() => {
                        msgDiv.remove();
                    }, 600);
                }, 3000);
            }
        }
    })
    .catch(err => console.error("Toggle failed:", err));
}

/* bulk action function */

document.getElementById('select-all').addEventListener('change', function () {
    const checked = this.checked;
    document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = checked);
});