from __future__ import print_function
from contentcuration.models import *
from collections import defaultdict
import json



# EXTRACT
################################################################################
def get_source_node(node):
    schannel = Channel.objects.get(id=node.source_channel_id)
    if schannel:
        try:
            snode = schannel.main_tree.get_descendants().get(node_id=node.source_node_id)
            return snode
        except Exception as e:
            print('WARNING: could not find snode for node with studio_id =', node.id, ' node_id =', node.node_id)
            return None
    else:
        return None


def extract_nodes_and_edges(channel_id):
    nodes = {}  # lookup table for ContentNode objects by channel_id, by method, by source_id
    edges = [] # list of tuples (snode.id, node.id) decribing relations "node is imported from snode"
    
    def add_node(node, channel_id, method=None):
        """
        Add the ContentNode object to `nodes` data under `channel_id`, under `method`,
        where `method` is either "added" or "imported".
        """
        if channel_id not in nodes:
            nodes[channel_id] = {
                "added": {},
                "imported": {},
            }
        group_dict = nodes[channel_id][method]
        group_dict[node.id] = node
    
    def extract_imports(channel_id):
        """
        Write the graph infomation to `nodes` and `edges` for `channel_id`.
        """
        channel = Channel.objects.get(id=channel_id)
        node_list = channel.main_tree.get_descendants()
        source_channel_ids = set()
        for node in node_list:
            # split nodes in the according to the medhod of incluion
            # ADDED
            if node.node_id == node.source_node_id:
                add_node(node, channel_id, method='added')
            # IMPORTED
            else:
                # record import relationship as edge tuple
                snode = get_source_node(node)
                if snode:
                    add_node(node, channel_id, method='imported')  # moved here to avoid trouble
                    # print_node_info(snode)
                    edge_tuple = (snode.id, node.id)
                    edges.append(edge_tuple)
                    # queue up source channel_id for recusive call...
                    source_channel_id = snode.get_channel().id
                    assert source_channel_id == node.source_channel_id, 'source_channel_id mismatch!'
                    source_channel_ids.add(source_channel_id)
        
        # recusevily continue to build import-graph data if not already done...
        for source_channel_id in source_channel_ids:
            if source_channel_id not in nodes:
                print('Recursing into channel', source_channel_id)
                extract_imports(source_channel_id)
            else:
                print('No need to extract channel_id', channel_id, 'since already extracted.')
    #
    #
    extract_imports(channel_id)
    return nodes, edges





# interface \/ \/  (nodes, edges )  \/  \/ 







# TRANSFORM
################################################################################

def is_source(edges, studio_id):
    verdict = False
    for edge in edges:
        if edge[0] == studio_id:
            verdict = True
    return verdict


def is_target(edges, studio_id):
    verdict = False
    for edge in edges:
        if edge[1] == studio_id:
            verdict = True
    return verdict


def get_resource_counts_by_kind(subtree):
    node_list = subtree.get_descendants()
    # all_kinds = set([node.kind_id for node in node_list])
    counts = defaultdict(int)
    for node in node_list:
        counts[node.kind_id] += 1
    return counts


def get_channel_as_graph_node(channel, name=None, description=None):
    return {
        "channel_id": channel.id,
        "name": channel.name if name is None else name,
        "description": channel.description if description is None else description,
    }


def group_node_list_by_source_channel_id(node_list):
    results = defaultdict(list)
    for node in node_list:
        results[node.source_channel_id].append(node)
    return results


