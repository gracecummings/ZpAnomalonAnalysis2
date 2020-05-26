# README

Welcome to the Leptophobic Z' Cascade decay to Anomalon's plotting and final analysis scripts. This analysis uses [Recursive Jigsaw Reconstruction](https://arxiv.org/abs/1705.10733).

## Use of RestFrames, the package that computes Jigsaw Variables

We use the software package [RestFrames](http://restframes.com/) developed by Christopher Rogan to compute the jigsaw variables. The package runs natively through C++, but we currently run RestFrames wrapped in python. 

### Setting up RestFrames

First, install RestFrames as directed in the [Downloads](http://restframes.com/downloads/) section of the RestFrames documentation. The following directions (taken from the aforementioned link) worked out of the box for Ubuntu 18.04 for installing RestFrames in a specific directory. Further details are provided on the RestFrames instuctions page.

```

$ git clone https://github.com/crogan/RestFrames RestFrames
$ ./configure --prefix=your_path_here
$ make
$ make install

```

### Running Recursive Jigsaw calculations

In the RestFrames documentation, one learns that RestFrames can be run from the ROOT command line, or as compiled macros. This README will only address how to run our python wrapped examples. RestFrames has copious examples included, each detailed in their [Examples Documentation](http://restframes.com/examples/). Here you can compare your desired decay tree to RestFrames development team varified examples. All the examples from the paper are also included.

In the same directory as you installed RestFrames, you can run everything in this (ZpAnomalonAnalysis2) repository. In the future, I will combine all of these steps into one streamlined git clone.

If you do not want to Download my entire framework, but still want to try the python wrapped Jigsaw as a standalone, you only need the `example_H_to_WlnuWlnu.py` file. This examples uses the same Jigsaw Rules as the Leptophobic Z' cascade to Anomalons and SM bosons.

#### Running H to WlnuWlnu example

This is a wrapper written by B. Hirosky for the H to Wlnu Wlnu example. Tested for both Python3 and Python2.7. To run, 

```

$ source setup_RestFrames.sh #if bash, other setup files are included
$ python example_H_to_WlnuWlnu.py

```

This example generates H to WlnuWlnu events, will produce plots showing the Jigsaw mass estimators for the H, and an output ROOT file.

