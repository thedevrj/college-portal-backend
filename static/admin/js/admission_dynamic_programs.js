document.addEventListener("DOMContentLoaded", function () {
    console.log("Admission Dynamic Programs JS initialized.");

    var deptSelect = document.getElementById('id_departments');
    var progSelect = document.getElementById('id_programs');

    if (!deptSelect || !progSelect) {
        console.log("Could not find #id_departments or #id_programs. Exiting.");
        return;
    }

    var allPrograms = [];

    fetch('/api/v1/programs/?limit=1000')
        .then(response => response.json())
        .then(data => {
            console.log("Successfully fetched programs:", data);
            allPrograms = data.results || data;
            updatePrograms(false);
        })
        .catch(err => {
            console.error("Failed to fetch programs for dynamic dropdown.", err);
        });

    function updatePrograms(clearSelection) {
        if (allPrograms.length === 0) return;

        // Get selected departments
        var selectedDepts = Array.from(deptSelect.selectedOptions).map(opt => opt.value);
        console.log("Selected departments:", selectedDepts);

        var validPrograms = allPrograms;
        if (selectedDepts.length > 0) {
            validPrograms = allPrograms.filter(function (p) {
                return p.department && selectedDepts.includes(String(p.department));
            });
        } else {
            validPrograms = [];
        }

        console.log("Valid programs count:", validPrograms.length);

        // Get currently selected programs
        var chosenPrograms = Array.from(progSelect.selectedOptions).map(opt => opt.value);
        if (clearSelection) {
            chosenPrograms = [];
        }

        // Rebuild programs dropdown
        progSelect.innerHTML = ''; // clear options
        validPrograms.forEach(function (p) {
            var isSelected = chosenPrograms.includes(String(p.id));
            var option = new Option(p.name, p.id, false, isSelected);
            progSelect.appendChild(option);
        });

        // Trigger change for Select2 if it's used
        progSelect.dispatchEvent(new Event('change', { bubbles: true }));

        // If jQuery is available, trigger change through it just in case Select2 misses the native event
        if (typeof window.jQuery !== 'undefined') {
            window.jQuery(progSelect).trigger('change');
        } else if (typeof django !== 'undefined' && django.jQuery) {
            django.jQuery(progSelect).trigger('change');
        }
    }

    // Listen for changes
    deptSelect.addEventListener('change', function () {
        console.log("Department selection changed.");
        updatePrograms(false);
    });

    // Select2 sometimes doesn't fire native change events on the original select when clicking the 'x'
    // So we bind to jQuery change event as a fallback if available
    if (typeof window.jQuery !== 'undefined') {
        window.jQuery(deptSelect).on('change', function () {
            console.log("Department selection changed (jQuery).");
            updatePrograms(false);
        });
    } else if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(deptSelect).on('change', function () {
            console.log("Department selection changed (django.jQuery).");
            updatePrograms(false);
        });
    }

});