def get_graph(cuv_channel_id, nodes, edges):
    """
    Aggregate the individual edges to granularity of channel_id to form the data
    for the d3 content import vizualization.
    """
    cuv_channel = Channel.objects.get(id=cuv_channel_id)
    graph = {
        "title": "Import graph data for channel " + cuv_channel.name,
        "description": "The channel description of CUV is: " + cuv_channel.description,
        "nodes": {},  # dict {channel_id --> channel_info}, where channe_info is a dict with keys: name, channel_id, counts
        "edges": [],  # edges of the form (source, target, kind, count) where source and target are channel_ids
    }
    # for each channel, there are three graph nodes:
    #  - channel_id
    #  - channel_id+'-added' = to represent nodes added to studio by uploading new content
    #  - channel_id+'-unused' = nodes in a channel that are not imported into derivative channels
    for channel_id, channel_data in nodes.items():
        print('processing channel channel_id='+channel_id)
        channel = Channel.objects.get(id=channel_id)        
        # INPUTS: LISTS OF INDIVIDUAL CONTENT NODES
        added = channel_data["added"].values()
        imported = channel_data["imported"].values()
        all_nodes = added + imported
        # A. ADD GRAPH NODES
        # add three (3x) nodes that correspond to this channel_id
        ########################################################################
        # self
        channel_node = get_channel_as_graph_node(channel)
        channel_node['counts'] = get_resource_counts_by_kind(channel.main_tree)
        graph['nodes'][channel_id] = channel_node
        # added
        added_node_id = channel_id+'-added'
        added_node = get_channel_as_graph_node(
            channel,
            name='Added',
            description='Count of nodes uploaded to channel_id ' + channel_id
        )
        graph['nodes'][added_node_id] = added_node
        # unused
        unused_node_id = channel_id+'-unused'
        unused_node = get_channel_as_graph_node(
            channel,
            name='Unused',
            description='Connts of nodes in channel_id ' + channel_id + ' that are not imported in any downstream channels.'
        )
        graph['nodes'][unused_node_id] = unused_node
        
        
        # B. ADD GRAPH EDGES
        ########################################################################
        # 1. add unused edges
        # counts for the  {{channel_id}}  -->  {{channel_id}}-unused  edges
        unused_aggregates = defaultdict(int)
        for node in all_nodes:
            if not is_source(edges, node.id):
                unused_aggregates[node.kind_id] += 1
        unused_node['counts'] = unused_aggregates
        for kind, count in unused_aggregates.items():
            graph['edges'].append(  (channel_id, unused_node_id, kind, count)  )
        # 
        # 2. add added edges
        # counts for the  {{channel_id}}-added  -->  {{channel_id}}  edges
        added_aggregates = defaultdict(int)
        for node in all_nodes:
            if not is_target(edges, node.id):
                added_aggregates[node.kind_id] += 1
        added_node['counts'] = added_aggregates
        for kind, count in added_aggregates.items():
            graph['edges'].append(  (added_node_id, channel_id, kind, count)   )
        #
        # 3. add imports edges
        # we're computing (snode-->node) imports for current channel only---not recusively
        for source_channel_id, imported_nodes in group_node_list_by_source_channel_id(imported).items():
            print('   processing source_channel_id '+source_channel_id)
            imported_aggregates = defaultdict(int)
            for imported_node in imported_nodes:
                snode = get_source_node(imported_node)
                assert is_source(edges, snode.id), 'failed assumption snode is not in edges'
                imported_aggregates[imported_node.kind_id] += 1
            for kind, count in imported_aggregates.items():
                graph['edges'].append((source_channel_id, channel_id, kind, count))
    #
    # thank you; come again...
    return graph



# TEST CHANNEL
test_channel_id = '8f33b2b268b140fb8bbb6fd09ccc6e17'
nodes, edges = extract_nodes_and_edges(test_channel_id)
g8fe33 = get_graph(test_channel_id, nodes, edges)
print(json.dumps(g8fe33))



# CBSE KA Hindi Class 6 to 9 channel_id= 33c467480fe94f24b4797ef829af9ef6
# contains 1391 nodes, of which  99.93% are imported
# imports  1390 nodes of which:
#   1390 imported from channel Khan Academy (हिन्दी, हिंदी) of which:
#      427 are exercises
#      305 are topics
#      658 are videos
small_channel_id = '33c467480fe94f24b4797ef829af9ef6'
nodes, edges = extract_nodes_and_edges(small_channel_id)
g33c46 = get_graph(small_channel_id, nodes, edges)
print(json.dumps(g33c46))




# SIB Foundation channel_id= 55eea6b34a4c481b8b6adee06a882360
# contains 2141 nodes, of which  99.77% are imported
# imports  2136 nodes of which:
#     10 imported from channel African Storybook of which:
#        10 are html5s
#     8 imported from channel Blockly Games of which:
#        7 are html5s
#        1 are topics
#     928 imported from channel CK-12 of which:
#        334 are exercises
#        8 are html5s
#        56 are topics
#        530 are videos
#     225 imported from channel Foundation 1 of which:
#        225 are videos
#     212 imported from channel Foundation 3 Literacy of which:
#        26 are documents
#        1 are topics
#        185 are videos
#     13 imported from channel Foundation 3 Numeracy of which:
#        2 are topics
#        11 are videos
#     477 imported from channel Nal'ibali Web Resource Tree of which:
#        466 are html5s
#        11 are topics
#     17 imported from channel Pratham Books' StoryWeaver of which:
#        17 are documents
#     76 imported from channel Thoughtful Learning of which:
#        68 are html5s
#        8 are topics
#     170 imported from channel UNKNOWN NAME of which:
#        11 are topics
#        159 are videos

