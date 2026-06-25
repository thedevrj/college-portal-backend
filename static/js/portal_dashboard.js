// Portal Dashboard Custom JavaScript
// This file is used for general UI tweaks across the ERP portal.

/**
 * Sidebar User Panel Fix
 * Replaces the numeric Staff ID with the Faculty's Full Name
 * and ensures the correct Profile Photo is displayed.
 */
function updateSidebarIdentity() {
    if (window.PORTAL_USER) {
        // 1. Update Name in Sidebar
        // Jazzmin uses .user-panel .info a or span
        const nameElements = document.querySelectorAll(".user-panel .info a, .user-panel .info span");
        nameElements.forEach(el => {
            if (window.PORTAL_USER.displayName) {
                el.textContent = window.PORTAL_USER.displayName;
                el.style.whiteSpace = "normal";
                el.style.lineHeight = "1.2";
            }
        });

        // 2. Update Avatar in Sidebar
        if (window.PORTAL_USER.avatarUrl) {
            const avatarImg = document.querySelector(".user-panel .image img");
            if (avatarImg) {
                avatarImg.src = window.PORTAL_USER.avatarUrl;
                avatarImg.style.objectFit = "cover";
                avatarImg.style.width = "2.1rem";
                avatarImg.style.height = "2.1rem";
            } else {
                // If there's an icon instead of an image, replace it
                const imageContainer = document.querySelector(".user-panel .image");
                if (imageContainer) {
                    imageContainer.innerHTML = `<img src="${window.PORTAL_USER.avatarUrl}" class="img-circle elevation-2" style="width: 2.1rem; height: 2.1rem; object-fit: cover;" alt="User">`;
                }
            }
        }
    }
}

// Execute on load
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", updateSidebarIdentity);
} else {
    updateSidebarIdentity();
}

// Also run periodically to catch any dynamic loads or race conditions with Jazzmin
setTimeout(updateSidebarIdentity, 500);
setTimeout(updateSidebarIdentity, 2000);


/**
 * Global ERP Dashboard Widgets
 * Fetches stats from the API and renders them in AdminLTE 3 small-boxes
 */
function renderGlobalDashboard() {
    const container = document.getElementById("global-dashboard-widgets");
    if (!container) return; // Not on the dashboard page

    fetch('/portal/api/dashboard-stats/', { credentials: 'same-origin' })
        .then(response => {
            if (!response.ok) throw new Error('Unauthorized or missing API');
            return response.json();
        })
        .then(data => {
            container.innerHTML = `
                <!-- Academics -->
                <div class="col-lg-3 col-6">
                    <div class="small-box bg-info" style="border-radius: 0.5rem; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div class="inner" style="padding: 1.5rem;">
                            <h3>${data.academics.departments} <sup style="font-size: 20px">Depts</sup></h3>
                            <p>${data.academics.programs} Programs</p>
                        </div>
                        <div class="icon" style="top: 10px;">
                            <i class="fas fa-university"></i>
                        </div>
                        <a href="/admin/academics/department/" class="small-box-footer" style="padding: 0.5rem;">More info <i class="fas fa-arrow-circle-right"></i></a>
                    </div>
                </div>
                
                <!-- Faculty & Staff -->
                <div class="col-lg-3 col-6">
                    <div class="small-box bg-success" style="border-radius: 0.5rem; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div class="inner" style="padding: 1.5rem;">
                            <h3>${data.people.faculty + data.people.staff} <sup style="font-size: 20px">Total</sup></h3>
                            <p>Faculty & Staff Profiles</p>
                        </div>
                        <div class="icon" style="top: 10px;">
                            <i class="fas fa-users"></i>
                        </div>
                        <a href="/admin/faculty/faculty/" class="small-box-footer" style="padding: 0.5rem;">More info <i class="fas fa-arrow-circle-right"></i></a>
                    </div>
                </div>

                <!-- Research Output -->
                <div class="col-lg-3 col-6">
                    <div class="small-box bg-warning" style="border-radius: 0.5rem; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div class="inner" style="padding: 1.5rem;">
                            <h3>${data.research.total_output} <sup style="font-size: 20px">Outputs</sup></h3>
                            <p>Publications & Projects</p>
                        </div>
                        <div class="icon" style="top: 10px;">
                            <i class="fas fa-flask"></i>
                        </div>
                        <a href="/admin/research/publication/" class="small-box-footer" style="padding: 0.5rem; color: #fff !important;">More info <i class="fas fa-arrow-circle-right"></i></a>
                    </div>
                </div>

                <!-- Admissions -->
                <div class="col-lg-3 col-6">
                    <div class="small-box bg-danger" style="border-radius: 0.5rem; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div class="inner" style="padding: 1.5rem;">
                            <h3>${data.admission.merit_lists} <sup style="font-size: 20px">Lists</sup></h3>
                            <p>${data.admission.active_session}</p>
                        </div>
                        <div class="icon" style="top: 10px;">
                            <i class="fas fa-graduation-cap"></i>
                        </div>
                        <a href="/admin/admission/admissionmeritlist/" class="small-box-footer" style="padding: 0.5rem;">More info <i class="fas fa-arrow-circle-right"></i></a>
                    </div>
                </div>
            `;
        })
        .catch(err => {
            console.error("Dashboard Stats Error:", err);
        });
}

// Ensure the dashboard renders on load
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderGlobalDashboard);
} else {
    renderGlobalDashboard();
}

/**
 * Auto-detect and set Import format based on file extension
 */
function setupImportFormatDetection() {
    var fileInput = document.getElementById('id_import_file');
    var formatSelect = document.getElementById('id_input_format');
    
    if (fileInput && formatSelect) {
        // Hide the format select field's container row so user doesn't see it
        var formatRow = formatSelect.closest('.form-row') || formatSelect.parentElement;
        if (formatRow) {
            formatRow.style.display = 'none';
        }
        
        // Auto-select format based on file extension when user picks a file
        fileInput.addEventListener('change', function(e) {
            var fileName = e.target.value;
            if (!fileName) return;
            var ext = fileName.split('.').pop().toLowerCase();
            
            // Map extension to the format select option text
            for (var i = 0; i < formatSelect.options.length; i++) {
                var optionText = formatSelect.options[i].text.toLowerCase().trim();
                // Strict match to prevent 'xls' matching 'xlsx'
                if (optionText === ext || optionText.startsWith(ext + " ") || optionText === ext.toUpperCase()) {
                    formatSelect.selectedIndex = i;
                    break;
                }
            }
        });
        
        // Trigger change if file already selected (e.g. on form reload with errors)
        if (fileInput.value) {
            fileInput.dispatchEvent(new Event('change'));
        }
    }
}

// Execute on load
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupImportFormatDetection);
} else {
    setupImportFormatDetection();
}
