import xml.etree.ElementTree as ET
import copy

N = 30  # Number of edits to keep
infile = "train-edits.xml"
outfile = "truncated_edits.xml"

context = ET.iterparse(infile, events=("end",))
root = ET.Element("WPEditSet")
count = 0

for event, elem in context:
    if elem.tag == "WPEdit":
        if count < N:
            root.append(copy.deepcopy(elem))
            count += 1
        elem.clear()
    if count >= N:
        break

tree = ET.ElementTree(root)
tree.write(outfile, encoding="utf-8", xml_declaration=True)