large_channel_id = '55eea6b34a4c481b8b6adee06a882360'
nodes, edges = extract_nodes_and_edges(large_channel_id)
g55ee = get_graph(large_channel_id, nodes, edges)
g55ee['description'] = 'Content imported from AS, Blockly games, Foundatin 1 3 , Pratham, and UKNOWN'
print(json.dumps(g55ee))















# DEBUG CODE
################################################################################

def print_node_info(node, msg=''):
    print(msg)
    print('Node:', 'studio_id='+node.id, 'node_id='+node.node_id, node.title, '('+node.kind_id+')', 'in channel_id='+node.get_channel().id)
    print('      source_channel_id='+node.source_channel_id,
             ',  source_node_id='+node.source_node_id)   
    print('      original_channel_id='+node.original_channel_id,
             ',  original_node_id='+node.original_node_id,
             ',  original_source_node_id='+node.original_source_node_id)
    print('')

# 
# Derivative node:
# Node: studio_id=6e4292e5194a4f4dae3e8e814616a6e7 node_id=ab06de465b8a42aa81ebf4b22c2ca7da Intro to theoretical probability (video) in channel_id=8f33b2b268b140fb8bbb6fd09ccc6e17
#       source_channel_id=d2579f2f62404c32a4791f4311371d0d ,  source_node_id=d0947c31cc4c497b8a99a704a48c79d0
#       original_channel_id=1ceff53605e55bef987d88e0908658c5 ,  original_node_id=02bea4efecbb4baeb6afa4752065ee22 ,  original_source_node_id=655296e4ef4b51efbc57d18028114db5
# 
# >>> snode = get_source_node(dnode)
# >>> print_node_info(snode, 'Source node:')
# Source node:
# Node: studio_id=0617e9e5f1174c47ac7325e67547f1d1 node_id=d0947c31cc4c497b8a99a704a48c79d0 Intro to theoretical probability (video) in channel_id=d2579f2f62404c32a4791f4311371d0d
#       source_channel_id=1ceff53605e55bef987d88e0908658c5 ,  source_node_id=655296e4ef4b51efbc57d18028114db5
#       original_channel_id=1ceff53605e55bef987d88e0908658c5 ,  original_node_id=02bea4efecbb4baeb6afa4752065ee22 ,  original_source_node_id=655296e4ef4b51efbc57d18028114db5
# 
# >>> onode = get_source_node(snode)
# >>> print_node_info(oonode, 'Original node:')
# Original node:
# Node: studio_id=02bea4efecbb4baeb6afa4752065ee22 node_id=655296e4ef4b51efbc57d18028114db5 Intro to theoretical probability (video) in channel_id=1ceff53605e55bef987d88e0908658c5
#       source_channel_id=1ceff53605e55bef987d88e0908658c5 ,  source_node_id=655296e4ef4b51efbc57d18028114db5
#       original_channel_id=1ceff53605e55bef987d88e0908658c5 ,  original_node_id=02bea4efecbb4baeb6afa4752065ee22 ,  original_source_node_id=655296e4ef4b51efbc57d18028114db5
# 

def group_node_list_by_channel_id(node_list):
    results = defaultdict(list)
    for node in node_list:
        channel_id = node.get_channel().id
        results[channel_id].append(node)
    return results


def get_node_by_studio_id(studio_id):
    for node_list in nodes.values():
        if studio_id in node_list:
            return node_list[studio_id]
    return None



provenance_test_channel = Channel.objects.get(id='8f33b2b268b140fb8bbb6fd09ccc6e17')
dtopic = provenance_test_channel.main_tree.children.get(title='Basic theoretical probability')
# dnode = dtopic.children.all()[0]


# 
# print_node_info(dnode, 'Derivative node:')
# snode = get_source_node(dnode)
# print_node_info(snode, 'Source node:')
# onode = get_source_node(snode)
# print_node_info(oonode, 'Original node:')

