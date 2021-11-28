import sys
from PIL import Image, ImageDraw

def parse_input( input_file, output_file ):
    layout = []

    source = []
    nodes = []
    sinks = []
    wires = []
    buffers = []

    with open( input_file, 'r' ) as file:
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

    with open( output_file, 'r' ) as file:
        # Node name, source name
        source_node = file.readline().split()
        source[0] = int( source_node[1] )

        # Node name, x, y
        num_nodes = int( file.readline().split()[2] )
        for i in range( num_nodes ):
            node = file.readline().split()
            node[0] = int( node[0] )
            node[1] = int( node[1] )
            node[2] = int( node[2] )
            nodes.append( node )

        # Node name, sink name
        num_sinks = int( file.readline().split()[2] )
        for i in range( num_sinks ):
            sink_node = file.readline().split()[0]
            sinks[i][0] = int(sink_node)

        # From node, to node, wire type
        num_wires = int( file.readline().split()[2] )
        for i in range( num_wires ):
            wire = file.readline().split()
            wire[0] = int( wire[0] )
            wire[1] = int( wire[1] )
            wire[2] = int( wire[2] )
            wires.append( wire )

        # From node, to node, buffer type
        num_buffers = int( file.readline().split()[2] )
        for i in range( num_buffers ):
            buffer = file.readline().split()
            buffer[0] = int( buffer[0] )
            buffer[1] = int( buffer[1] )
            buffer[2] = int( buffer[2] )
            buffers.append( buffer )

    return ( layout, source, nodes, sinks, wires, buffers )

def get_node( name, nodes, sinks, source ):
    if name == source[0]:
        return ( source )

    for node in nodes:
        if node[0] == name:
            return ( node )

    for sink in sinks:
        if sink[0] == name:
            return ( sink )

    return None

if __name__ == '__main__':

    # Check cmd line args
    if ( len( sys.argv ) < 3 ):
        print( 'python main.py [INPUT_FILE] [OUTPUT_FILE]\n' )
        exit( 1 )

    # Get input file name
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Parse input
    layout, source, nodes, sinks, wires, buffers = parse_input( input_file, output_file )
    
    # Create blank image
    scale = 10e-4
    image = Image.new( 'RGB', ( int( layout[2] * scale ), int( layout[3] * scale ) ), ( 255, 255, 255 ) )

    # Draw time
    draw = ImageDraw.Draw( image )

    # Draw source
    width = 30
    draw.ellipse((source[1] * scale - width, source[2] * scale - width, source[1] * scale + width, source[2] * scale + width), fill='blue', outline='blue')

    # Draw wires
    for wire in wires:
        node1 = get_node( wire[0], nodes, sinks, source )
        node2 = get_node( wire[1], nodes, sinks, source )
        
        if node1 and node2:
            draw.line((node1[1] * scale, node1[2] * scale, node2[1] * scale, node2[2] * scale), fill=(0, 0, 0), width=7)

    # Draw sinks
    for sink in sinks:
        width = 30
        draw.ellipse((sink[1] * scale - width, sink[2] * scale - width, sink[1] * scale + width, sink[2] * scale + width), fill='red', outline='red')

    # Draw buffers
    for buffer in buffers:
        node1 = get_node( buffer[0], nodes, sinks, source )
        node2 = get_node( buffer[1], nodes, sinks, source )
        width = 20
        
        if node1 and node2:
            draw.rectangle((node1[1] * scale - width, node1[2] * scale - width, node2[1] * scale + width, node2[2] * scale + width), fill='green', outline='green')

    # Show image
    image.save( 'test.png' )
