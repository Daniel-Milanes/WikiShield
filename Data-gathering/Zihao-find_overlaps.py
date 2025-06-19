import xml.etree.ElementTree as ET

def extract_edit_ids_and_vandal_counts(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ids = set()
    vandal_count = 0
    for wpedit in root.findall("WPEdit"):
        edit_id = wpedit.findtext("EditID")
        vandal_flag = wpedit.findtext("isvandalism")
        if edit_id:
            ids.add(edit_id.strip())
        if vandal_flag and vandal_flag.strip().lower() == "true":
            vandal_count += 1
    return ids, vandal_count

xml_file1 = "trial-edits-0713d.xml"
xml_file2 = "trial-edits-0413c.xml"

ids1, vandal_count1 = extract_edit_ids_and_vandal_counts(xml_file1)
ids2, vandal_count2 = extract_edit_ids_and_vandal_counts(xml_file2)
overlap = ids1 & ids2

print(f"Number of overlapping edits: {len(overlap)}")

print(f"Number of edits in {xml_file1}: {len(ids1)}")

print(f"Edits in {xml_file1} marked as vandalism: {vandal_count1}, proportion: {vandal_count1/len(ids1)}")

print(f"Number of edits in {xml_file2}: {len(ids2)}")

print(f"Edits in {xml_file2} marked as vandalism: {vandal_count2}, proportion: {vandal_count2/len(ids2)}")

