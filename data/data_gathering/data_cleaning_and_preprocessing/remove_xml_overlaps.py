import xml.etree.ElementTree as ET

file1 = "combined_edits.xml"     # File to filter (edits to keep only if NOT in file2)
file2 = "trial-edits-0713d.xml"     # File whose edits are to be removed from file1
output_file = "filtered_edits.xml"

# 1. Build a set of EditIDs in file2
tree2 = ET.parse(file2)
root2 = tree2.getroot()
editids_to_remove = set()
for wpedit in root2.findall("WPEdit"):
    eid = wpedit.findtext("EditID")
    if eid:
        editids_to_remove.add(eid.strip())

# 2. Parse file1, keep only edits NOT in file2
tree1 = ET.parse(file1)
root1 = tree1.getroot()
filtered_root = ET.Element("WPEditSet")

for wpedit in root1.findall("WPEdit"):
    eid = wpedit.findtext("EditID")
    if eid and eid.strip() not in editids_to_remove:
        filtered_root.append(wpedit)

# 3. Write result to output file
ET.ElementTree(filtered_root).write(output_file, encoding="utf-8", xml_declaration=True)
print(f"Filtered XML saved as {output_file}.")
