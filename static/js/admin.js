console.log("File loaded")
/* sidebar toggler */

const toggleBtn = document.getElementById("toggleSidebar");
      const sidebar = document.getElementById("sidebar");
      const main = document.getElementById("main");

      toggleBtn.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
        main.classList.toggle("collapsed");
      });


/* delete msg function */

function openDeleteModal(itemName, url) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const modalText = document.getElementById('modal-text');

    modalText.innerText = `Are you sure you want to delete "${itemName}"?`;
    form.action = url;
    modal.style.display = 'flex'; 
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.remove('show');
    setTimeout(() => {
        modal.style.display = 'none';
    }, 300);
}

window.onclick = function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target === modal) {
        closeDeleteModal();
    }
};

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

    if (!imagePreview) return;

    function showImageInput() {
        if (imageInput) {
            imageInput.style.display = 'block';
            if (imageInput.previousElementSibling?.tagName === 'LABEL') {
                imageInput.previousElementSibling.style.display = 'block';
            }
        }
    }

    function clearPreview() {
        if (imageInput) imageInput.value = '';
        imagePreview.innerHTML = '<p class="no-image">No image selected</p>';
        if (removeInput) removeInput.value = '1';
        showImageInput();
    }

    // ✅ EVENT DELEGATION — works for edit + add
    imagePreview.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-image')) {
            e.preventDefault();
            clearPreview();
        }
    });

    // Handle new image selection
    if (imageInput) {
        imageInput.addEventListener('change', function () {
            const file = this.files[0];

            if (file) {
                if (removeInput) removeInput.value = '0';

                const reader = new FileReader();
                reader.onload = function (e) {
                    imagePreview.innerHTML = `
                        <div class="preview-wrapper" style="position:relative; display:inline-block;">
                            <img src="${e.target.result}"
                                 style="max-width:200px; max-height:150px; border:1px solid #e5e7eb; border-radius:4px;">
                            <span class="remove-image"
                                  style="
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
                                    font-weight:bold;
                                    z-index:10;">×</span>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    }

});
