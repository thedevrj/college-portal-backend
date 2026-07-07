/**
 * claim_checkbox_toggle.js
 *
 * Hides the "Confirm Co-Authorship / Co-Inventor Claim" checkbox by default.
 * It is only revealed (with a highlighted warning banner) when the server returns
 * a validation error on that field — meaning a duplicate title/DOI was detected.
 *
 * This prevents the checkbox from confusing users on a fresh "Add" form.
 */
(function () {
  "use strict";

  function initClaimCheckbox() {
    document.querySelectorAll(".claim-confirm-checkbox").forEach(function (checkbox) {
      var row = checkbox.closest(".form-row") || checkbox.closest("p") || checkbox.parentElement;
      if (!row) return;

      // Check if Django rendered an error on this field (i.e. duplicate was detected)
      var hasError =
        row.querySelector(".errorlist") !== null ||
        row.classList.contains("errors");

      if (hasError) {
        // Duplicate detected — make the row very visible with a warning style
        row.style.display = "";
        row.style.padding = "12px";
        row.style.background = "#fff3cd";
        row.style.border = "2px solid #ffc107";
        row.style.borderRadius = "4px";
        row.style.marginTop = "10px";
      } else {
        // No duplicate — hide the row entirely
        row.style.display = "none";
      }
    });
  }

  // Run after DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initClaimCheckbox);
  } else {
    initClaimCheckbox();
  }
})();
