import sys
import math

#
# Globals
#
TRIM_TREE = True
LOCALIZED_TREE = True
TREE_DEPTH = 3

def parse_input( file_name ):
    layout = []
    source = []

    vdd_sim = []
    slew_limit = 0
    cap_limit = 0
    blockages = []

    sinks = []
    wire_lib = []
    buf_lib = []

    with open( file_name, 'r' ) as file:
        # lower left x, y, upper right x, y
        layout = file.readline().split()
        layout = [ int( val ) for val in layout ]

        # Source name, x, y, buffer name
        source = file.readline().split()[1:]
        source = [ int( val ) for val in source ]

        # Sinks [name, x, y, load cap fF]
        num_sinks = int( file.readline().split()[2] )
        for i in range( num_sinks ):
            sink = file.readline().split()
            sink[0] = int( sink[0] )
            sink[1] = int( sink[1] )
            sink[2] = int( sink[2] )
            sink[3] = float( sink[3] )
            sinks.append( sink )

        # Wire lib [name, unit R (Ohm/nm), unit C (fF/nm)]
        num_wires = int( file.readline().split()[2] )
        for i in range( num_wires ):
            wire = file.readline().split()
            wire = [ float( val ) for val in wire ]
            wire[0] = int( wire[0] )
            wire_lib.append( wire )

        # Buffer lib [id, spice file, inverted?, input load cap, output
        # parasitics, output resistance]
        num_buffers = int( file.readline().split()[2] )
        for i in range( num_buffers ):
            buffer = file.readline().split()
            buffer[0] = int( buffer[0] )
            buffer[2] = int( buffer[2] )
            buffer[3] = float( buffer[3] )
            buffer[4] = float( buffer[4] )
            buffer[5] = float( buffer[5] )
            buf_lib.append( buffer )

        # Vdd sim settings
        vdd_sim = file.readline().split()[2:]
        vdd_sim = [ float( val ) for val in vdd_sim ]

        # Slew and capacitance limit
        slew_limit = float( file.readline().split()[2] )
        cap_limit = float( file.readline().split()[2] )

        # Blockages [lower left x, y, upper right x, y]
        num_blockages = int( file.readline().split()[2] )
        for i in range( num_blockages ):
            blockage = file.readline().split()
            blockage = [ int( val ) for val in blockage ]
            blockages.append( blockage )

    return ( layout, source, sinks, wire_lib, buf_lib, vdd_sim, slew_limit, cap_limit, blockages )

def write_out( file_name, source, nodes, sinks, wires, buffers ):
    with open( file_name, 'w' ) as outfile:
        # Node name, source name
        outfile.write( 'sourcenode {} {}\n'.format( source[0], source[1] ) )

        outfile.write( 'num node {}\n'.format( len( nodes ) ) )
        for node in nodes:
            # node name, x, y
            outfile.write( '{} {} {}\n'.format( node[0], node[1], node[2] ) )

        outfile.write( 'num sinknode {}\n'.format( len( sinks ) ) )
        for sink in sinks:
            # Node name, sink name
            outfile.write( '{} {}\n'.format( sink[0], sink[1] ) )

        outfile.write( 'num wire {}\n'.format( len( wires ) ) )
        for wire in wires:
            # From node name, to node name, wire type
            outfile.write( '{} {} {}\n'.format( wire[0], wire[1], wire[2] ) )

        outfile.write( 'num buffer {}\n'.format( len( buffers ) ) )
        for buffer in buffers:
            # From node name, to node name, buffer type
            outfile.write( '{} {} {}\n'.format( buffer[0], buffer[1], buffer[2] ) )

def get_wire_type( wire_lib ):
    return ( wire_lib[0][0] )

def get_buffer_type( buf_lib ):
    return ( buf_lib[0][0] )

