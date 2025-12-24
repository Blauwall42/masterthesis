class GuidelineHandler {
    constructor(card_data, container_id){
        this.card_data = card_data
        this.container = document.getElementById(container_id)
        this.group = {}
        Object.entries(this.card_data.groups).forEach(([key, data]) => {
            let div = document.createElement('DIV')
            div.id = key + '_card_container'
            div.classList.add('guideline_card_container', 'hidden')
            let header = document.createElement('h3')
            header.classList.add('card_title')
            header.textContent = data.title

            let help_wrapper = document.createElement('DIV')
            help_wrapper.setAttribute('data-tooltip', 'Leitlinienversion ' + data.guideline.version + ', S' + data.guideline.page)
            help_wrapper.setAttribute('data-placement', 'left')
            let help = document.createElement('SPAN')
            help.innerText = 'help'
            help.classList.add('material-icons')
            help_wrapper.appendChild(help)
            header.appendChild(help_wrapper)

            div.appendChild(header)

            this.container.appendChild(div)
            let start_card_id = data.start_card
            this.create_card(key, start_card_id)
        });
        document.getElementById(this.card_data.start_group + '_card_container').classList.remove('hidden')
    }

    create_card(group_id, card_id, link=null){
        console.log(group_id, card_id)
        var data = this.card_data.groups[group_id].cards[card_id]
        var card = document.createElement('DIV')
        card.id = group_id + '_' + card_id
        card.classList.add('card-content')

        console.log(group_id, card_id)
        if (data.subtitle) {
            card.appendChild(this.create_text_element('h6', data.subtitle, ['card_subtitle']))
        }
        if (data.text) {
            card.appendChild(this.create_text_element('p', data.text, ['card_text']))
        }
        if (data.question) {
            card.appendChild(this.create_text_element('SPAN', data.question, ['card_question']))
        }
        if (data.additional) {
            card.appendChild(this.create_text_element('SPAN', data.additional, ['card_additional']))
        }

        if (data.list) {
            let list = document.createElement('UL')
            data.list.forEach(element => {
                let li = document.createElement('LI')
                li.textContent = element
                list.appendChild(li)
            })
            card.appendChild(list)
        }

        if (data.options) {
            let content = this.create_card_logic(group_id, card_id, link)
            if (!content) {return}
            card.appendChild(content)
        }
        document.getElementById(group_id + '_card_container').appendChild(card)
    }

    create_text_element(node_type, text, classes=[]) {
        var text_element = document.createElement(node_type)
        text_element.textContent = text
        classes.forEach((class_name) => {
            text_element.classList.add(class_name)
        })
        return text_element
    }


    create_card_logic(group_id, card_id, link=null){
        let data = this.card_data.groups[group_id].cards[card_id]
        let options = data.options
        var content = document.createElement('DIV')
        if (link) {
            var link_data = '{\'index\': ' + link.index + ', \'sum\': ' + link.sum + ', \'group_id\': \'' + link.group_id + '\', \'parent_card\': \'' + link.parent_card + '\'}'
        }

        if (options.type == 'button') {
            Object.values(options.values).forEach(option => {
                let button = document.createElement('BUTTON')
                button.textContent = option.text
                if (option.action.type == 'card') {
                    let next_card = option.action.id
                    button.setAttribute('onclick', 'guideline_handler.replace_card(\'' + group_id + '\', \'' + next_card + '\')')
                }
                if (option.action.type == 'link_child') {
                    button.setAttribute('onclick', 'guideline_handler.sum_up_options(\'' + group_id + '\', \'' + card_id + '\', ' + link_data + ', ' + option.action.value + ')')
                }
                if (option.action.type == 'group') {
                    let next_group = option.action.id
                    button.setAttribute('onclick', 'guideline_handler.change_group("' + next_group + '")')
                }
                
               content.append(button)
               content.classList.add('btn-container')
            })
        }

        if (options.type == 'checkbox') {
            let counter = 0
            Object.values(options.values).forEach(option => {
                var input = document.createElement('INPUT')
                input.setAttribute('type', 'checkbox')
                input.id = group_id + '_' + card_id + '_' + counter
                input.value = option.value
                var label = document.createElement('LABEl')
                label.htmlFor = group_id + '_' + card_id + '_' + counter++
                label.appendChild(input)
                label.appendChild(document.createTextNode(option.text))
                content.appendChild(label)
            })
            var button = document.createElement('BUTTON')
            button.textContent = 'Weiter'
            let onclick_func = 'guideline_handler.sum_up_options(\'' + group_id + '\', \'' + card_id + '\''
            if (link) {
                var link_data = '{\'index\': ' + link.index + ', \'sum\': ' + link.sum + ', \'group_id\': \'' + link.group_id + '\', \'parent_card\': \'' + link.parent_card + '\'}'
                onclick_func += ', ' + link_data
            }
            button.setAttribute('onclick', onclick_func + ')')
            let button_container = document.createElement('DIV')
            button_container.appendChild(button)
            button_container.classList.add('btn-container')
            content.appendChild(button_container)
            content.classList.add('checkbox-container')
        }

        if (options.type == 'link') {
            if (link == null) {
                link = {
                    "index": 0,
                    "sum": 0,
                    "group_id": group_id,
                    "parent_card": card_id
                }
            }
            if (link.index < options.values.length){
                this.replace_card(group_id, options.values[link.index++], link)
            } else {
                var new_card_id = null
                Object.values(data.results).forEach(element => {
                    if ((element.operation == 'equal' && link.sum == element.value) ||
                        (element.operation == 'greater' && link.sum > element.value) ||
                        (element.operation == 'less' && link.sum < element.value)
                    ) {
                        if (element.return.type == 'card') {
                            new_card_id = element.return.id
                        }
                    }
                })
                this.replace_card(group_id, new_card_id)
            }
            
            return false
        }
       
        return content
    }

    sum_up_options(group_id, card_id, link = null, btn_value = null){
        var options = document.getElementById(group_id + '_' + card_id)
        var result = null
        var next_card = null

        if (btn_value || btn_value == 0) {
            result = btn_value
        } else {
            var count_selected  = options.querySelectorAll('input:checked').length
            console.log(count_selected)
            Object.values(this.card_data.groups[group_id].cards[card_id].results).forEach(element => {
                if ((element.operation == 'equal' && count_selected == element.value) ||
                    (element.operation == 'greater' && count_selected > element.value) ||
                    (element.operation == 'less' && count_selected < element.value)) {
                    if (element.return.type == 'value') {
                        result = element.return.value
                    }
                    if (element.return.type == 'card') {
                        next_card = element.return.id
                    }
                }
            })
        }
        if (link) {
            link.sum += result
            console.log(link)
            this.replace_card(link.group_id, link.parent_card, link)
        } else if (next_card) {
            this.replace_card(group_id, next_card)
        }


    }
    
    replace_card(group_id, card_id, link=null) {
        var container = document.getElementById(group_id + '_card_container').querySelector('.card-content')
        console.log(container)
        if (container) {container.remove()}
        this.create_card(group_id, card_id, link)
    }

    change_group(group) {
        document.querySelectorAll('.guideline_card_container').forEach(elem => {elem.classList.add('hidden')})
        document.getElementById(group + '_card_container').classList.remove('hidden')
    }
}

guideline_handler = new GuidelineHandler(card_data, 'tab_guideline')