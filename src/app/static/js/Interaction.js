/**
 * Class for handling graph interaction
 *
 * @class Interaction
 * @typedef {Interaction}
 */
class Interaction {
    
    /**
     * Creates an instance of Interaction.r
     *
     * @constructor
     */
    constructor(selected_model, import_patient_data = false) {
        // All donut-graph instances are stored in this variable. Every diagnosis prediction graph gets registered first.
        this.donut_graphs = [
            {'view': 'prediction','container_id': 'ADNI', 'title': 'ADNI', 'model_key': 'ADNI', 'feature_key': 'Diagnose', 'graph': null},
            {'view': 'prediction','container_id': 'DELCODE', 'title': 'DELCODE', 'model_key': 'DELCODE', 'feature_key': 'Diagnose', 'graph': null}
        ]
        this.ig_data = []
        this.UR_handler = new UndoRedoHandler()

        this.add_nodes_graphs_to_donut_graphs_list()
        console.log('import patient')
        console.log(import_patient_data)
        if (import_patient_data) {
            this.case_counter = import_patient_data['interaction_data']['case_counter']
            this.case_list = import_patient_data['interaction_data']['case_list']
            this.import_cases(import_patient_data['cases_data'])
            this.change_patient_data(import_patient_data)
            this.selected_model = selected_model
        } else {
            this.case_counter = 0
            this.case_list = []
            this.add_case()
            this.selected_model = selected_model
        }
        this.initialize()

        this.inferred_data = {}
    }

    
    /** Initialize default view */
    initialize(){
        draw_network(this.selected_model)
        this.inference()
    }

    inference(replace_evidence = false, model=false){
        inference(this.case_list, replace_evidence, model)
    }

    
    /** Register every node of all bayesian networks as a vega-lite graph */
    add_nodes_graphs_to_donut_graphs_list(){
        for (let network_keys of Object.keys(network)) {
            for (let node of network[network_keys]['nodes']){
                let node_id = node['id']
                this.donut_graphs.push(
                    {'view':'network', 'container_id': 'network_' + clean_id(node_id), 'model_key': network_keys, 'feature_key': node_id, 'graph': null}
                )
            }
        }
    }

    
    /**
     * Renders every in this.donut_graphs registered graphs
     *
     * @param {dict} data - inferred data
     */
    render_graphs(new_inferred_data) {
        Object.keys(new_inferred_data).forEach(key => {
            this.inferred_data[key] = structuredClone(new_inferred_data[key])
        })
        
        for (let i = 0; i < this.donut_graphs.length; i++) {
            let container_id = this.donut_graphs[i]['container_id']
            let graph_data = this.get_graph_data(this.inferred_data, i)
            if (this.donut_graphs[i]['view'] == 'network') {
                let title = this.donut_graphs[i]['feature_key']

                // Graph in bayesian network node
                //document.getElementById('model_selection').value
                if (this.donut_graphs[i]['model_key'] == this.selected_model){
                    let category_order = category_list[this.selected_model][title]
                    this.donut_graphs[i]['graph'] = new DonutChart(container_id, graph_data, title, 100, 1, this.case_list, category_order)
                } else {
                    this.donut_graphs[i]['graph'] = null
                }
            } else {
                // Graph in prediction view
                let title = 'Diagnose' // this.donut_graphs[i]['title']
                let category_order = category_list[this.donut_graphs[i]['model_key']][title]
                this.donut_graphs[i]['graph'] = new DonutChart(container_id, graph_data, title, 100, 1, this.case_list, category_order)
            }
            if (this.donut_graphs[i]['graph']) {
                this.donut_graphs[i]['graph'].render()
            }
        }
    }

    
    /**
     * Transforms the inferred data received from the server to easily processable format for vega-lite graph.
     *
     * @param {dict} data - Inferred data
     * @param {number} graph_index - Index for accessing a specific graph from this.donut_graphs
     * @returns {list}} - Transformed data
     */
    get_graph_data(data, graph_index) {
        let graph_data = []
        let case_keys = Object.keys(data)
        let model_key = this.donut_graphs[graph_index]['model_key']
        let feature_key = this.donut_graphs[graph_index]['feature_key']
        for (const case_key of case_keys) {
            if (data[case_key][model_key][feature_key] == undefined) {
                graph_data.push({'title': feature_key, 'case': case_key, 'category': 'Selected', 'value': 1, 'model_key': model_key})
                continue                
            }
            for (const [key, value] of Object.entries(data[case_key][model_key][feature_key])){
                graph_data.push({'title': feature_key,'case': case_key,'category': key,'value': value}
            )
            }            
        
        }
       return graph_data
    }