# TODO: one day make this continue depth until close to sink nodes
def create_htree( center, length, depth, nodes, wires, wire_lib ):
    if ( depth == 0 ):
        return

    node_x0 = int( center[1] - length / 2 )
    node_x1 = int( center[1] + length / 2 )
    node_y0 = int( center[2] - length / 2 )
    node_y1 = int( center[2] + length / 2 )

    # Add nodes and wires
    node_1 = [len( nodes ) + 1, node_x0, node_y0]
    node_2 = [len( nodes ) + 2, node_x0, node_y1]
    node_3 = [len( nodes ) + 3, node_x1, node_y0]
    node_4 = [len( nodes ) + 4, node_x1, node_y1]
    node_5 = [len( nodes ) + 5, node_x0, center[2]]
    node_6 = [len( nodes ) + 6, node_x1, center[2]]
    nodes.append( node_1 )
    nodes.append( node_2 )
    nodes.append( node_3 )
    nodes.append( node_4 )
    nodes.append( node_5 )
    nodes.append( node_6 )

    # 1     3
    # |   6 |
    # |-----|
    # | 5   |
    # 2     4
    wire_1 = [center[0], len( nodes ) - 1, get_wire_type( wire_lib )] # (x, y), (x0, y)
    wire_2 = [center[0], len( nodes ) - 0, get_wire_type( wire_lib )] # (x, y), (x1, y)
    wire_3 = [len( nodes ) - 1, len( nodes ) - 4, get_wire_type( wire_lib )] # (x0, y), (x0, y1)
    wire_4 = [len( nodes ) - 1, len( nodes ) - 5, get_wire_type( wire_lib )] # (x0, y), (x0, y0)
    wire_5 = [len( nodes ) - 0, len( nodes ) - 2, get_wire_type( wire_lib )] # (x1, y), (x1, y1)
    wire_6 = [len( nodes ) - 0, len( nodes ) - 3, get_wire_type( wire_lib )] # (x1, y), (x1, y0)
    wires.append( wire_1 )
    wires.append( wire_2 )
    wires.append( wire_3 )
    wires.append( wire_4 )
    wires.append( wire_5 )
    wires.append( wire_6 )

    # Update length
    # alt version: update length by average
    length = int( length / 2 )
    
    # Call create tree on subtrees
    create_htree( node_1, length, depth - 1, nodes, wires, wire_lib )
    create_htree( node_2, length, depth - 1, nodes, wires, wire_lib )
    create_htree( node_3, length, depth - 1, nodes, wires, wire_lib )
    create_htree( node_4, length, depth - 1, nodes, wires, wire_lib )

def dist( node1, node2 ):
    return abs( node1[1] - node2[1] ) + abs( node1[2] - node2[2] )

def connect_sinks( sinks, nodes, wires, wire_lib ):
    sink_nodes = []

    for sink in sinks:
        closest_node = nodes[0]
        min_dist = dist( sink, closest_node )
        
        for node in nodes:
            node_dist = dist( sink, node )
            if node_dist < min_dist:
                min_dist = node_dist
                closest_node = node
        
        # Connect sink to closest node
        node = [len(nodes) + 1, closest_node[1], sink[2]]
        nodes.append( node )

        sink_node = [len(nodes) + len(sinks), sink[0]]
        sink_nodes.append( sink_node )

        wire_1 = [closest_node[0], node[0], get_wire_type( wire_lib )]
        wire_2 = [node[0], sink_node[0], get_wire_type( wire_lib )]
        wires.append( wire_1 )
        wires.append( wire_2 )

    return ( sink_nodes )

def is_sink( name, sinks ):
    for sink in sinks:
        if ( name == sink[0] ):
            return True

    return False

def trim_tree( source_node, wires, buffers, sink_nodes, nodes ):
    # Get all valid nodes
    connections = []
    for wire in wires:
        connection = [ wire[0], wire[1] ]
        if connection not in connections:
            connections.append( connection )

    for buffer in buffers:
        connection = [ buffer[0], buffer[1] ]
        if connection not in connections:
            connections.append( connection )

    valid_nodes = []
    if ( get_valid_nodes( source_node[0], valid_nodes, connections, sink_nodes ) ):
        valid_nodes.append( source_node[0] )

    # Remove all connections that are not valid
    new_nodes = []
    for node in nodes:
        if node[0] in valid_nodes:
            new_nodes.append( node )

    new_buffers = []
    for buffer in buffers:
        if buffer[0] in valid_nodes and buffer[1] in valid_nodes:
            new_buffers.append( buffer )

    new_wires = []
    for wire in wires:
        if wire[0] in valid_nodes and wire[1] in valid_nodes:
            new_wires.append( wire )

    return new_nodes, new_wires, new_buffers

