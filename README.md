content-provenance
==================
Scripts to extract and visualize the content import graph for Studio channels.



Context
-------
(explain on call)



Extract
-------
Inputs: a `channel_id` for the channel we want to analyze (henceforth called
        channel under visualization (CUV)
Outputs: raw data for channel imports grouped by channel

Node data (each channel or folder):
  - Channel name
  - channel_id
  - counts (dict of the form {str-->int} that contains total counts of items in channel
  - modified?
  - curated (bool): True if channel is manually curated, False if channel is a ricecooker
    


Edge data:
  - original_channel_id   # a.k.a source id
  - channel_id            # a.k.a target id
  - counts (dict of the form {str-->int} that contains counts of imported items)


Option 1: use `libstudio` and json exports (NOT GOOD---TOO SLOW)
Option 2: run as queries in the django shell, print to stdout + copy paste
(see )



Transform
---------
In order for the visualization to obey the "conservation of content" principle,
we must process the raw data to augment with two types of dummy nodes:
  - Not used: dummy node for content that is not imported.
    Add to all channels nodes except CUV
  - Original content: dummy node to represent new content added to a channel that
    is not imported from any pre-existing channel.
    Add to all curated channels but not ricecooker channels.



Load
----
The import visualization js should its loading some `import_graph_data.json`
(static file for testing but long term could be an API endpoints, e.g. `/api/provenance/{{channel_id}}`
which returns a json for channel_id and is rendered by a generic js channel provenance visualizer view)

After loading the "raw" json data, js code should do necessary transforms to make
it suitable for the different vizs:
  - Viz 1: aggregate different counts of different content kinds to form total import counts; sankey
  - Viz 2: Sankey with different content kinds colored in differenr colors and tracked separately,
    i.e., treat each content kind as a different type of edge
  - Viz 3: ?



### Visualization requirements

  - hide -added for leftmost nodes (original source channels that that import from any channel)
  - hide -unused for the CUV 


### Challenges
  - the size of the -unused and -added for large channels like Khan Academy might dwarf the size of the rest of the content
    so it would be nice to do some sort of hiding 
    - if a node counts are > 1000 just show a 1000-sized box and display the total count (2k and 100k boxes are the same size as a 1k box)




Scope
-----

### In scope
  - Basic viz (all content kinds combined)
  - Detailed viz (show separate flows for each content kind)
  - On mouse-over info



### Out of scope (for now)
  - Granular graph, i.e., work with subfolders instead of just at channel-level




Links
-----

### D3

 - https://github.com/d3/d3-sankey
 - https://beta.observablehq.com/@mbostock/d3-sankey-diagram
 - https://bost.ocks.org/mike/sankey/
 - https://github.com/d3/d3-sankey#sankey_nodes
 - https://christophergandrud.github.io/networkD3/


### Sankey Google Chart

  - https://developers.google.com/chart/interactive/docs/gallery/sankey
  - https://www.rdocumentation.org/packages/googleVis/versions/0.6.0/topics/gvisSankey
  - https://stackoverflow.com/questions/45510421/how-to-make-a-googlevis-multiple-sankey-from-a-data-frame




