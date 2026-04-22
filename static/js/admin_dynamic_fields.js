document.addEventListener('DOMContentLoaded', function () {
    console.log("Admin Dynamic Fields Tracker Initialized v4");

    function toggleDisable(dropdown, otherInput) {
        if (!dropdown || !otherInput) return;
        if (dropdown.value === 'Others') {
            otherInput.readOnly = false;
            otherInput.disabled = false;
            otherInput.style.backgroundColor = '';
            otherInput.style.opacity = '1';
            otherInput.style.pointerEvents = 'auto';
        } else {
            otherInput.readOnly = true;
            otherInput.value = '';
            // Using disabled natively prevents any interactions/clicks
            otherInput.disabled = true;
            otherInput.style.backgroundColor = '#eee';
            otherInput.style.opacity = '0.5';
            otherInput.style.pointerEvents = 'none';
        }
    }

    // 1. Static Field (Program Level)
    const levelSelect = document.getElementById('id_level');
    const otherLevelInput = document.getElementById('id_other_level');
    if (levelSelect && otherLevelInput) {
        toggleDisable(levelSelect, otherLevelInput);
        levelSelect.addEventListener('change', function () {
            toggleDisable(this, otherLevelInput);
        });
    }

    // 2. Static Field (Notice Category)
    const categorySelect = document.getElementById('id_category');
    const otherCategoryInput = document.getElementById('id_other_category');
    if (categorySelect && otherCategoryInput) {
        toggleDisable(categorySelect, otherCategoryInput);
        categorySelect.addEventListener('change', function () {
            toggleDisable(this, otherCategoryInput);
        });
    }

    // 3. Static Field (Centre Head Title)
    const headTitleSelect = document.getElementById('id_head_title');
    const headTitleOtherInput = document.getElementById('id_head_title_other');
    if (headTitleSelect && headTitleOtherInput) {
        toggleDisable(headTitleSelect, headTitleOtherInput);
        headTitleSelect.addEventListener('change', function () {
            toggleDisable(this, headTitleOtherInput);
        });
    }

    // Event Delegation for dynamically changing selects
    document.body.addEventListener('change', function(event) {
        const target = event.target;
        if (target && target.tagName === 'SELECT') {
            if (target.id.endsWith('-course_type')) {
                const otherInput = document.getElementById(target.id.replace('-course_type', '-other_course_type'));
                toggleDisable(target, otherInput);
            }
            if (target.id.endsWith('-designation_in_committee')) {
                const otherInput = document.getElementById(target.id.replace('-designation_in_committee', '-other_designation'));
                toggleDisable(target, otherInput);
            }
        }
    });

    // Initialize all existing inlines on page load
    const allSelects = document.querySelectorAll('select');
    allSelects.forEach(function(select) {
        if (select.id.includes('__prefix__')) return; // ignore django empty form templates
        
        if (select.id.endsWith('-course_type')) {
            const otherInput = document.getElementById(select.id.replace('-course_type', '-other_course_type'));
            toggleDisable(select, otherInput);
        }
        if (select.id.endsWith('-designation_in_committee')) {
            const otherInput = document.getElementById(select.id.replace('-designation_in_committee', '-other_designation'));
            toggleDisable(select, otherInput);
        }
    });
    
    // Observer to initialize newly added inlines dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // ELEMENT_NODE
                    const selects = node.querySelectorAll ? node.querySelectorAll('select') : [];
                    selects.forEach(function(select) {
                        if (select.id.includes('__prefix__')) return;
                        if (select.id.endsWith('-course_type')) {
                            const otherInput = document.getElementById(select.id.replace('-course_type', '-other_course_type'));
                            toggleDisable(select, otherInput);
                        }
                        if (select.id.endsWith('-designation_in_committee')) {
                            const otherInput = document.getElementById(select.id.replace('-designation_in_committee', '-other_designation'));
                            toggleDisable(select, otherInput);
                        }
                    });
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
