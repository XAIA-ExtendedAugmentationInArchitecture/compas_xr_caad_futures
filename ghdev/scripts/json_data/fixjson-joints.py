import json

# List of joint IDs to update
mirror_ids = {
    113, 117, 111, 120, 116, 100, 125, 124, 60, 66, 67, 82, 77, 79, 128, 129, 147, 151, 153, 210, 205,
    213, 217, 78, 53, 80, 103, 107, 75, 76, 109, 234, 233, 235, 236, 30, 31, 33, 29, 28, 32, 69, 70, 40,
    224, 108, 220, 179, 141, 142, 145, 132, 146, 221, 227, 228, 206, 49, 50, 152, 212, 214, 215, 238,
    239, 237, 46, 81, 99, 61, 93, 97, 136, 237, 243, 244, 191, 193, 245, 148, 159, 94, 95, 101, 126, 135,
    127, 131, 211, 161, 162, 163, 164, 24, 26, 27, 203, 138, 137, 105, 110, 112, 182, 181, 25, 189, 201,
    185, 186, 169, 171, 172, 173, 158, 165, 168
}

# Load JSON from file
with open("robarch24_joints.json", "r") as f:
    data = json.load(f)

# Process each joint
for joint_id, joint_data in data.get("joint", {}).items():
    if int(joint_id) in mirror_ids:
        joint_data["is_mirrored"] = True

# Save updated JSON to a new file
with open("robarch24_joints_fixed.json", "w") as f:
    json.dump(data, f, indent=4)

print("Saved modified JSON to robarch24_joints_fixed.json")
