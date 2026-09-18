/**
 * notice_appointment_toggle.js
 *
 * Dynamically shows or hides the "Appointment Choice" (appointment_type) field
 * in the Global Notice Django admin form based on whether "Appointment"
 * is selected in the "Categories" field.
 */
document.addEventListener("DOMContentLoaded", function () {
    const categoriesSelect = document.getElementById("id_categories");
    const appointmentField = document.getElementById("id_appointment_type");

    if (!categoriesSelect || !appointmentField) return;

    // Find row/wrapper (works with Jazzmin / standard Django admin)
    const wrapper = appointmentField.closest(".form-group.field-appointment_type") ||
                    appointmentField.closest(".form-group") ||
                    appointmentField.closest(".fieldBox") ||
                    appointmentField.closest(".form-row");

    function isAppointmentSelected() {
        if (!categoriesSelect) return false;
        // Works for multi-select (<select multiple>) or single select
        if (categoriesSelect.selectedOptions && categoriesSelect.selectedOptions.length > 0) {
            return Array.from(categoriesSelect.selectedOptions).some(
                opt => opt.value === "Appointment"
            );
        }
        // Fallback if selectedOptions is not supported
        for (let i = 0; i < categoriesSelect.options.length; i++) {
            if (categoriesSelect.options[i].selected && categoriesSelect.options[i].value === "Appointment") {
                return true;
            }
        }
        return false;
    }

    function toggleAppointmentField() {
        const show = isAppointmentSelected();
        if (wrapper) {
            wrapper.style.display = show ? "" : "none";
        } else {
            appointmentField.style.display = show ? "" : "none";
        }
        if (!show) {
            // Reset appointment selection when Appointment is deselected
            appointmentField.value = "";
            if (typeof window.jQuery !== "undefined") {
                window.jQuery(appointmentField).trigger("change");
            }
        }
    }

    // Initial check on page load
    toggleAppointmentField();

    // Native change listener
    categoriesSelect.addEventListener("change", toggleAppointmentField);

    // Fallback listeners for jQuery / Select2 in Jazzmin / Django admin
    if (typeof window.jQuery !== "undefined") {
        window.jQuery(categoriesSelect).on("change select2:select select2:unselect", toggleAppointmentField);
    } else if (typeof django !== "undefined" && django.jQuery) {
        django.jQuery(categoriesSelect).on("change select2:select select2:unselect", toggleAppointmentField);
    }
});
