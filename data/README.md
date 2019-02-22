
### Sample channel

see sample_channel.json

    # TEST CHANNEL
    nodes, edges = extract_nodes_and_edges('8f33b2b268b140fb8bbb6fd09ccc6e17')
    g8fe33 = get_graph(nodes, edges)
    print(json.dumps(g8fe33))


### small channel

see 33c467480fe94f24b4797ef829af9ef6.json

    # CBSE KA Hindi Class 6 to 9 channel_id= 33c467480fe94f24b4797ef829af9ef6
    # contains 1391 nodes, of which  99.93% are imported
    # imports  1390 nodes of which:
    #   1390 imported from channel Khan Academy (हिन्दी, हिंदी) of which:
    #      427 are exercises
    #      305 are topics
    #      658 are videos
    nodes, edges = extract_nodes_and_edges('33c467480fe94f24b4797ef829af9ef6')
    g33c46 = get_graph(nodes, edges)
    print(json.dumps(g33c46))


### Large diverse channel

see 55eea6b34a4c481b8b6adee06a882360.json

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
    nodes, edges = extract_nodes_and_edges('55eea6b34a4c481b8b6adee06a882360')
    g55ee = get_graph(nodes, edges)
    g55ee['title'] = 'Imports graph for the SIB Foundation channel'
    g55ee['description'] = 'Import content imported from AS, Blockly games, Foundatin 1 3 , Pratham, and UKNOWN'
    print(json.dumps(g55ee))




