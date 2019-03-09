// TODO:
// 1. check out label issue with other datasets (e.g. sample_graph.json)
// 2. add mouse-over info box [in progress]
// 3. make responsive (?)

// DONE:
// 0. integrate 'added' and 'unused' (at least expand height of nodes to represent that)

// ==============
//	OPTIONS
// ==============

// var dataPath = "data_v2/292583c17e6d4199b81f0423bec58766.json";
// var dataPath = "data_v2/33c467480fe94f24b4797ef829af9ef6.json";
// var dataPath = "data_v2/34fd6722dd734687bc5291fc717d2d7f.json";
var dataPath = "data_v2/55eea6b34a4c481b8b6adee06a882360.json";

// -- circular links cause error --
// var dataPath = "data_v2/0a9cd3c76a36402e87d6bf80a997901f.json"; // PROBLEM
// var dataPath = "data_v2/591b7e1bc89645ef846c1685a7dd7b50.json"; // PROBLEM
// var dataPath = "data_v2/6f63fe92ad1044fdb3b3c17d54d0978e.json"; // PROBLEM
// var dataPath = "data_v2/9e5305326ed742d0892479dea825a514.json"; // PROBLEM

// indicate the channel uid suffixes to exclude from chart
// e.g. "added" or "unused"
// if multiple suffixes, use an array, like so: ["added", "unused"]
// use "none" to keep all links and nodes
var removeTerms = "unused";
//var removeTerms = "none";

var	margin = {top: 20, right: 100, bottom: 60, left: 120},
	// bottom margin for legend, left & right margins for labels
	width = 900 - margin.left - margin.right,
	height = 600 - margin.top - margin.bottom,
	nodeRect = {width: 20, padding:10};

var  palContent = {
		"document": "#f38080", // pink
		"topic": "#f3e21a", //"#ffe000", // yellow
		"exercise": "#16e485", // green
		"video": "#08BECC", // teal/lightblue
		"html5": "#488FBF" // darker blue
	};

var menuData = [
	{	value: "dataDense",
		text: "Condensed view"
	},
	{	value: "dataFull",
		text: "All channels"
	},
	{	value: "dataPart",
		text: "Partial channels"
	}
];

// ==============
//	DRAW SANKEY
// ==============

// create dropdown menu
// Create a dropdown

// d3.select("#options").append("p").attr("class", "optionLabel").text("chart style: ")
var menu = d3.select("#options")
	.append("select")

menu.selectAll("option")
	.data(menuData)
	.enter()
	.append("option")
        .attr("value", d => d.value)
	   .text(d => d.text);

// create base svg element for chart
var svg = d3.select("#diagram").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// create links (empty)
var links = svg.append("g")
	.attr("id", "linkGroup")
	.selectAll("path");

// create nodes (empty)
var nodes = svg.append("g")
	.attr("id", "nodeGroup")
	.selectAll("rect");

// create labels (empty)
var labels = svg.append("g")
	.attr("id", "labelGroup")
	.selectAll("text");

// get and append data
d3.json(dataPath)
	.then(function(dataOrig){

		// re-format data for d3-sankey
		var	dataForm	= formatData(dataOrig);

		// get data in all it's possible formats
		var dataSet = {
			dataFull: pipe(sankey		)(dataForm),	// complete data, all nodes/links
			dataPart: pipe(sankey, rmData	)(dataForm),	// partial data, some links hidden, node height represents total content
			dataDense: pipe(rmData, sankey)(dataForm)	// partial data, some links hidden, nodes condensed
		};

		drawSankey(dataSet[menuData[0].value]);

		menu.on('change', function() {
 		    var selectedOption = d3.select(this).property("value");
		    drawSankey(dataSet[selectedOption]);
 	    });

	});

// ==============
//	DRAW LEGEND
// ==============

var ordinal = d3.scaleOrdinal()
	.domain(Object.keys(palContent))
	.range(Object.values(palContent));

var legendOrdinal = d3.legendColor()
	.shape("path", d3.symbol().type(d3.symbolCircle).size(400)())
	.shapePadding(20)
	.scale(ordinal)
	.orient('horizontal');