    add_case(case_id = false, to_undo = true, reset_redo_history = true, criteria_data = false, case_count = false){
        if (!case_id){
            case_id = this.case_counter
        }
        
        if (case_id > 0) {
            this.UR_handler.push_to_history({
                'type': 'add case',
                'change': {
                    'case_id': case_id,
                    'case_counter': this.case_counter,
                    'case_list': Array.from(this.case_list)
                }
            }, to_undo, reset_redo_history)
        }

        this.case_list.push(case_id)
        this.add_case_list(case_id, 'template-criteria-list', 'criteria_list_container')

        this.add_case_to_case_selector(case_id)

        if (criteria_data) {
            criteria_data.forEach(item => {
                if (!item['empty']) {
                    document.getElementById(item['criteria-item']).classList.remove('empty')
                }
                document.getElementById(item['criteria-input']).value = item['value']
            })
        }
    
        if (case_count) {
            this.case_counter = case_count
        } else {
            this.case_counter += 1
        }
    }

    add_case_to_case_selector(case_id) {
        var case_name = 'What-If-Fall ' + case_id

        if (case_id > 0) {
            document.querySelectorAll('#case0_criteria_list .criteria-item:not(.empty)').forEach(
                elem => {
                    let criteria = elem.id.replace(/^case0/, "")
                    let value = document.getElementById('case0_input' + criteria).value
                    document.getElementById('case' + case_id + '_input' + criteria).value = value
                    document.getElementById('case' + case_id + criteria).classList.remove('empty')
                }
            )
        } else {
            case_name = 'Referenz'
        }

        var case_selector = document.getElementById('input_case_selection')

        let option = new Option(case_name, 'case' + case_id, false, true)

        case_selector.appendChild(option)
        this.show_selected_case('case' + case_id)
        if (this.case_list.length > 5) {
            document.getElementById('add_case_btn').disabled = true
        }

        if (this.case_list.length > 1){
            document.getElementById('remove_case_btn').disabled = false
        } else {
            document.getElementById('remove_case_btn').disabled = true
        }
    }

    import_cases(cases_data){
        this.case_list.forEach((case_id, index) => {
            this.add_case_list(case_id,  'template-criteria-list', 'criteria_list_container')
            this.add_case_to_case_selector(case_id)
            for (var [key, value] of Object.entries(cases_data[index])){
                console.log(key)
                let criteria_item = document.querySelector('#' + key)
                console.log(criteria_item)
                criteria_item.classList.remove('empty')
                criteria_item.querySelector('input, select').value = value
            }
        })
        this.show_selected_case('case' + this.case_list[0])
    }

    add_case_list(case_id, template_id, target_container){
        var criteria_list_template = document.getElementById(template_id)
        var criteria_list = criteria_list_template.content.cloneNode(true)
        var elements_with_id = criteria_list.querySelectorAll("[id]")
        elements_with_id.forEach(el => {
            const old_id = el.id
            el.id = 'case' + case_id + old_id
        });

        var elements_with_for = criteria_list.querySelectorAll("[for]");

        elements_with_for.forEach(el => {
            const old_for = el.htmlFor
            el.htmlFor = 'case' + case_id + old_for
        });

        criteria_list.querySelectorAll('.criteria-input').forEach(el=>{
            el.dataset.case = case_id
        })
        document.getElementById(target_container).appendChild(criteria_list)
    }


