# Thin Layer Chromatography (TLC) Viewer and Analyzer
See the original c# version : https://github.com/danammeansbear/OpenTLC
## Overview

This project is an open-source Python-based tool designed to perform Thin Layer Chromatography (TLC) analysis with the same precision and accuracy as High-Performance Thin Layer Chromatography (HPTLC). The tool provides a comprehensive platform for visualizing and analyzing TLC plates, particularly useful in the screening of medicinal cannabinoids. It offers the convenience of smartphone integration for quantitative evaluation of chromatographic analyses.


## Abstract

Quantification of cannabinoids with computational assessment of natural products thin-layer chromatography (canTLC)

A. Dabdoub*, Land Grant Program, Central State University, Wilberforce, OH 45384; C. Schluttenhofer, Agriculture Research Development Program, Central State University, Wilberforce, OH 45384

For the last 100 years Cannabis sativa has been classified depending on whos growing it, the purpose and the views of those in power.In recent years since the legalization of Hemp, Measuring THC and other compounds within the plant are necessary to separate it from a legal and non legal plant. One Testing method used to detect cannabinoids like THC and CBD and keep hemp farmers in compliance is thin-layer chromatography (TLC). A major challenge with TLC has been the human interpretation of these testing results. Recent work using Artificial Intelligence and Computers has substantially improved the testing ability of TLC. This work evaluates the use of Computer Image Processing and Machine learning on TLC for the detection of chemicals, creates a standard for the range of colors in these test, and the detection of chemical cannabis compounds. Standard testing methods and equipment can have a equipment cost starting at $35,000, creating a cost to entry barrier for the scientific community, farmers and Researchers. There is also problems with farmers needing to use copious amounts of product which could be saved if they had a way to test themselves. This Problem led to the creation of an opensource software developed by my professor and I. The application, computational assessment of natural products TLC (canTLC), determines color value, color intensity, and size of spots based on custom and free-to-use software. To make sure it was working and accurate, known concentrations were used to devise a standard curve for quantification of spots based on intensity and size. Unknown samples analyzed with canTLC were comparable with the standards in testing these chemical compounds. Observations indicate standardization of human and digital systems are needed to further fine-tune the methodology. The in-house software with an open source application is available for public download.

Topic Area: Plant Health and Production and Plant Products currently cant work on this, would love some help.

All this said. This has been an amazing ride.

Thanks everyone for their ever growing support all those years.

Let's keep in touch,

## Features

- **High Precision Analysis**: Achieve results comparable to HPTLC.
- **Smartphone Integration**: Use your smartphone camera to capture TLC plates and perform quantitative analysis.
- **Automated Analysis**: Automatic detection and quantification of analyte spots.
- **User-Friendly Interface**: Easy-to-use graphical interface for visualizing TLC results.
- **Real-time Data Processing**: Analyze TLC results in real-time using your smartphone.
- **Open Source**: Fully customizable and extendable for specific research needs.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or higher
- NumPy
- OpenCV
- Matplotlib
- Flask (for optional web-based interface)
- PIL (Python Imaging Library)
- TensorFlow (for optional advanced image processing and machine learning tasks)
- Your smartphone's camera (for capturing TLC plates)

### Usage

Capturing Images:

Use your smartphone camera to capture a clear image of the TLC plate.
Ensure consistent lighting and minimal reflection for best results.
Image Upload:

Upload the image to the tool via the graphical user interface (GUI) or the web interface.


Analysis:

The tool will automatically detect the spots on the TLC plate.
Quantitative analysis will be performed, providing data on the concentration of each analyte.



Visualization:

View the results in the GUI or export them as a CSV or image file.
Generate visual reports that can be used for further research or documentation.
