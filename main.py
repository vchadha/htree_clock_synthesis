import sys
import math

#
# Globals
#
TRIM_TREE = True
LOCALIZED_TREE = True
TREE_DEPTH = 3
SKEW_DIFF = 7
INSERTION_DIST = 30000

SLEW_LIMIT = 0
CAP_LIMIT = 0

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

def get_cap( node ):
    return node[3]

def get_wire_length( p1, p2 ):
    return dist( p1, p2 )

def get_delay( wire, length, load_cap ):
    # delay = r0 l (0.5 c0 l + Cload)
    return wire[1] * length * ( 0.5 * wire[2] * length + load_cap )

def get_wires_to_node( node, wires ):
    wires_to_node = []
    for wire in wires:
        if wire[1] == node:
            wires_to_node.append( wire )
    
    return wires_to_node

def get_wires_from_node( node, wires ):
    wires_from_node = []
    for wire in wires:
        if wire[0] == node:
            wires_from_node.append( wire )

    return wires_from_node

def get_leaves( wires ):
    leaves = []
    
    from_nodes = []
    to_nodes = []

    for wire in wires:
        from_nodes.append( wire[0] )
        to_nodes.append( wire[1] )

    leaves = list( set( to_nodes ) - set( from_nodes ) - set( [0] ) )
    return leaves

def get_sink_node( name, sink_nodes, sinks ):
    sink_name = None
    for node in sink_nodes:
        if name == node[0]:
            sink_name = node[1]
            break

    for sink in sinks:
        if sink[0] == sink_name:
            return sink

    return None

def get_node_loc( name, nodes, sink_nodes, sinks ):
    for node in nodes:
        if node[0] == name:
            return node[1], node[2]

    for node in sink_nodes:
        if node[0] == name:
            for sink in sinks:
                if node[1] == sink[0]:
                    return sink[1], sink[2]

    return -1, -1

def get_node( name, nodes, sink_nodes, sinks ):
    for node in nodes:
        if node[0] == name:
            return node

    for node in sink_nodes:
        if node[0] == name:
            for sink in sinks:
                if node[1] == sink[0]:
                    return sink

    return None

def is_valid_location( point, blockages ):
    for blockage in blockages:
        if point[0] >= blockage[0] and point[0] <= blockage[2]:
            if point[1] >= blockage[1] and point[1] <= blockage[3]:
                return False
    
    return True

def is_valid_point( point, start_point, end_point, vertical ):
    if vertical:
        if start_point[2] > end_point[2]:
            return point[1] > end_point[2]
        else:
            return point[1] < end_point[2]
    else:
        if start_point[1] > end_point[1]:
            return point[0] > end_point[1]
        else:
            return point[0] < end_point[1]
    
    return False

def get_feasible_insertion_points( node1, node2, dist, blockages ):
    points = []
    vertical = node1[1] == node2[1] # X values are the same so we climb y

    curr_point = [ node2[1], node2[2] ]
    stopping_val = node1[2]

    if vertical:
        if node2[2] > node1[2]:
            dist *= -1

        curr_point[1] += dist
    else:
        if node2[1] > node1[1]:
            dist *= -1

        stopping_val = node1[1]
        curr_point[0] += dist

    while is_valid_point( curr_point, node2, node1, vertical ):
        if is_valid_location( curr_point, blockages ):
            points.append( curr_point )

        if vertical:
            curr_point = [curr_point[0], curr_point[1] + dist]
        else:
            curr_point = [curr_point[0] + dist, curr_point[1]]

    return points

def get_wire_cap( wire_lib ):
    return wire_lib[get_wire_type( wire_lib )][2]

def get_wire_resistence( wire_lib ):
    return wire_lib[get_wire_type( wire_lib )][1]

def get_buffer_cap( buf_lib ):
    return buf_lib[get_buffer_type( buf_lib )][3]

def prune_options( options ):
    return options

