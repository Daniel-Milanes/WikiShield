import xml.etree.ElementTree as ET


input_xml = "filtered_edits.xml"
output_xml = "filtered_edits_no_dup.xml"

tree = ET.parse(input_xml)
root = tree.getroot()

seen_ids = set()
new_root = ET.Element("WPEditSet")

for wpedit in root.findall("WPEdit"):
    eid = wpedit.findtext("EditID")
    if eid and eid not in seen_ids:
        seen_ids.add(eid)
        new_root.append(wpedit)

print(f"Original edits: {len(root.findall('WPEdit'))}")
print(f"Deduplicated edits: {len(seen_ids)}")

ET.ElementTree(new_root).write(output_xml, encoding="utf-8", xml_declaration=True)
print(f"Deduplicated XML saved as {output_xml}.")

tree = ET.parse("filtered_edits_no_dup.xml")
root = tree.getroot()


editids = []
for wpedit in root.findall("WPEdit"):
    eid = wpedit.findtext("EditID")
    if eid:
        editids.append(eid)
print("Total edits:", len(editids))
print("Unique EditIDs:", len(set(editids)))
