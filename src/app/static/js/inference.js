
/**
 * Gathers all selected criteria as evidence (ordered by what-if-case) and sends them
 * as ajax request to the server. After receiving a successful response, it initiates
 * the rendering of the graphs.
 */
function inference(case_list, replace_evidence=false, model=false) {
    let infer_btn = document.getElementById('infer_btn')
    infer_btn.ariaBusy = true
    infer_btn.disabled = true

    var evidence = get_evidence(case_list, replace_evidence)
    console.log(evidence)

    var url = '/ajax'

    if (model) {
        url += '/' + model
    } else {replace_evidence = false}
    var data = {'evidence': evidence, 'replace_evidence': replace_evidence}

    console.log(model)
    console.log(url)
    $.ajax({
        url: url,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(result){
            console.log('Results')
            console.log(result)
            if (result['information_gain'] && Object.keys(result['information_gain']).length > 0){
                interaction.ig_data = result['information_gain']
                update_network_ig()
            }
            interaction.render_graphs(result['results'])
        },
        error: function(xhr, status, error) {
            console.error("AJAX Error:", status, error);
            console.log("Response Text:", xhr.responseText);
            console.log("Status Code:", xhr.status);
        },
        complete: function () {
            infer_btn.ariaBusy = false
            infer_btn.disabled = false
        }
    });
}

function get_evidence(case_list, replace_evidence = false) {

    var selected_criteria = document.querySelectorAll('.criteria-item:not(.empty)');
    var data = {}

    for (const case_id of case_list) {
        data['case' + case_id] = {};
    }

    selected_criteria.forEach(element => {
        let input_elem = element.querySelector('.criteria-input')
        let case_id = input_elem.dataset.case
        let feature = input_elem.dataset.node
        data['case' + case_id][feature] = input_elem.value
        
    })


    console.log(data)
    let cases_to_ignore = []
    Object.keys(data).forEach(key => {
        if (old_evidence != null && JSON.stringify(data[key]) == old_evidence[key] && !replace_evidence && !replaced_evidence_last_time) {
            cases_to_ignore.push(key)
        } else {
            if (old_evidence == null) {old_evidence = {}}
            old_evidence[key] = JSON.stringify(data[key])
        }   
    })
    cases_to_ignore.forEach(key => {
        delete data[key]
    })
    
    if (replace_evidence) {
        replaced_evidence_last_time = true
    }


    console.log('data')
    return data
}

var old_evidence = null
var replaced_evidence_last_time = false