def _insert_buffers( source_node, wires, buffers, sink_nodes, nodes, blockages, sinks ):
    # option = (to node, x, y, slew, cap, delay, RAQ, skew, inv_cnt, buffer?, ( type, ptr ))
    # type = 0 - single, 1 - branch ( 1, (to_node, ptr), (to_node, ptr) )
    options = []
    
    # each node has a list of options (when we get to root, we have one node and a final list of options)
    leaves = get_leaves( wires )
    nodes_to_analyze = leaves

    buffer_dist = INSERTION_DIST
    
    while ( True ):
        print(nodes_to_analyze, len( options ))
        wires_to_analyze = []
        for node in nodes_to_analyze:
            wires_to_analyze += get_wires_to_node( node, wires )

            x, y = get_node_loc( node, nodes, sink_nodes, sinks )
            complete_node = [node, x, y]


            # Add initial option
            # At sink: option = (node, x, y, 0, Cs, 0, 0, 0, [0], 0, (0, None))
            if is_sink( node, sink_nodes ) or node in leaves:
                _type = 0
                cap = 0
                if is_sink( node, sink_nodes ):
                    cap = get_cap( get_sink_node( node, sink_nodes, sinks ) )
                option = ( node, x, y, 0, cap, 0, 0, 0, [0], 0, ( _type, None ) )
                options.append( option )

            # Multiple branches
            elif len( get_wires_from_node( node, wires ) ) > 1:
                # Wires from node
                wires_from_node = get_wires_from_node( node, wires )

                # Get all options with to node
                merge_options = [ [] for _ in range( len( wires_from_node ) ) ]
                for i in range( len( wires_from_node ) ):
                    for j in range( len( options ) - 1, -1, -1 ):
                        if options[j][0] == wires_from_node[i][1]:
                            merge_options[i].append( options.pop( j ) )
                
                print('merge banch: ', len(merge_options))
                all_combinations = [ (op1, op2) for op1 in merge_options[0] for op2 in merge_options[1] ]
                for combination in all_combinations:
                    op1 = combination[0]
                    op2 = combination[1]
                    # Create option
                    slew = 0
                    if op2[3] > op1[3]:
                        wire = wire_lib[get_wire_type( wire_lib )]
                        length = dist( complete_node, op2 )
                        load_cap = get_wire_cap( wire_lib )
                        slew = op2[3] + math.log( 9 ) * get_delay( wire, length, load_cap )
                    else:
                        wire = wire_lib[get_wire_type( wire_lib )]
                        length = dist( complete_node, op1 )
                        load_cap = get_wire_cap( wire_lib )

                        slew = op1[3] + math.log( 9 ) * get_delay( wire, length, load_cap )

                    cap = op1[4] + op2[4]

                    delay = 0
                    if op2[5] > op1[5]:
                        wire = wire_lib[get_wire_type( wire_lib )]
                        length = dist( complete_node, op2 )
                        load_cap = get_wire_cap( wire_lib )
                        delay = op2[5] + get_delay( wire, length, load_cap )
                    else:
                        wire = wire_lib[get_wire_type( wire_lib )]
                        length = dist( complete_node, op1 )
                        load_cap = get_wire_cap( wire_lib )
                        delay = op1[5] + get_delay( wire, length, load_cap )

                    # TODO: do I want RAQ?
                    raq = 0

                    # TODO: this should be diff in delay right?
                    skew = abs( op1[7] - op2[7] )
                    invt_cnt = op1[8] + op2[8]

                    temp_option = ( node, x, y, slew, cap, delay, raq, skew, invt_cnt, 0, ( 1, ( ( op1[0], op1 ), ( op2[0], op2 ) ) ) )

                    # If option is valid, add to option lists
                    if temp_option[3] < SLEW_LIMIT and temp_option[4] < CAP_LIMIT and temp_option[7] < SKEW_DIFF:
                        options.append( temp_option )

            # Single branch
            else:
                wires_from_node = get_wires_from_node( node, wires )

                options_to_check = []
                for i in range( len( wires_from_node ) ):
                    for j in range( len( options ) - 1, -1, -1 ):
                        if options[j][0] == wires_from_node[i][1]:
                            options_to_check.append( options.pop( j ) )

                print('single branch: ', len(options_to_check))
                for option in options_to_check:
                    # Create option
                    cap = option[4] + get_wire_cap( wire_lib ) * dist( complete_node, option )

                    wire = wire_lib[get_wire_type( wire_lib )]
                    length = dist( complete_node, option )
                    load_cap = get_wire_cap( wire_lib )
                    delay = option[5] + get_delay( wire, length, load_cap )

                    slew = math.log( 9 ) * get_delay( wire, length, load_cap )

                    # TODO: do I want raq
                    raq = 0

                    # TODO: I feel like skew is wrong
                    skew = option[7]
                    invt_cnt = option[8]

                    temp_option = ( node, x, y, slew, cap, delay, raq, skew, invt_cnt, 0, ( 0, option ) )

                    # if option is valid add to options list
                    if temp_option[3] < SLEW_LIMIT and temp_option[4] < CAP_LIMIT:
                        options.append( temp_option )

        # Remove all nodes
        nodes_to_analyze = []

        # Prune options
        options = prune_options( options )

        print('Start part 2 - traversal')

        # Reached root node
        if len( wires_to_analyze ) == 0:
            break

        # Get wire to check for insertion points
        for wire_to_analyze in wires_to_analyze:
            # Add from node
            if wire_to_analyze[0] not in nodes_to_analyze:
                nodes_to_analyze.append( wire_to_analyze[0] )

            # Get options that wire points to so we can create new options from it
            curr_options = []
            for i in range( len( options ) - 1, -1, -1 ):
                if options[i][0] == wire_to_analyze[1]:
                    curr_options.append( options.pop( i ) )

            # Get insertion points
            from_node = get_node( wire_to_analyze[0], nodes, sink_nodes, sinks )
            to_node = get_node( wire_to_analyze[1], nodes, sink_nodes, sinks )

            wire_length = get_wire_length( from_node, to_node )
            if wire_length > 70000:
                buffer_dist = wire_length / 10            
            insertion_points = get_feasible_insertion_points( from_node, to_node, buffer_dist, blockages )
            print('insertion points: ', len(insertion_points))

            # Iterate over insertion points
            for point in insertion_points:
                new_options = []
                for option in curr_options:
                    # Generate new options at point
                    
                    cap = option[4] + get_wire_cap( wire_lib ) * dist( [0, point[0], point[1]], option )
                    
                    wire = wire_lib[get_wire_type( wire_lib )]
                    length = dist( [0, point[0], point[1]], option )
                    load_cap = get_wire_cap( wire_lib )
                    delay = option[5] + get_delay( wire, length, load_cap )

                    slew = math.log( 9 ) * get_delay( wire, length, load_cap )

                    # TODO: do I want raq?
                    raq = 0

                    # I feel like skew is wrong
                    skew = option[7]
                    invt_cnt = option[8]

                    temp_option1 = ( option[0], point[0], point[1], slew, cap, delay, raq, skew, invt_cnt, 0, ( 0, option ) )

                    buf_cap = get_buffer_cap( buf_lib )
                    new_invt_cnt = []
                    for cnt in invt_cnt:
                        new_invt_cnt.append( cnt + 1 )
                    # TODO: add delay of buffer
                    temp_option2 = ( option[0], point[0], point[1], slew, buf_cap, delay, raq, skew, new_invt_cnt, 1, ( 0, option ) )
                    
                    # Check if options are valid
                    if temp_option1[3] < SLEW_LIMIT and temp_option1[4] < CAP_LIMIT:
                        new_options.append( temp_option1 )
                    
                    if temp_option2[3] < SLEW_LIMIT and temp_option2[4] < CAP_LIMIT:
                        new_options.append( temp_option2 )

                # TODO: do I want to prune here too?
                new_options = prune_options( new_options )
                curr_options = new_options

            for option in curr_options:
                options.append( option )

            options = prune_options( options )


    print( options[0] )
    # TODO: also prune those where RAQ and c are bad (same as buffer insertion time!)

    # TODO: at root remove all with odd inverter cnt
    # TODO: pick best candidate and then add nodes and buffers and update wires

