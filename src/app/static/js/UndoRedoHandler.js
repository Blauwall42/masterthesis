class UndoRedoHandler {
    constructor() {
        this.max_history_length = 1000
        this.undo_history = []
        this.redo_history = []
        this.undo_btn = document.getElementById('undo_btn')
        this.redo_btn = document.getElementById('redo_btn')

        this.undo_btn.disabled = true
        this.redo_btn.disabled = true
    }

    undo() {
        if (this.undo_history.length < 1) {
            this.undo_btn.disabled = true
            return
        }

        var step = this.undo_history.pop()
        if (step['type'] == 'criteria') { this.undo_redo_criteria_change(step['change'], true)}
        if (step['type'] == 'add case') { this.undo_redo_add_case(step['change'], true)}
        if (step['type'] == 'remove case') { this.undo_redo_remove_case(step['change'], true)}

        if (this.undo_history.length < 1) {
            this.undo_btn.disabled = true
        }
    }

    redo() {
        if (this.redo_history.length < 1) {
            this.redo_btn.disabled = true
            return
        }
        var step = this.redo_history.pop()
        if (step['type'] == 'criteria') { this.undo_redo_criteria_change(step['change'], false)}
        if (step['type'] == 'add case') { this.undo_redo_add_case(step['change'], false)}
        if (step['type'] == 'remove case') { this.undo_redo_remove_case(step['change'], false)}

        if (this.redo_history.length < 1) {
            this.redo_btn.disabled = true
        }
    }

    undo_redo_criteria_change(change, is_undo) {
        var criteria_input = document.getElementById(change['criteria-input'])
        let is_element = true
        let reset_redo_history = false
        if (is_undo) {
            this.push_criteria_to_redo_history(criteria_input, is_element, reset_redo_history)
        } else {
            this.push_criteria_to_undo_history(criteria_input, is_element, reset_redo_history)
        }
        criteria_input.value = change['value']
        if (change['empty']) {
            criteria_input.parentElement.classList.add('empty')
        } else {
            criteria_input.parentElement.classList.remove('empty')
        }
    }

    undo_redo_add_case(change, is_undo) {
        var case_id = change['case_id']
        interaction.remove_case(case_id, !is_undo, false)
    }

    undo_redo_remove_case(change, is_undo) {
        var case_id = change['case_id']
        interaction.add_case(case_id, !is_undo, false,
            change['criteria-items'], change['case_counter']
        )
    }



    push_to_undo_history (change_data, reset_redo_history = true) {
        this.push_to_history(change_data, true, reset_redo_history)
    }

    push_to_redo_history (change_data, reset_redo_history = true) {
        this.push_to_history(change_data, false, reset_redo_history)
    }


    push_criteria_to_undo_history(criteria_input, is_element, reset_redo_history = true) {
        this.push_criteria_to_history(criteria_input, true, is_element, reset_redo_history)
    }

    push_criteria_to_redo_history(criteria_input, is_element, reset_redo_history = true) {
        this.push_criteria_to_history(criteria_input, false, is_element, reset_redo_history)
    }

    push_criteria_to_history(criteria_input, for_undo_history, is_element, reset_redo_history) {
        var input_data = criteria_input
        if (is_element) {
            input_data = this.get_criteria_input_data(criteria_input)
        }
        var change_data = this.get_criteria_change(input_data)
        this.push_to_history(change_data,for_undo_history, reset_redo_history)       
    }

    get_criteria_input_data(element) {
        return {
            'empty': element.parentElement.classList.contains('empty'),
            'criteria-input': element.id,
            'value': element.value
        }
    }

    get_criteria_change(criteria_input_data) {
        return {
            'type': 'criteria',
            'change': criteria_input_data
        }
    }




    push_to_history(change, for_undo_history, reset_redo_history) {
        if (for_undo_history) {
            this.undo_btn.disabled = false
            this.undo_history.push(change)
        } else {
            this.redo_btn.disabled = false
            this.redo_history.push(change)
        }

        if (reset_redo_history) {
            this.clear_redo_history()
        }
    }

    clear_redo_history() {
        this.redo_history = []
        this.redo_btn.disabled = true
    }
}

        
