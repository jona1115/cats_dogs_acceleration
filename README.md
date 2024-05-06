# Cats Dogs Acceleration

Hardware Accelerators for Machine Learning have always fascinated me. In this project, I want to try different things to accelerate an ML model. I chose to use the [Kaggle Dogs vs Cats project](https://www.kaggle.com/c/dogs-vs-cats/data).

Goal of this project:
1. Obtain the model and create the Python inference code to run the inference.
2. Pick a layer in the model and, write a C++ implementation of that layer, and use that code when running inference.
3. Use VHDL to write an accelerator for that layer.
4. Try turning the model into a xmodel and running it on my Kria board's DPU.

There are several parts in this project:
1. Python code: /python/
2. VHDL IP: /VHDL/
3. Other coming soon...

Current Progress:
| Date | Progress |
| --- | --- |
| 3/28/2024 | Followed Vitis-AI tutorial and trained the model |
| 5/5/2024 | Created inference code that uses custom c++ layer implementation |
