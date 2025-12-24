/**
 * Class for easier vega-lite handling.
 *
 * @class Graph
 * @typedef {Graph}
 */
class Graph{
    
    /**
     * Creates an instance of Graph.
     *
     * @constructor
     * @param {*} target 
     */
    constructor(target) {
        this.target = target;
        this.vega_vis = null;
        this.signal_names = [];
    }

    
    /**
     * Saves the vega-lite specs as private variable
     *
     * @param {dict} specs 
     */
    set_specs(specs){
        this.specs = specs
    }


    set_signals_names(signal_names){
        this.signal_names = signal_names
    }
    
    
    /**
     * Saves options for vegaEmbed as private variable.
     *
     * @param {*} options 
     */
    set_options(options){
        this.options = options;
    }


    
    /** Renders the vega-lite graph. */
    render() {
        let graph = this
        vegaEmbed('#' + graph.target, graph.specs, graph.options)
        .then(function(vega_vis) {
            
            // Register a SignalListener for selecting data in the graph
            graph.vega_vis = vega_vis;
            for (let i=0; i < graph.signal_names.length; i++){
                graph.vega_vis.view.addSignalListener(graph.signal_names[i], function (signalName, e) {
                    interaction.criteria_highlight(e, [graph])
                });
            }
            // console.log('Graph Init')
            // console.log(graph.specs)
            // console.log(vega_vis.view.getState())
        });
    }

    get_selection() {
        return this.vega_vis.view.getState()
    }

    set_selection(state) {
        this.vega_vis.view.setState(state)
    }

    delete_selection() {
        // console.log(this.title)
        var state = this.vega_vis.view.getState()
        Object.keys(state['data']).forEach(key => {
            state['data'][key] = []
        });
        this.vega_vis.view.setState(state)
    }
}