    remove_case(case_id = false, to_undo = true, reset_redo_history = true) {
        var case_selector = document.getElementById('input_case_selection')
        if (!case_id) {
            case_id = case_selector.value.replace(/^case/, "")
        }
        if (case_id == 0){ return }

        var criteria_list = document.getElementById('case' + case_id + '_criteria_list')
        
        this.UR_handler.push_to_history({
            'type': 'remove case',
            'change': this.get_case_data(criteria_list, case_id)
        }, to_undo, reset_redo_history)

        this.case_list = this.case_list.filter(item => item != case_id)
        criteria_list.remove()
        var query = 'option[value="case' + case_id + '"]'
  
        var option_to_be_removed = case_selector.querySelector(query)
        if (option_to_be_removed) {
            option_to_be_removed.remove()
        }
        this.show_selected_case('case' + this.case_list[0])
        document.getElementById('add_case_btn').disabled = false
        if (this.case_list == [0]) {
            document.getElementById('remove_case_btn').disabled = true
        }
    }

    highlight_node(node_id) {
        document.querySelectorAll('.highlighted-node').forEach(elem => {
            elem.classList.remove('highlighted-node')
        })
        let node_foreign_div= document.getElementById('network_' + node_id)
        let node = node_foreign_div.parentElement.parentElement
        node.querySelector('circle').classList.add('highlighted-node')
    }

    criteria_highlight(e, ignored_graphs = []) {
        console.log(e)
        var case_id = e['case'][0]
        let replace_evidence = {
            'case_id': case_id,
            'feature': e['title'][0],
            'value': e['category'][0]
        }
        // console.log(replace_evidence)
        if (replace_evidence['feature'] != 'Diagnose') {
            this.inference(replace_evidence, this.selected_model)
        }

        this.show_selected_case(case_id)
        var query = 'option[value="' + case_id + '"]'
        var option = document.getElementById('input_case_selection').querySelector(query)
        if (option) {
            option.selected = true
        }

        this.delete_highlight(ignored_graphs)

        // console.log(e)
        this.show_node_details(e)

        
        var query = '[id^="' + case_id + '"][id$="' + clean_id(e['title'][0]) + '"]'
        var criteria = document.querySelector(query)
        criteria.classList.add('highlighted')
        document.querySelectorAll('.criteria-group').forEach( element => {
            element.open = true
        })
        
        this.highlight_node(clean_id(criteria.querySelector('.criteria-input').dataset.node))
        criteria.scrollIntoView()
    }

    show_node_details (data) {
        document.getElementById('node_details').classList.remove('hidden')
        let case_id = String(data['case']).replace(/^case/, "")
        if (case_id == 0) {
            case_id = 'Referenz'
        }
        document.getElementById('node_detail_case').textContent = case_id
        document.getElementById('node_detail_name').textContent = data['title']
        document.getElementById('node_detail_category').textContent = data['category']
        document.getElementById('node_detail_prob').textContent = parseFloat(data['value']).toFixed(2)
    }


    remove_node_details () {
        document.getElementById('node_details').classList.add('hidden')
        document.getElementById('node_detail_case').textContent = ''
        document.getElementById('node_detail_name').textContent = ''
        document.getElementById('node_detail_category').textContent = ''
        document.getElementById('node_detail_prob').textContent = ''
    }

    delete_highlight(ignored_graphs = []) {
        document.querySelectorAll('.highlighted').forEach( element => {
            element.classList.remove('highlighted')
        })
        document.querySelectorAll('.highlighted-node').forEach(elem => {
            elem.classList.remove('highlighted-node')
        })
        this.delete_graph_selection(ignored_graphs)
        this.remove_node_details()
    }


