/**
 * Search function for criteria search which hides unmatched results.
 */
$(document).ready(function() {
    $('#search_input').on('input', function() {
        console.log($(this))
        document.querySelectorAll('.criteria-group').forEach( element => {
            element.open = true
        })
        const filter = $(this).val().toLowerCase();
        $('.criteria-item').each(function() {
            const item = $(this);
            const input_elem = item.find('.criteria-input')
            const textValue = input_elem.attr('data-node').toLowerCase();
            
            if (textValue.includes(filter)) {
                console.log(textValue)
                item.removeClass('hidden');
            } else {
                item.addClass('hidden');
            }
        });
    });

    /**
     * Select what-if-case and shows associated criteria lists
     */
    $('#input_case_selection').on('input', function() {
        const case_id = this.value;
        interaction.show_selected_case(case_id)
        interaction.delete_highlight()
    });

    document.querySelectorAll('#net_container, #prediction_view').forEach(element => {
            element.addEventListener('click', function (event) {
                let target = event.target
                if (target.tagName == 'BUTTON' || target.tagName == 'path' || target.closest('#node_details')) { return }
                console.log(target)
                interaction.inference()
                interaction.delete_highlight()
                // console.log(interaction.donut_graphs)
                // console.log(target.tagName)
                // interaction.donut_graphs.forEach(graph => {
                //     if (graph['model_key'] != interaction.selected_model) { return }
                //     console.log(graph['graph'].title)
                //     graph['graph'].delete_selection()
                //     graph['graph'].update_selection()
                // })
            })
        }
    )
});




/**
 * Adds criteria to selected criteria list.
 *
 * @param {string} case_id - ID of what-if-case
 * @param {string} id - ID of criteria
 */
function add_criteria(btn_element) {
    var criteria = btn_element.parentElement 
    criteria_input = criteria.querySelector('.criteria-input')
    let criteria_item_data = interaction.get_criteria_input_data(criteria_input)

    if (criteria_input.value == '' || criteria_input.value == 'Bitte auswählen') {
        return
    }
    criteria.classList.remove('empty')
    interaction.UR_handler.push_criteria_to_undo_history(criteria_item_data, false)
    // interaction.add_criteria_input_to_undo(criteria_item_data)
}


/**
 * Removes criteria from selected criteria list
 *
 * @param {string} case_id - ID of what-if-case
 * @param {string} id - ID of criteria
 */
function remove_criteria(btn_element) {
    let criteria = btn_element.parentElement
    let criteria_input = criteria.querySelector('.criteria-input')

    let criteria_item_data = interaction.get_criteria_input_data(criteria_input)


    criteria.classList.add('empty');
    if (criteria_input.tagName.toLowerCase() === 'select') {
        criteria_input.value = 'Bitte auswählen';
    } else {
        criteria_input.value = '';
    }
    interaction.UR_handler.push_criteria_to_undo_history(criteria_item_data, false)
}


function get_age_from_date(birthday) {
    birthday = new Date(birthday)
    let today = new Date()
    return Math.round((today - birthday)/1000/60/60/24/365*100)/100
}


function add_gender_to_criteria() {
    let gender = document.getElementById('patient_gender').value
    if (gender == 'Geschlecht') {
        return
    }
    const case_id = document.getElementById('input_case_selection').value;
    let criteria_id = 'Allgemein_Geschlecht'
    document.getElementById(case_id + '_input_' + criteria_id).value = gender
    add_criteria(case_id, criteria_id)
}