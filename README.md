# README

Welcome to the Leptophobic Z' Cascade decay to Anomalon's plotting and final analysis scripts. This analysis uses [Recursive Jigsaw Reconstruction](https://arxiv.org/abs/1705.10733).

## Use of RestFrames, the package that computes Jigsaw Variables

We use the software package [RestFrames](http://restframes.com/) developed by Christopher Rogan to compute the jigsaw variables. The package runs natively through C++, but we currently run RestFrames wrapped in python. This README will provide the steps necessary to access both modes of operations.

### Setting up RestFrames

First, install RestFrames as directed in the [Downloads](http://restframes.com/downloads/) section of the RestFrames documentation. The following directions (taken from the aforementioned link) worked out of the box for Ubuntu 18.04 for installing RestFrames in a specific directory.

`$ git clone https://github.com/crogan/RestFrames RestFrames`
`$ ./configure --prefix=your_path_here`