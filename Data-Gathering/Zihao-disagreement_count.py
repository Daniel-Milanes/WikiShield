import xml.etree.ElementTree as ET

def extract_editid_to_vandal(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    d = {}
    for wpedit in root.findall("WPEdit"):
        edit_id = wpedit.findtext("EditID")
        vandal_flag = wpedit.findtext("isvandalism")
        if edit_id:
            d[edit_id.strip()] = (vandal_flag.strip().lower() if vandal_flag else "false")
    return d

xml_file1 = "trial-edits-0713d.xml"
xml_file2 = "trial-edits.xml"

map1 = extract_editid_to_vandal(xml_file1)
map2 = extract_editid_to_vandal(xml_file2)

overlap = set(map1.keys()) & set(map2.keys())

num_disagree = 0
for eid in overlap:
    if map1[eid] != map2[eid]:
        num_disagree += 1

if num_disagree == 0:
    print("All overlapping edits agree on isvandalism value.")
else:
    print(f"{num_disagree} overlapping edits disagree on isvandalism value.")
