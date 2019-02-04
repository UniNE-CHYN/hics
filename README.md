# Hyperspectral Imaging Control System

This software, `hics` (Hyperspectral Imaging Control System), is a tool to control a push-broom hyperspectral camera system. Such a system usually consists in a camera and a scanner.

It currently contain the code to support a SPECIM SWIR camera, and SPECIM AisaKestrel 10 cameras. It is also possible to run a simulator if no hardware is present.

## Requirements

* Python 3
* A redis server
* Redis Python 3 bindings
* PyQt4
* Numpy, Scipy, Matplotlib


## Installation

```
git clone https://github.com/UniNE-CHYN/hics
cd hics
pip3 install -e .
```

## Usage

A [short manual](../blob/master/softwaremanual.pdf) is provided.

## Licence

LGPL v3

## Support

This is a research project, and is provided as-is with the hope that it will be useful, so no support can be expected. However, I will try if possible to answer any questions.

## Contributing

Contribution are welcome, please submit them as pull requests.
