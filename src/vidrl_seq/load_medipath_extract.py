import csv
import re
import pandas as pd

def load_medipth_extraction(medipath_extraction_file):
    number_of_rows = []
    collect_of_information = [["Medipath_ID", "PROC", "SPECIMEN_DATE","ALT_Medipath"]]
    with open(medipath_extraction_file, 'r') as mycsv:
        csvreader = csv.reader(mycsv)
        count = 0
        for line in csvreader:
            if count == 0:
                count += 1
                continue
            nrows = len(line)
            number_of_rows.append(nrows)
            if nrows < 10:
                continue
            product = line[1]
            medipath_id = line[3]
            specimendata = line[5]
            #print(";".join(line))
            medi_id_pool = re.findall(r'2\d{7}', ";".join(line))
            print
            medi_id_set = set(medi_id_pool)
            medi_id_set.discard(medipath_id)
            medi_id_alt = ""
            if len(medi_id_set) > 0:
                medi_id_alt = ";".join(list(medi_id_set))
            collect_of_information.append([medipath_id, product, specimendata, medi_id_alt])
    df_collect_info = pd.DataFrame(data=collect_of_information[1:], columns=collect_of_information[0])
    return df_collect_info

def save_load_extraction(db_path, collection_df):
    collection_df.to_csv(db_path, index=None)

def load_from_save(db_path):
    return pd.read_csv(db_path)