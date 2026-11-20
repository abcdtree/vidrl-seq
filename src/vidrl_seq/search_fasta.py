from pathlib import Path
from Bio import SeqIO
import pandas as pd
import re
import shutil
from tqdm import tqdm

def search_path_for_fasta(path_list, export_file=""):
    medipath_pattern = re.compile(r'(?<!\d)2\d{7}(?!\d)')

    df_sum = pd.DataFrame()
    for root_dir in path_list:
        results = []

        # Collect matching FASTA files first so tqdm knows the total count
        print(f"Working on fasta search under path: {root_dir} ...")
        fasta_files = [
            f for f in Path(root_dir).rglob("*")
            if f.is_file() and f.suffix.lower() in (".fa", ".fasta")
        ]

        for fasta_file in tqdm(fasta_files, desc=f"Scanning {Path(root_dir).name}", unit="file"):
            # check filename
            filename_matches = medipath_pattern.findall(fasta_file.name)

            for mid in filename_matches:
                results.append({
                    "medipath_id": mid,
                    "file": str(fasta_file),
                    "source": "filename",
                    "seqid": None
                })

            # check fasta seq ids
            try:
                for record in SeqIO.parse(fasta_file, "fasta"):
                    matches = medipath_pattern.findall(record.id)

                    for mid in matches:
                        results.append({
                            "medipath_id": mid,
                            "file": str(fasta_file),
                            "source": "seqid",
                            "seqid": record.id
                        })

            except Exception as e:
                tqdm.write(f"Error reading {fasta_file}: {e}")

        """ for fasta_file in Path(root_dir).rglob("*"):
            if fasta_file.suffix.lower() not in (".fa", ".fasta"):
                continue

            # check filename
            filename_matches = medipath_pattern.findall(fasta_file.name)

            for mid in filename_matches:
                results.append({
                    "medipath_id": mid,
                    "file": str(fasta_file),
                    "source": "filename",
                    "seqid": None
                })

            # check fasta seq ids
            try:
                for record in SeqIO.parse(fasta_file, "fasta"):
                    matches = medipath_pattern.findall(record.id)

                    for mid in matches:
                        results.append({
                            "medipath_id": mid,
                            "file": str(fasta_file),
                            "source": "seqid",
                            "seqid": record.id
                        })

            except Exception as e:
                print(f"Error reading {fasta_file}: {e}") """

        df = pd.DataFrame(results)
        # remove duplicates if desired
        df = df.drop_duplicates()
        print(f"From {root_dir}, Found {len(df)} consensus fasta files with medipath id")
        if df_sum.empty:
            df_sum = df.copy()
        else:
            df_sum = pd.concat([df_sum, df])
    df_sum = df_sum.drop_duplicates()
    df_sum = df_sum.sort_values(by="medipath_id")
    print(f"In total, Found {len(df_sum)} consensus fasta files with medipath id")
    if export_file != "":
        df_sum.to_csv(export_file, index=False)
    return df_sum

def load_from_export(export_file):
    return pd.read_csv(export_file)

def backup_file(src, dst):
    src_p = Path(src)
    dst_p = Path(dst)

    if dst_p.exists():
        i = 1
        while True:
            new_dst = dst_p.with_name(f"{dst_p.stem}_{i}{dst_p.suffix}")
            if not new_dst.exists():
                dst_p = new_dst
                break
            i += 1
    shutil.copy2(src_p, dst_p)

def add_new_folder_in(export_file, new_paths):
    df_old = load_from_export(export_file)
    df_new = search_path_for_fasta(new_paths)

    df_join = pd.concat([df_old, df_new])
    df_join = df_join.sort_values(by="medipath_id")
    df_join = df_join.drop_duplicates()
    #backup the old load

    backup_file(export_file, export_file+".backup")
    df_join.to_csv(export_file, index=False)
    return df_join

