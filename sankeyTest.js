// TODO:
// 0. integrate 'added' and 'unused' (at least expand height of nodes to represent that)
// 1. check out label issue with other datasets (e.g. sample_graph.json)
// 2. add mouse-over info box
// 3. make responsive

// ==============
//	OPTIONS
// ==============

var dataPath = "data/55eea6b34a4c481b8b6adee06a882360.json";
//var dataPath = "data/sample_graph.json"; // <-- weird label issue to debug
//var dataPath = "data/33c467480fe94f24b4797ef829af9ef6.json"; // <-- weird label issue to debug

var	margin = {top: 20, right: 100, bottom: 60, left: 120},
	// bottom margin for legend, left & right margins for labels
	width = 900 - margin.left - margin.right,
	height = 550 - margin.top - margin.bottom,
	nodeRect = {width: 20, padding:10};

var	colNode = "#60605d", // dark grey
	palContent = {
		"document": "#D87852", // orange
		"topic": "#F7BE38", // yellow
		"exercise": "#71933E", // green
		"video": "#08BECC", // teal/lightblue
		"html5": "#488FBF" // darker blue
	};

// ==============
//	DRAW SANKEY
// ==============

var svg = d3.select("#container").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json(dataPath)
	.then(function(original_data){

		var data = sankey(formatData(original_data));

		// === nodes
		svg.append("g")
			.attr("stroke", "#000")
			.selectAll("rect")
				.data(data.nodes)
				.join("rect")
				.attr("x", d => d.x0)
				.attr("y", d => d.y0)
				.attr("height", d => d.y1 - d.y0)
				.attr("width", d => d.x1 - d.x0)
				.attr("fill", colNode)
				.attr("stroke", "none")
				.append("title")
					.text(d => d.name);

		// === links
		const link = svg.append("g")
			.attr("fill", "none")
			.attr("stroke-opacity", 0.7)
			.selectAll("g")
				.data(data.links)
				.join("g");

		link.append("path")
			.attr("d", d3.sankeyLinkHorizontal())
			.attr("stroke", function(d,i) {return palContent[d.content];})
			.attr("stroke-width", d => Math.max(1, d.width));

		link.append("title")
			.text(d => d.value + " " + d.content + "s");

		// === labels
		svg.append("g")
			.style("font", "11px sans-serif")
			.style("fill", colNode)
			.selectAll("text")
				.data(data.nodes)
				.join("text")
				.attr("x", d => d.x0 < width / 2 ? d.x1 - (nodeRect.width + 2) : d.x0 + (nodeRect.width + 2))
				.attr("y", d => (d.y1 + d.y0) / 2)
				.attr("dy", "0.35em")
				.attr("text-anchor", d => d.x0 < width / 2 ? "end" : "start")
				.text(d => d.title)
					.call(wrap, 115);
	});

// ==============
//	DRAW LEGEND
// ==============

var ordinal = d3.scaleOrdinal()
	.domain(Object.keys(palContent))
	.range(Object.values(palContent));

var legendOrdinal = d3.legendColor()
	.shape("path", d3.symbol().type(d3.symbolCircle).size(400)())
	.shapePadding(24)
	.scale(ordinal)
	.orient('horizontal');

var legend = svg.append("g")
		.attr("class", "legendOrdinal")
		.attr("transform", "translate("+ width/2 + "," + (height + margin.top + 10) + ")")
		.call(legendOrdinal);

legend.selectAll("text")
	.style("font", "11px sans-serif")
	.style("fill", colNode);

legend.selectAll("path")
	.attr("opacity", "0.7");

// ==============
//	FUNCTIONS
// ==============

// format input data correctly for sankey
function formatData(data){

	var newData = {nodes: [], links: []};

	// test for and (for now) remove 'added' and 'unused' channels
	var re = /(added)|(unused)/i;

	// add reformatted links
	Object.entries(data.edges).forEach(([key, value]) => {

		if (!re.test(value[0]) & !re.test(value[1])) {

			newData.links.push({
				source: value[0],
				target: value[1],
				value: value[3],
				content: value[2]
			});
		};

	});

	// add reformatted nodes
	Object.keys(data.nodes).forEach(function(part, index, theArray) {
		if (!re.test(part)) {
			newData.nodes.push({
				name: part,
				title: data.nodes[part].name
			});//
		};
	});

	return newData;
};

// generate sankey nodes/links
function sankey(data){

	const sankey = d3.sankey()
		.nodeId(d => d.name)
		.nodeWidth(nodeRect.width)
		.nodePadding(nodeRect.padding)
		.extent([[1, 5], [width - 1, height - 5]]);

	return sankey({
		 nodes: data.nodes.map(d => Object.assign({}, d)),
		 links: data.links.map(d => Object.assign({}, d))
	 });
};


// wrap long text
// credit: Mike Bostock, https://bl.ocks.org/mbostock/7555321
function wrap(text, width) {

	text.each(function() {
		var	text = d3.select(this),
			words = text.text().split(/\s+/).reverse(),
			word,
			line = [],
			lineNumber = 0,
			lineHeight = 0.97, // ems
			y = text.attr("y"),
			dy = parseFloat(text.attr("dy")),
			tspan = text.text(null)
		 		.append("tspan")
					.attr("x", text.attr("x"))
					.attr("y", y)
					.attr("dy", dy + "em");

		while (word = words.pop()) {
			line.push(word);
			tspan.text(line.join(" "));
			if (tspan.node().getComputedTextLength() > width) {
				line.pop();
				tspan.text(line.join(" "));
				line = [word];
				tspan = text.append("tspan")
				 	.attr("x", 0)
					.attr("y", y)
					.attr("dy", ++lineNumber * lineHeight + dy + "em")
					.text(word);
			}
		}
	});
};
