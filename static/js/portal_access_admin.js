(function ($) {
    'use strict';

    $(document).ready(function () {

        // Roles that do not require Entity Type or Dynamic Entity
        const rolesWithoutEntity = [
            'FACULTY',
            'RD_ADMIN',
            'COE',
            'REGISTRAR',
            'FINANCE_SECTION',
            'ACADEMIC_SECTION'
        ];

        // Function to handle entity type change
        function handleEntityTypeChange() {
            console.log(
                "Entity type changed detected:",
                $(this).attr('id'),
                "Value:",
                $(this).val()
            );

            var $entityTypeSelect = $(this);
            var selectedType = $entityTypeSelect.val();
            var $dynamicEntitySelect;

            // Determine if we are in an inline or standalone form
            if ($entityTypeSelect.attr('id') === 'id_entity_type') {
                $dynamicEntitySelect = $('#id_dynamic_entity');
            } else {
                var $row = $entityTypeSelect.closest(
                    '.form-row, tr, fieldset'
                );

                $dynamicEntitySelect = $row.find(
                    'select[id*="dynamic_entity"]'
                );
            }

            if (!$dynamicEntitySelect.length) {
                return;
            }

            // Clear current options
            $dynamicEntitySelect
                .empty()
                .append('<option value="">---------</option>');

            // If no entity type is selected
            if (!selectedType) {
                $dynamicEntitySelect.trigger('change');
                return;
            }

            // Fetch entities via AJAX
            console.log(
                "Fetching entities for type:",
                selectedType
            );

            $.ajax({
                url: '/portal/api/get-entities/',
                data: {
                    'type': selectedType
                },
                dataType: 'json',

                success: function (data) {

                    console.log(
                        "Entities received:",
                        data.entities
                            ? data.entities.length
                            : 0
                    );

                    if (
                        data.entities &&
                        data.entities.length > 0
                    ) {
                        $.each(
                            data.entities,
                            function (index, entity) {

                                $dynamicEntitySelect.append(
                                    $('<option></option>')
                                        .val(entity.id)
                                        .html(entity.name)
                                );

                            }
                        );
                    }

                    // Update Select2 if active
                    $dynamicEntitySelect.trigger('change');
                },

                error: function (xhr, status, error) {

                    console.error(
                        'Error fetching entities:',
                        error
                    );

                }
            });
        }


        // Function to handle role change
        function handleRoleChange() {

            var $roleSelect = $(this);
            var selectedRole = $roleSelect.val();

            var $entityTypeSelect;
            var $dynamicEntitySelect;


            // Standalone form
            if ($roleSelect.attr('id') === 'id_role') {

                $entityTypeSelect = $('#id_entity_type');
                $dynamicEntitySelect = $('#id_dynamic_entity');

            }

            // Inline form
            else {

                var $row = $roleSelect.closest(
                    '.form-row, tr, fieldset'
                );

                $entityTypeSelect = $row.find(
                    'select[id*="entity_type"]'
                );

                $dynamicEntitySelect = $row.find(
                    'select[id*="dynamic_entity"]'
                );
            }


            // Make sure both fields exist
            if (
                $entityTypeSelect.length &&
                $dynamicEntitySelect.length
            ) {

                var $typeContainer =
                    $entityTypeSelect.closest(
                        '.form-row, .fieldBox, .form-group'
                    );

                var $dynamicContainer =
                    $dynamicEntitySelect.closest(
                        '.form-row, .fieldBox, .form-group'
                    );


                // Hide Entity Type and Dynamic Entity
                // for specific roles
                if (
                    rolesWithoutEntity.includes(
                        selectedRole
                    )
                ) {

                    $typeContainer.hide();
                    $dynamicContainer.hide();


                    // Clear Entity Type
                    $entityTypeSelect
                        .val('')
                        .trigger('change');


                    // Clear Dynamic Entity
                    $dynamicEntitySelect
                        .val('')
                        .trigger('change');

                }

                // Show fields for all other roles
                else {

                    $typeContainer.show();
                    $dynamicContainer.show();

                }
            }
        }


        // Handle Entity Type changes
        // Works for normal forms and dynamically
        // added Django inline rows
        $(document).on(
            'change select2:select',
            'select[id*="entity_type"]',
            handleEntityTypeChange
        );


        // Handle Role changes
        $(document).on(
            'change select2:select',
            'select[id*="role"]',
            handleRoleChange
        );


        // Run role handler when page loads
        // This handles existing records
        $('select[id*="role"]').each(
            handleRoleChange
        );


        // Load entities for existing Entity Type values
        $('select[id*="entity_type"]').each(
            function () {

                // Only process if Entity Type
                // already has a value
                if ($(this).val()) {

                    var $select = $(this);
                    var $dynamic;


                    // Standalone form
                    if (
                        $select.attr('id') ===
                        'id_entity_type'
                    ) {

                        $dynamic =
                            $('#id_dynamic_entity');

                    }

                    // Inline form
                    else {

                        $dynamic =
                            $select
                                .closest(
                                    '.form-row, tr, fieldset'
                                )
                                .find(
                                    'select[id*="dynamic_entity"]'
                                );
                    }


                    // Fetch entities only if
                    // Dynamic Entity is empty
                    if (
                        $dynamic.length &&
                        $dynamic.children(
                            'option'
                        ).length <= 1
                    ) {

                        handleEntityTypeChange.call(
                            this
                        );

                    }
                }
            }
        );

    });

})(window.jQuery || window.$ || django.jQuery);