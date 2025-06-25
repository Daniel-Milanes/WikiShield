import xml.etree.ElementTree as ET

file1 = "train-edits-random.xml"
file2 = "train-edits-reported.xml"
output_file = "combined_edits.xml"

# Parse both files
tree1 = ET.parse(file1)
tree2 = ET.parse(file2)
root1 = tree1.getroot()
root2 = tree2.getroot()

# Create a new root and append all WPEdit children from both files
combined_root = ET.Element("WPEditSet")

for wpedit in root1.findall("WPEdit"):
    combined_root.append(wpedit)

for wpedit in root2.findall("WPEdit"):
    combined_root.append(wpedit)

# Write out the combined XML
ET.ElementTree(combined_root).write(output_file, encoding="utf-8", xml_declaration=True)
print(f"Combined XML saved as {output_file}.")