def insert_buffers( source_node, wires, buffers, sink_nodes, nodes, blockages, sinks ):    
    best_option = _insert_buffers( source_node, wires, buffers, sink_nodes, nodes, blockages, sinks )

    # TODO: start from scratch and remake wires nodes buffers etc

    return nodes, wires, buffers

# TODO: h-tree uniform trim and nontrim, non-uniform trim and nontrim
def synthesize( layout, source, sinks, wire_lib, buf_lib, vdd_sim, slew_limit, cap_limit, blockages ):
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
        nodes, wires, buffers = trim_tree( source_node, wires, buffers, sink_nodes, nodes )

    # Insert buffers
    nodes, wires, buffers = insert_buffers( source_node, wires, buffers, sink_nodes, nodes, blockages, sinks )

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
    layout, source, sinks, wire_lib, buf_lib, vdd_sim, slew_limit, cap_limit, blockages = parse_input( input_file )
    SLEW_LIMIT = slew_limit
    CAP_LIMIT = cap_limit

    # Synthesize clock
    source_node, nodes, sink_nodes, wires, buffers = synthesize( layout, source, sinks, wire_lib, buf_lib, vdd_sim, slew_limit, cap_limit, blockages )

    # Write output
    write_out( output_file, source_node, nodes, sink_nodes, wires, buffers )
