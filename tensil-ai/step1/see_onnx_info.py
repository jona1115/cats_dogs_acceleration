import onnx

# Load the ONNX model
model = onnx.load("f_model.onnx")

# Get the graph from the model
graph = model.graph

# Print layer information
for node in graph.node:
    print(f"Layer Name: {node.name}")
    print(f"Layer Type: {node.op_type}")
    print("Inputs: ", [input for input in node.input])
    print("Outputs: ", [output for output in node.output])
    print("-" * 60)
