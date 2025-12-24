var globalColaLayout

function draw_network(model_name) {
    var svg = document.getElementById('bayesian_network')
    svg.replaceChildren()
    var width = svg.clientWidth,
        height = svg.clientHeight;
    var initialScale = 0.25
    var data = network[model_name]

    
    var radius_scale = d3.scaleLinear().domain([0,1]).range([30,100])

    var group_map = []
    var nodes = []
    data.nodes.forEach(function (n, i) {
        let g = n.group_name
        if (typeof group_map[g] == 'undefined') {
                    group_map[g] = [];
                }
        group_map[g].push(i)
        // let ig = igs[n.id] || 0
        let r = radius_scale(0) 
        nodes.push({'name': n.id, 'group': 1, 'radius': r, 'width': r*2, 'height': r*2})
    })

    var links = []
    data.links.forEach(function (l, i) {
        let source_node = nodes.findIndex(element => element.name === l.source)
        let target_node = nodes.findIndex(element => element.name === l.target)
        links.push({'source': source_node, 'target': target_node},)
    })


    var groups = []

    Object.keys(group_map).forEach(function (g, i){
        groups.push({'leaves': group_map[g], 'name': g, 'padding': 60})
    })


    var graph = {
        'nodes': nodes,
        'links': links,
        'groups': groups
    }

    var svg = d3.select("#bayesian_network")
    svg.append("defs").append("marker")
    .attr("id", "arrow")           // Die ID, um später darauf zu verweisen
    .attr("viewBox", "0 -5 10 10") // Koordinatensystem des Markers
    .attr("refX", 34)              // WICHTIG: Radius (30) + Puffer (8) = Pfeil am Rand
    .attr("refY", 0)               // Mitte der Spitze
    .attr("markerWidth", 6)        // Größe der Darstellung
    .attr("markerHeight", 6)
    .attr("orient", "auto")        // Pfeil rotiert automatisch mit der Linie
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")   // Zeichnet ein Dreieck
    .style("fill", "#999");        // Farbe (sollte zur Linienfarbe passen)

    var container = svg.append('g')

    const initialTranslateX = (width - width * initialScale) / 2;
    const initialTranslateY = (height - height * initialScale) / 2;

    var zoom = d3.zoom().on("zoom", function() {
        container.attr("transform", d3.event.transform); 
    });
    svg.call(zoom);


    // Wende Transformation direkt an (ohne Transition, damit es sofort da ist)
    svg.call(zoom.transform, d3.zoomIdentity
        .translate(initialTranslateX, initialTranslateY)
        .scale(initialScale)
    );
    
    var cola_d3 = cola.d3adaptor(d3)
        .size([width, height])
        .nodes(graph.nodes)
        .links(graph.links)
        .groups(graph.groups)
        .avoidOverlaps(true)
        .linkDistance(300)
        .flowLayout('y', 100)
        .start(10, 15, 20);

    globalColaLayout = cola_d3

    var group = container.selectAll(".group")
        .data(graph.groups)
        .enter().append("g")
        .attr("class", "group");


    group.append("rect")
        .attr("class", "group-rect")
        .attr("rx", 8).attr("ry", 8);


    group.append("text")
        .attr("class", "group-label")
        .text(d => d.name)
        .attr("x", 10)
        .attr("y", 20)
        .call(cola_d3.drag);


    var link = container.selectAll(".link")
        .data(graph.links)
        .enter().append("line")
        .attr("class", "link")
        .attr("marker-end", "url(#arrow)");;

    // --- Knoten (Nodes) ---
    var node = container.selectAll(".node")
        .data(graph.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(cola_d3.drag);
    
        node.append("text")
        .attr("class", "label")
        .text(d => d.name)
        .attr("text-anchor", "middle")
        .attr("y", d => d.radius + 15);

    node.append('circle')
        .attr("r", d => d.radius)
        .style("fill", 'white')

    var foreignObject = node.append("foreignObject")
        .attr('width', d => d.radius * 2)
        .attr('height', d => d.radius * 2)
        .attr('x', d => - d.radius)
        .attr('y', d => -d.radius)
        .style("overflow", "visible");

    var vega_lite_div = foreignObject.append('xhtml:div')
        .attr('id', function (d) {return 'network_' + clean_id(d.name)})
        .attr('class', 'network-vega-lite-container')
        .style("width", d => d.radius * 2 + "px")
        .style("height",  d => d.radius * 2 + "px")
        .style("display", "flex") 
        .style("justify-content", "center")
        .style("align-items", "center");




    cola_d3.on("tick", function () {
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("transform", d => "translate(" + d.x + "," + d.y + ")");

        var groupMargin = 30;

        group.select(".group-rect")
            .attr("x", d => d.bounds.x + groupMargin)
            .attr("y", d => d.bounds.y + groupMargin)

            .attr("width", d => Math.max(0, d.bounds.width() - 2 * groupMargin))
            .attr("height", d => Math.max(0, d.bounds.height() - 2 * groupMargin));

        group.select(".group-label")
            .attr("x", d => d.bounds.x + groupMargin + 5)
            .attr("y", d => d.bounds.y + groupMargin - 10);
    });

}


function update_network_ig() {
    var newIgMap = interaction.ig_data[interaction.selected_model]
    if (!newIgMap) {return}
    var radiusScale = d3.scaleLinear().domain([0, 1]).range([30,100]);
    var nodesSelection = d3.selectAll(".node");
    nodesSelection.each(function(d) {
        if (newIgMap.hasOwnProperty(d.name)) {
            d.ig = newIgMap[d.name];
            d.radius = radiusScale(d.ig);
            
            d.width = d.radius * 2;
            d.height = d.radius * 2;
        }
    });

    var t = d3.transition().duration(750).ease(d3.easeCubicInOut);

    nodesSelection.select("circle")
        .transition(t)
        .attr("r", d => d.radius);

    nodesSelection.select("text.label")
        .transition(t)
        .attr("y", d => d.radius + 15);


    nodesSelection.select("foreignObject")
        .transition(t)
        .attr("width", d => d.radius * 2)
        .attr("height", d => d.radius * 2)
        .attr("x", d => -d.radius)
        .attr("y", d => -d.radius);

    // D) Das DIV innerhalb des ForeignObjects anpassen
    nodesSelection.select("foreignObject div")
        .transition(t)
        .style("width", d => (d.radius * 2) + "px")
        .style("height", d => (d.radius * 2) + "px");

    // 5. PHYSIK UPDATE
    // Da die Knoten jetzt größer sind, würden sie überlappen.
    // Wir starten Cola neu, aber mit wenigen Iterationen, damit es nur "zurechtrückt".
    if (globalColaLayout) {
        // start(initialUnconstrainedIterations, initialUserConstraintIterations, structuralIterations)
        // Wir nutzen hier sanfte Werte, damit das Netz nicht wild springt.
        globalColaLayout.start(10, 10, 10);
    }
}