var legend = svg.append("g")
	.attr("id", "legend")
	.attr("transform", "translate("+ width/2 + "," + (height + margin.top + 10) + ")")
	.call(legendOrdinal);

// ==============
//	FUNCTIONS
// ==============

// =============================
// pipes!
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);

// =============================
// create all the sankey elements
function drawSankey(data){
	drawLinks(data);
	drawNodes(data);
	drawLabels(data);
};

// =============================
// create nodes
function drawNodes(data){

	svg.selectAll("#nodeGroup").selectAll("rect").remove();

	nodes.data(data.nodes)
		.join("rect")
		.attr("x", d => d.x0)
		.attr("y", d => d.y0)
		.attr("height", d => d.y1 - d.y0)
		.attr("width", d => d.x1 - d.x0)
			.append("title")
			.text(d => d.name);
};

// =============================
// create links
function drawLinks(data){

	svg.selectAll("#linkGroup").selectAll("path").remove();

	links.data(data.links)
		.join("path")
		.attr("d", d3.sankeyLinkHorizontal())
		.attr("stroke", function(d,i) {return palContent[d.content];})
		.attr("stroke-width", d => Math.max(1, d.width))
		.append("title")
		 	.text(d => d.value + " " + d.content + "s");
};

// =============================
// create labels
function drawLabels(data){

	svg.selectAll("#labelGroup").selectAll("text").remove();

	labels.data(data.nodes)
		.join("text")
		.attr("x", d => d.x0 < width / 2 ? d.x1 - (nodeRect.width + 2) : d.x0 + (nodeRect.width + 2))
		.attr("y", d => (d.y1 + d.y0) / 2)
		.attr("dy", "0.35em")
		.attr("text-anchor", d => d.x0 < width / 2 ? "end" : "start")
		.text(d => d.title)
			.call(wrap, 100);

	svg.selectAll("#labelGroup").selectAll("text").attr("class", "label");

}

// =============================
// format input data correctly for sankey
function formatData(data){

	return {

		links:
			Object.values(data.edges).map( d => ({
				source: d[0],
				target: d[1],
				value: d[3],
				content: d[2]
			})),
		nodes:
			Object.keys(data.nodes).map( d => ({
				name:d,
				title: data.nodes[d].name
			}))

	}

};

// =============================
function rmData(data, terms){
// filter out nodes/links based on phrases at the end of the channel IDs (uids) (e.g. -added and -unused)

	// build a regular expression the searches for any of the
	// elements in terms in the channel IDs for nodes and links
	terms = terms || ["added","unused"];
	if (Array.isArray(terms)) {
		terms = terms.map(term => "("+term+")").join('|');
	}
	var re = new RegExp(terms, 'i');

	// filter
	data.nodes = data.nodes.filter(node => !re.test(node.name));
	data.links = data.links.filter(link =>
		// for when data is removed before sankey-ficiation:
		!re.test(link.source) &
		!re.test(link.target) &
		// for when data is removed after sankey-ification:
		!re.test(link.source.name) &
		!re.test(link.target.name)
	)

	return data;

}

// =============================
// generate sankey nodes/links
function sankey(data){

	const sankey = d3.sankey()
		.nodeId(d => d.name)
		.nodeWidth(nodeRect.width)
		.nodePadding(nodeRect.padding)
		.extent([[1, 5], [width - 1, height - 5]]);

	return sankey({
		 nodes: data.nodes.map(d => Object.assign({}, d)),
		 links: data.links.map(d => Object.assign({}, d)),
	 });
};

// =============================
// wrap long text
// credit: Mike Bostock, https://bl.ocks.org/mbostock/7555321
function wrap(text, width) {

	text.each(function() {
		var	text = d3.select(this),
			words = text.text().split(/\s+/).reverse(),
			word,
			line = [],
			lineNumber = 0,
			lineHeight = 0.95, // ems
			y = text.attr("y"),
			x = text.attr("x"),
			dy = parseFloat(text.attr("dy")),
			tspan = text.text(null)
		 		.append("tspan")
					.attr("x", x)
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
				 	.attr("x", x)
					.attr("y", y)
					.attr("dy", ++lineNumber * lineHeight + dy + "em")
					.text(word);
			}
		}
	});
};
