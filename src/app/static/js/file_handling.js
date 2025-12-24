$(document).ready(function() {
    document.getElementById('import_file_input').addEventListener('change', function (event) {
        var file = event.target.files[0]
        if (!file) {return}

        var reader = new FileReader()

        reader.onload = function(e) {
            try {
                var import_patient_data = JSON.parse(e.target.result)
            }
            catch (error) {
                console.log(error)
            }
            console.log('Data loaded')
            console.log(import_patient_data)
            add_new_patient(import_patient_data)
        }
        console.log('read file')
        reader.readAsText(file)
        document.getElementById('import_file_input').value = ''
    })

});


function add_new_patient (import_patient_data = false) {
    document.getElementById('criteria_list_container').replaceChildren()
    document.getElementById('input_case_selection').replaceChildren()
    document.getElementById('search_input').replaceChildren()
    document.getElementById('patient_id_input').value = ''
    document.getElementById('patient_surname_input').value = ''
    document.getElementById('patient_name_input').value = ''
    document.getElementById('patient_bday_input').value = ''
    document.getElementById('patient_gender_input').value = 'Bitte auswählen'
    document.getElementById('patient_name').textContent = 'N/A, N/A'
    document.getElementById('patient_id').textContent = 'N/A'
    document.getElementById('patient_bday').textContent = 'N/A'
    old_evidence = null
    interaction = new Interaction('ADNI', import_patient_data)
    document.getElementById('settings_modal').close()
}


function export_patient() {
    console.log('export started')
    let patient_id = document.getElementById('patient_id').textContent
    let patient_name = document.getElementById('patient_name').textContent
    let file_name = 'patient'
    if (patient_id != 'N/A') {
        file_name = patient_id
    } else if (patient_name != 'N/A') {
        file_name = file_name + '_' + patient_name
    }

    saveFile(file_name, get_data())    
}

function import_patient() {
    console.log('import started')

    document.getElementById('import_file_input').click()
}


function saveFile(filename, content) {
    const blob = new Blob([JSON.stringify(content, null, 2)], {type: "application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function get_data() {
    return {
        'patient_id': document.getElementById('patient_id_input').value,
        'patient_surname': document.getElementById('patient_surname_input').value,
        'patient_name': document.getElementById('patient_name_input').value,
        'patient_bday': document.getElementById('patient_bday_input').value,
        'patient_gender': document.getElementById('patient_gender_input').value,
        'interaction_data': {
            'selected_model': interaction.selected_model,
            'case_counter': interaction.case_counter,
            'case_list': interaction.case_list, 
        },
        'cases_data': get_case_data()
    }
}

function get_case_data() {
    var cases = []
    document.querySelectorAll('.criteria-list').forEach(element => {
        var criteria_list = {}
        element.querySelectorAll('.criteria-item:not(.empty)').forEach(elem => {
            criteria_list[elem.id] = elem.querySelector('input, select').value
        });
        cases.push(criteria_list)
    });
    console.log(cases)
    return cases
}


var typing_timer;
var empty_criteria_timer;
var old_criteria_item


function get_current_criteria_node(input_element){
    old_criteria_item = interaction.get_criteria_input_data(input_element)
}


function changing_input(element) {

    clearTimeout(typing_timer)
    clearTimeout(empty_criteria_timer)

    function push_to_undo_history (element) {
        current_criteria_item = interaction.get_criteria_input_data(element)
            if (old_criteria_item != current_criteria_item) {
                interaction.UR_handler.push_criteria_to_undo_history(old_criteria_item, false)
                old_criteria_item = current_criteria_item
            }
    }

    if (element.tagName == 'INPUT') {
        typing_timer = setTimeout(() => {
            push_to_undo_history(element)
        }, 500)
    } else {
        push_to_undo_history(element)
    }
    
    
    if (element.parentElement.classList.contains('empty')) { return }
    if (element.tagName == 'INPUT') {
        if (element.value != '') { return }
        empty_criteria_timer = setTimeout(() => {
            element.parentElement.classList.add('empty')
        }, 500)
        return
    }
    if (element.tagName == 'SELECT') {
        if (element.value != 'Bitte auswählen') { return }
        element.parentElement.classList.add('empty')
        return
    }
}