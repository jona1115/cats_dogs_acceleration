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

Important:
- If you are following on and trying this project on your own, do note that this folder probably won't work, if you were to follow along, I suggest starting with Vitis-AI's tutorial, and coping the "important files" into the project.
- I am using a non prebuilt version of Vitis-AI (xilinx/vitis-ai-tensorflow2-gpu:3.5.0.001-b2b227921). I suggest following [this tutorial](https://xilinx.github.io/Vitis-AI/3.5/html/docs/install/install.html) to install it, when I did it, I followed [Option 2: Build the Docker Container from Xilinx Recipes](https://xilinx.github.io/Vitis-AI/3.5/html/docs/install/install.html#option-2-build-the-docker-container-from-xilinx-recipes).
