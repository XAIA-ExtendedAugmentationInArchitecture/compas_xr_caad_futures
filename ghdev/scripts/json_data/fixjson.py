import json

# Cross product of two 3D vectors
def cross_product(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]

# Load JSON from file
with open("foCTree_assembly.json", "r") as f:
    data = json.load(f)

# Iterate over each node
for node_id, node_data in data["node"].items():
    # Add 'type' if missing
    if isinstance(node_data, dict) and "type" not in node_data:
        node_data["type"] = 3  

    # Process frame: compute z = x × y, replace yaxis with zaxis
    element = node_data.get("element")
    if isinstance(element, dict):
        frame = element.get("frame")
        if isinstance(frame, dict) and "xaxis" in frame and "yaxis" in frame:
            x = frame["xaxis"]
            y = frame["yaxis"]
            if len(x) == 3 and len(y) == 3:
                z = cross_product(x, y)
                frame["xaxis"] = z  # replace yaxis with computed zaxis

# Save to new file
with open("foCTree_assembly_fixed.json", "w") as f:
    json.dump(data, f, indent=4)

print("Saved modified JSON to foCTree_assembly_fixed.json")
