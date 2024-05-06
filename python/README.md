# Python code for running inference of the catdog model

Important files (aka files I made):
- catdog_inference.py
- catdog_inference_w_custom_conv24.py
- run_conv2d_24.cpp
- utils.h

Note:
- This is a continuation of the [Kaggle Dogs vs Cats project](https://www.kaggle.com/c/dogs-vs-cats/data).
- To prepare the dataset, and create the model, follow [this Vitis-AI tutorial](https://github.com/Xilinx/Vitis-AI-Tutorials/blob/1.4/Design_Tutorials/08-tf2_flow/README.md)
- The Vitis-AI tutorial is trying to demo using the DPU IP in a ZCU102, which I am too poor to buy, so my project is on running this model on my Xilinx Kria KV260.
