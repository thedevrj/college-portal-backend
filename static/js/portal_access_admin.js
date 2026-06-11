(function ($) {
    'use strict';

    $(document).ready(function () {
        // Function to handle entity type change
        function handleEntityTypeChange() {
            console.log("Entity type changed detected:", $(this).attr('id'), "Value:", $(this).val());
            var $entityTypeSelect = $(this);
            var selectedType = $entityTypeSelect.val();
            var $dynamicEntitySelect;

            // Determine if we are in an inline or standalone form
            if ($entityTypeSelect.attr('id') === 'id_entity_type') {
                $dynamicEntitySelect = $('#id_dynamic_entity');
            } else {
                var $row = $entityTypeSelect.closest('.form-row, tr, fieldset');
                $dynamicEntitySelect = $row.find('select[id*="dynamic_entity"]');
            }

            if (!$dynamicEntitySelect.length) return;

            // Clear current options
            $dynamicEntitySelect.empty().append('<option value="">---------</option>');

            if (!selectedType) {
                $dynamicEntitySelect.trigger('change');
                return;
            }

            // Fetch new options via AJAX
            console.log("Fetching entities for type:", selectedType);
            $.ajax({
                url: '/portal/api/get-entities/',
                data: { 'type': selectedType },
                dataType: 'json',
                success: function (data) {
                    console.log("Entities received:", data.entities ? data.entities.length : 0);
                    if (data.entities && data.entities.length > 0) {
                        $.each(data.entities, function (index, entity) {
                            $dynamicEntitySelect.append(
                                $('<option></option>').val(entity.id).html(entity.name)
                            );
                        });
                    }
                    // Trigger change so Select2 (if active) updates its display
                    $dynamicEntitySelect.trigger('change');
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching entities:', error);
                }
            });
        }

        // Function to handle role change
        function handleRoleChange() {
            var $roleSelect = $(this);
            var selectedRole = $roleSelect.val();
            var $entityTypeSelect, $dynamicEntitySelect;

            if ($roleSelect.attr('id') === 'id_role') {
                $entityTypeSelect = $('#id_entity_type');
                $dynamicEntitySelect = $('#id_dynamic_entity');
            } else {
                var $row = $roleSelect.closest('.form-row, tr, fieldset');
                $entityTypeSelect = $row.find('select[id*="entity_type"]');
                $dynamicEntitySelect = $row.find('select[id*="dynamic_entity"]');
            }

            if ($entityTypeSelect.length && $dynamicEntitySelect.length) {
                var $typeContainer = $entityTypeSelect.closest('.form-row, .fieldBox, .form-group');
                var $dynamicContainer = $dynamicEntitySelect.closest('.form-row, .fieldBox, .form-group');

                if (selectedRole === 'FACULTY' || selectedRole === 'RD_ADMIN') {
                    $typeContainer.hide();
                    $dynamicContainer.hide();
                    // Clear values when hidden
                    $entityTypeSelect.val('').trigger('change.select2');
                } else {
                    $typeContainer.show();
                    $dynamicContainer.show();
                }
            }
        }

        // Use event delegation so it works for dynamically added inline rows too
        $(document).on('change select2:select', 'select[id*="entity_type"]', handleEntityTypeChange);
        $(document).on('change select2:select', 'select[id*="role"]', handleRoleChange);

        // Run on page load for existing values
        $('select[id*="role"]').each(handleRoleChange);

        // For entity type, only trigger if the select entity dropdown is empty
        $('select[id*="entity_type"]').each(function () {
            if ($(this).val()) {
                var $select = $(this);
                var $dynamic;
                if ($select.attr('id') === 'id_entity_type') {
                    $dynamic = $('#id_dynamic_entity');
                } else {
                    $dynamic = $select.closest('.form-row, tr, fieldset').find('select[id*="dynamic_entity"]');
                }

                if ($dynamic.length && $dynamic.children('option').length <= 1) {
                    handleEntityTypeChange.call(this);
                }
            }
        });
    });
})(window.jQuery || window.$ || django.jQuery);
