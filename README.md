# H-Tree Clock Synthesis

## Requisites
- Python3
- Input netlist is of ISPD2009 contest format
- Output netlist is produced to follow ISPD2009 contest format

## Files
- main.py
    - contains main functionality for generating clock tree
    - `python main.py <input_netlist> <output_netlist>`
    - creates output netlist file according to ISPD2009 contest format
    - you can then use the output file with the ISPD2009 evaluation script
        - `./eval2009.pl <input_netlist> <output_netlist> tunned_45nm_hp.pm`
    - this file is controlled by global booleans at the top of the file
        - `GENERATE_ALL_TREES` generates all posible combinations of trees
            - localized, central with full and trimmed versions of both
        - `INSERT_BUFFERS` controls whether buffers are inserted or not
        - `TRIM_TREE` controls whether the tree is trimmed ie. remove all
          wires not connected to sink nodes
        - `LOCALIZED_TREE` controls whether the tree is generated with
          localized or centralized style
        - `TREE_DEPTH` controls depth of H-tree
        - `SKEW_DIFF` controls max difference in skew for options when
          merging
        - `SAMPLING_AMT` controls how big the option pool will get before
          sampling takes place
        - `INSERTION_POINTS` controls how many points can be inserted on a
          wire
- view.py
    - contains functionality to visualize a clock tree
    - `python view.py <input_netlist> <output_netlist>`
    - generates a png file called `temp.png`

## How to use

To generate clock tree:
`python main.py <input_netlist> <output_netlist>`

To visualize clock tree:
`python view.py <input_netlist> <output_netlist>`

To run with ISPD2009 contest evaluation script:
`./eval2009.pl <input_netlist> <output_netlist> tuned_45nm_hp.pm`

