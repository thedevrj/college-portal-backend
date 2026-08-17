document.addEventListener('DOMContentLoaded', function () {
    function toggleDisable(dropdown, otherInput) {
        if (!dropdown || !otherInput) return;

        let rawFieldName = otherInput.id.replace('id_', '');
        let baseFieldName = rawFieldName;
        const lastDashIndex = rawFieldName.lastIndexOf('-');
        if (lastDashIndex !== -1) {
            baseFieldName = rawFieldName.substring(lastDashIndex + 1);
        }

        // Target Jazzmin's .form-group, standard Django's .fieldBox, or the specific field wrapper
        const wrapper = otherInput.closest('.form-group.field-' + rawFieldName) ||
            otherInput.closest('.form-group.field-' + baseFieldName) ||
            otherInput.closest('.field-' + baseFieldName) ||
            otherInput.closest('.form-group') ||
            otherInput.closest('.fieldBox') ||
            otherInput.closest('.form-row');

        if (dropdown.value === 'Others' || dropdown.value === 'Other') {
            otherInput.readOnly = false;
            otherInput.disabled = false;
            otherInput.style.backgroundColor = '';
            otherInput.style.opacity = '1';
            otherInput.style.pointerEvents = 'auto';

            if (wrapper && wrapper.tagName !== 'TR' && wrapper.tagName !== 'TD') {
                // Restore original CSS display (flex/block) instead of hardcoding 'block'
                wrapper.style.display = '';
            } else if (!wrapper || (wrapper.tagName !== 'TR' && wrapper.tagName !== 'TD')) {
                otherInput.style.display = '';
            }
        } else {
            otherInput.readOnly = true;
            otherInput.value = '';
            otherInput.disabled = true;
            otherInput.style.backgroundColor = '#eee';
            otherInput.style.opacity = '0.5';
            otherInput.style.pointerEvents = 'none';

            if (wrapper && wrapper.tagName !== 'TR' && wrapper.tagName !== 'TD') {
                wrapper.style.display = 'none';
            } else if (!wrapper || (wrapper.tagName !== 'TR' && wrapper.tagName !== 'TD')) {
                otherInput.style.display = 'none';
            }
        }
    }

    function getOtherInput(selectId) {
        if (!selectId) return null;
        let prefix = "id_";
        let fieldName = selectId.substring(3);

        const lastDash = fieldName.lastIndexOf('-');
        if (lastDash !== -1) {
            prefix = "id_" + fieldName.substring(0, lastDash + 1);
            fieldName = fieldName.substring(lastDash + 1);
        }

        const candidates = [
            prefix + "other_" + fieldName,
            prefix + "others_" + fieldName,
            prefix + fieldName + "_other",
            prefix + "other_" + fieldName + "_name",
            prefix + "other_designation",
            prefix + "other_" + fieldName.toLowerCase(),
            prefix + "others_" + fieldName.toLowerCase()
        ];

        for (let i = 0; i < candidates.length; i++) {
            const el = document.getElementById(candidates[i]);
            if (el) return el;
        }
        return null;
    }

    function initializeSelect(select) {
        if (!select || !select.id || select.id.includes('__prefix__')) return;
        const otherInput = getOtherInput(select.id);
        if (otherInput) {
            toggleDisable(select, otherInput);

            if (!select.dataset.dynamicBound) {
                select.addEventListener('change', function () {
                    toggleDisable(this, otherInput);
                });
                select.dataset.dynamicBound = 'true';

                // Fallback for Select2 or other libraries that might not trigger native change
                if (typeof window.jQuery !== 'undefined') {
                    window.jQuery(select).on('change', function () {
                        toggleDisable(select, otherInput);
                    });
                } else if (typeof django !== 'undefined' && django.jQuery) {
                    django.jQuery(select).on('change', function () {
                        toggleDisable(select, otherInput);
                    });
                }
            }
        }
    }

    // Initialize all selects on page load
    document.querySelectorAll('select').forEach(initializeSelect);

    // Observer to initialize newly added inlines dynamically
    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1) { // ELEMENT_NODE
                    if (node.tagName === 'SELECT') {
                        initializeSelect(node);
                    }
                    const selects = node.querySelectorAll ? node.querySelectorAll('select') : [];
                    selects.forEach(initializeSelect);
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
