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