def get_valid_nodes( curr_node, valid_nodes, connections, sinks ):
    if is_sink( curr_node, sinks ):
        return True

    to_nodes = []
    for connection in connections:
        if connection[0] == curr_node and connection[1] not in to_nodes:
            to_nodes.append( connection[1] )

    return_val = False
    for node in to_nodes:
        if get_valid_nodes( node, valid_nodes, connections, sinks ):
            valid_nodes.append( node )
            return_val = True

    return return_val

def get_center( layout, sinks ):
    if LOCALIZED_TREE:
        avg_x = 0
        avg_y = 0
        for sink in sinks:
            avg_x += sink[1]
            avg_y += sink[2]

        avg_x /= len( sinks )
        avg_y /= len( sinks )

        return [int( avg_x ), int( avg_y )]
    
    return [int( layout[2] / 2 ), int( layout[3] / 2 )]

def get_length( layout, sinks ):
    if LOCALIZED_TREE:
        min_x = layout[2]
        max_x = layout[0]
        min_y = layout[3]
        max_y = layout[1]
        for sink in sinks:
            if sink[1] < min_x:
                min_x = sink[1]
            if sink[1] > max_x:
                max_x = sink[1]
            if sink[2] < min_y:
                min_y = sink[2]
            if sink[2] > max_y:
                max_y = sink[2]

        dx = max_x - min_x
        dy = max_y - min_y
        if dx > dy:
            return ( dx / 2 )
        
        return ( dy / 2 )

    return ( layout[2] / 2 )

# TODO: h-tree uniform trim and nontrim, non-uniform trim and nontrim
def synthesize( layout, source, sinks, wire_lib, buf_lib, vdd_sim, slew_limit, cap_limit, blockage ):
    # Init output data
    source_node = [0, source[0]]
    nodes = []
    sink_nodes = []
    wires = []
    buffers = []
    
    # Compute center of H-Tree (alt version is local center - ie.
    # average x and y of all sinks)
    center = get_center( layout, sinks )

    # Add initial invertor to flip signal
    temp_node = [len( nodes ) + 1, 0, 0]
    nodes.append( temp_node )

    buffer = [source_node[0], len( nodes ), get_buffer_type( buf_lib )]
    buffers.append( buffer )

    # Connect source to H-Tree
    node = [len( nodes ) + 1, center[0], 0]
    nodes.append( node )
    wire = [len( nodes ) - 1, len( nodes ), get_wire_type( wire_lib )]
    wires.append( wire )

    node = [len( nodes ) + 1, center[0], center[1]]
    nodes.append( node )
    wire = [len( nodes ) - 1, len( nodes ), get_wire_type( wire_lib )]
    wires.append( wire )

    # Iteritvely branch tree
    # Set length as static based on layout
    # alt version: use average center
    length = get_length( layout, sinks )
    depth = TREE_DEPTH
    create_htree( node, length, depth, nodes, wires, wire_lib )

    # Connect sinks to closest nodes
    sink_nodes = connect_sinks( sinks, nodes, wires, wire_lib )

    # Trim all branches that are not connected
    if TRIM_TREE:
        nodes, wires, vuffers = trim_tree( source_node, wires, buffers, sink_nodes, nodes )

    # TODO: Insert buffers to solve skew constraints

    return ( source_node, nodes, sink_nodes, wires, buffers )

if __name__ == '__main__':

    # Check cmd line args
    if ( len( sys.argv ) < 3 ):
        print( 'python main.py [INPUT_FILE] [OUTPUT_FILE]\n' )
        exit( 1 )

    # Get input file name
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Parse input
    layout, source, sinks, wire_lib, buf_lib, vdd_sim, slew_limit, cap_limit, blockage = parse_input( input_file )
    
    # Synthesize clock
    source_node, nodes, sink_nodes, wires, buffers = synthesize( layout, source, sinks, wire_lib, buf_lib, vdd_sim, slew_limit, cap_limit, blockage )

    # Write output
    write_out( output_file, source_node, nodes, sink_nodes, wires, buffers )