    delete_graph_selection(ignored_graphs = []){
        this.donut_graphs.forEach(graph => {
            if (graph['graph'] && !ignored_graphs.includes(graph['graph'])) {
                graph['graph'].delete_selection()
            }
        })
    }

    show_selected_case(case_id) {
        var active_criteria_list = document.querySelector('.criteria-list:not(.hidden)')
        if (active_criteria_list) {
            active_criteria_list.classList.add('hidden')
        }
        document.getElementById('input_case_selection').value = case_id
        document.querySelector('#' + case_id +'_criteria_list').classList.remove('hidden')
    
        document.getElementById('remove_case_btn').disabled = case_id == 'case0'
       
    }

    set_model(pressed_button, model) {
        var model_selection_buttons = document.getElementsByClassName('model-selection-btn')
        for (let button of model_selection_buttons) {
            button.classList.add('outline')
        }
        pressed_button.classList.remove('outline')
        this.selected_model = model
        draw_network(model);
        update_network_ig()
        this.inference()
    }

    undo() { this.UR_handler.undo()}
    redo() { this.UR_handler.redo()}


    change_patient_data (import_patient_data = false) {
        if (import_patient_data) {
            document.getElementById('patient_id_input').value = import_patient_data['patient_id']
            document.getElementById('patient_surname_input').value = import_patient_data['patient_surname']
            document.getElementById('patient_name_input').value = import_patient_data['patient_name']
            document.getElementById('patient_bday_input').value = import_patient_data['patient_bday']
            document.getElementById('patient_gender_input').value = import_patient_data['patient_gender']
        }
        var patient_id = document.getElementById('patient_id_input').value || 'N/A'
        var patient_surname = document.getElementById('patient_surname_input').value || 'N/A'
        var patient_name = document.getElementById('patient_name_input').value || 'N/A'
        var patient_bday = document.getElementById('patient_bday_input').value || 'N/A'
        
        if (!import_patient_data) {
            document.getElementById('case0_input_allgemein_geschlecht').value = document.getElementById('patient_gender_input').value
        }

        document.getElementById('patient_id').textContent = patient_id
        document.getElementById('patient_name').textContent = patient_surname + ', ' + patient_name
        document.getElementById('patient_bday').textContent = patient_bday
        document.getElementById('settings_modal').close()
    }

    toggle_theme () {
        var current_theme = document.documentElement.getAttribute('data-theme')
        if (!current_theme) {
        current_theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
        console.log(current_theme)
        if (current_theme == 'dark') {
            document.documentElement.setAttribute('data-theme', 'light')
        } else {
            document.documentElement.setAttribute('data-theme', 'dark')
        }
    }

    open_tab(tab) {
        document.querySelectorAll('.tab:not(.hidden)').forEach(elem => elem.classList.add('hidden'))
        document.getElementById(tab).classList.remove('hidden')
        document.querySelectorAll('.tab_btn:not(.outline)').forEach(elem => elem.classList.add('outline'))
        document.getElementById(tab + '_btn').classList.remove('outline')
    }


    get_criteria_input_data(element) {
        return {
            'criteria-item': element.parentElement.id,
            'empty': element.parentElement.classList.contains('empty'),
            'criteria-input': element.id,
            'value': element.value
        }
    }

    get_case_data(criteria_list, case_id) {
        var criteria_items = []

        criteria_list.querySelectorAll('.criteria-input').forEach((element) => {
                criteria_items.push(this.get_criteria_input_data(element))
            });
        return {
                'case_id': case_id,
                'criteria_list': criteria_list.id,    
                'case_counter': this.case_counter,
                'case_list': Array.from(this.case_list),
                'criteria-items': criteria_items
            }
    }

    

    scroll_to_top() {
        window.scrollTo({top: 0,behavior: "smooth"})}
}


var interaction = new Interaction('ADNI')

function clean_id(str) {
    return str
        .replace(/[^a-zA-Z0-9]/g, '_')
        .toLowerCase()
}