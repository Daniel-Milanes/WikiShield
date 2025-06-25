**api_calls** contains scripts that call the MediaWiki and Wikidata APIs/platforms to fetch more detailed data based on the edit information provided in the xml files. We first used "summarize_edit_diffs.py" to extract the actual added and deleted content associated with each edit and decode some useful features from the xml, and output a csv file. Then we use "recent_edit_count_for_csv.py" and "is_person_encoding" to fetch data for two more features and add them into the csv. The "find_edits.py" script is optional and it gives an overview of the added/deleted contents of the edits from the xml file.  

**find_edits**: 
shows the added and removed lines corresponding to the edits given an xml file by calling the MediaWiki API

**is_person_encoding**: 
given a csv file, uses the Wikidata QID of the Wikipedia posts to determine if the subject is about a person (QID could be traced back to Q5), and puts the results in the csv with one hot encoding

**recent_edit_count_for_csv**: 
given a csv file, calls the MediaWiki API to obtain the number of edits made to the Wikipedia posts within the 5-day time window before the recorded edits were made, and puts the results in the csv

**summarize_edit_diffs**: 
given an xml file, fetches useful information from the xml file itself and calls the MediaWiki API to obtain the added and removed lines associated with the edits, and saves the output into a csv file

---------------------------------------------------------------

**data_cleaning and preprocessing** contains scripts that help decipher and manipulate the information in the xml files. These scripts are optional to be used depending on the data.


**combine_xml**: 
combines two xml files that contain Wikipedia edit info into one single xml file

**count_edits_remove_duplicates**: 
counts the number of distinct edits contained in an xml file and removes the duplicate edits

**data_truncation**: 
takes out the first N edits contained in an xml file (to test if scripts work as desired)

**dates**: 
retrieves dates when the edits were made from an xml file; counts how many of the edits were made before a timestamp

**disagreement_count**: 
for two different xml files that contain overlapping edit info, checks how many disagreements there are over the overlapping part in terms of the isvandalism label

**find_categories_of_interest**: 
among the first few edits that are labeled as vandalism, summarizes their topic categories based on Wikidata QID

**find_overlaps**: 
counts how much two xml files overlap in terms of the edits they contain, and computes the percentage of vandalism edits in both files

**remove_xml_overlaps**: 
given an xml file, filters out the edits that are contained in another xml file
