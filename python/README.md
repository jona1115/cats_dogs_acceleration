# Python code for running inference of the catdog model

Important files (aka files I made):
- catdog_inference.py
- catdog_inference_w_custom_conv24.py
- run_conv2d_24.cpp
- utils.h
- catdog_inference_w_custom_conv24_1000_runs.py
- catdog_inference_w_custom_conv24_1000_runs_tflite.py

Note:
- This is a continuation of the [Kaggle Dogs vs Cats project](https://www.kaggle.com/c/dogs-vs-cats/data).
- To prepare the dataset, and create the model, follow [this Vitis-AI tutorial](https://github.com/Xilinx/Vitis-AI-Tutorials/blob/1.4/Design_Tutorials/08-tf2_flow/README.md)
- The Vitis-AI tutorial is trying to demo using the DPU IP in a ZCU102, which I am too poor to buy, so my project is on running this model on my Xilinx Kria KV260.

***
# How to run?
Note: I am using a nonprebuilt version of Vitis-AI (Xilinx/vitis-ai-tensorflow2-gpu:3.5.0.001-b2b227921). I suggest following [this tutorial](https://xilinx.github.io/Vitis-AI/3.5/html/docs/install/install.html) to install it. When I did it, I followed [Option 2: Build the Docker Container from Xilinx Recipes](https://xilinx.github.io/Vitis-AI/3.5/html/docs/install/install.html#option-2-build-the-docker-container-from-xilinx-recipes).
1. Build the container mentioned above ^^^.
2. Start the Vitis-AI container: `sudo ./docker_run.sh xilinx/vitis-ai-tensorflow2-gpu:3.5.0.001-b2b227921`
3. Run `catdog_inference.py` to verify that your environment is set up correctly (it should be).
4. Walah!
