class DonutChart extends Graph {
    constructor(target, data, title = '', size=100, fraction=1, cases = [1, 2, 3, 4, 5], category_order = []){
        super(target);
        this.title = title
        this.category_order = category_order
        const specs = {
            '$schema': 'https://vega.github.io/schema/vega-lite/v6.json',
                        'background': 'transparent',
            'data': {'values': data},
            'height': size*2,
            'width': size*2,
            'padding': 0,
            'transform': [{'calculate': `indexof(${JSON.stringify(this.category_order)}, datum.category)`, 'as': 'cat_order'}],
            'layer': this.get_layers(cases, fraction, size),
            'config': {
                'legend': {
                    'disable': true
                },
            },
            "resolve": {
                "scale": {
                    "color": "independent"
                }
            },
        };
        
        const options = {
            actions: false, // Disable the export menu
            renderer: 'svg'
        };

        super.set_specs(specs);
        super.set_options(options);
    }

    get_layers(cases, fraction, size) {
        const select = {
            'params': [
                {
                    'name': 'select',
                    'select': {'type': 'point', 'fields': ['case', 'value', 'category', 'title']}
                },
            ]
        }
        
        var layers = []
        var radius_step = size/cases.length
        var signal_names = []
        var color_scales = ['blues', 'greens', 'reds', 'oranges', 'purples', 'teals']
        for (let i=0; i < cases.length; i++) {
            let signal_name = 'select' + cases[i]
            var layer = {
                    'mark': {'type': 'arc', 'innerRadius': i*radius_step/fraction, 'outerRadius': (i*radius_step+radius_step)/fraction},
                    'transform': [
                        {'filter': "datum.case == 'case" + cases[i] + "'"},
                        {
                            'calculate': "datum.case == 'case0' ? 'Ref.' : replace(datum.case, 'case', '')",
                            'as': 'case_name'
                        }
                    ],
                    'encoding': {
                        'theta': {'field': 'value', 'type': 'quantitative'},
                        'color': {'field': 'category', 'type': 'nominal', 'scale': {'scheme': color_scales[i], 'domain': this.category_order}},
                        "fillOpacity": {
                            "condition": {
                                "param": signal_name,
                                "value": 1.0
                            },
                            "value": 0.3
                        },
                        "order": {
                            "field": "cat_order",
                            "type": "ordinal",
                            "sort": 'ascending'
                        },
                        'tooltip': [
                                {'field': 'case_name', 'type': 'nominal', 'title': 'Fall'},
                                {'field': 'title', 'type': 'nominal', 'title': 'Knoten'},
                                {'field': 'category', 'type': 'nominal', 'title': 'Kategorie'},
                                {'field': 'value', 'type': 'quantitative', 'title': 'Wahrscheinlichkeit in %'},
                            ],
                    },
                    'params': [
                        {
                            'name': signal_name,
                            'select': {'type': 'point', 'fields': ['case', 'title', 'category', 'value']}
                        },
                    ]
            }
            layers.push(layer)
            signal_names.push(signal_name)
        }

        super.set_signals_names(signal_names)
        return layers
    }

}