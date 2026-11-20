from .load_medipath_extract import *
from .search_fasta import *
import argparse
from pathlib import Path
import tomllib
import sys

def load_config(config):
    with Path(config).open("rb") as f:
        config_dict = tomllib.load(f)
    return config_dict

def check_db_files(config_dict):
    database_config = config_dict.get("database", {})
    if len(database_config) == 0:
        print("Error in config file, if could not find reason, use the default config file instead")
        return False
    else:
        medi_path = Path(database_config["db_path"]) / database_config["default_medipath_db"]
        if not Path(medi_path).exists():
            default_medipath_exact = Path(database_config["db_path"]) / database_config["default_medipath_extract"]
            df_medipath = load_medipth_extraction(default_medipath_exact)
            save_load_extraction(medi_path, df_medipath)
        fasta_db_path = Path(database_config["db_path"]) / database_config["default_consensus_db"]
        if not Path(fasta_db_path).exists():
            default_list = database_config.get("default_project_path_list", [])
            print("Creating consensus db with default project paths list, this may take a while")
            search_path_for_fasta(default_list, fasta_db_path)
        return Path(fasta_db_path).exists() and Path(medi_path).exists()

def search_in_medipath_db(medipath_ids, medipath_db):

    mask = (
        medipath_db["Medipath_ID"].astype(str).isin(medipath_ids)
        |
        medipath_db["ALT_Medipath"]
            .fillna("")
            .str.split(";")
            .apply(lambda ids: any(i in medipath_ids for i in ids))
    )

    result = medipath_db[mask]
    return result

def search_in_consensus_db(all_ids, consensus_db):
    mask = (
        consensus_db["medipath_id"].astype(str).isin(all_ids)
    )

    result = consensus_db[mask]
    return result


def search_by_medipath(config_dict, medipath_ids):
    medi_path = Path(config_dict["database"]["db_path"]) / config_dict["database"]["default_medipath_db"]
    consensus_path = Path(config_dict["database"]["db_path"]) / config_dict["database"]["default_consensus_db"]
    if Path(medi_path).exists() and Path(consensus_path).exists():

        medipath_db = load_from_save(medi_path)
        consensus_db = load_from_export(consensus_path)

        #check medipath id
        medipath_check = search_in_medipath_db(medipath_ids, medipath_db)
        if medipath_check.empty:
            print("Could not find any matching results in Medipath extraction")
        else:
            print(medipath_check.to_string(index=False))
        alt_ids = []
        for _, row in medipath_check.iterrows():
            alt_row = row["ALT_Medipath"]
            if alt_row != "":
                alt_ids = alt_ids + alt_row.split(";")
        new_id_list = list(set(medipath_ids + medipath_check["Medipath_ID"].astype(str).tolist() + alt_ids))
        #print(new_id_list)
        consensus_check = search_in_consensus_db(new_id_list, consensus_db)
        if consensus_check.empty:
            print("Could not find any matching consensus record under all project folders")
        else:
            print(consensus_check.to_string(index=False))
 

    else:
        print("db is not ready to use, please run `vidrl-seq` init first")
        sys.exit()
    



def build_parser():
    parser = argparse.ArgumentParser(
        prog="vidrl_seq",
        description="CLI tool for VIDRL sequence extraction and FASTA searching.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available subcommands",
    )

    # 1. vidrl_seq search [medipath_id] --output (optional)
    search_parser = subparsers.add_parser("search", help="Search FASTA by Medipath ID")
    search_parser.add_argument(
        "medipath_id",
        nargs="+",
        type=str,
        help="The Medipath ID to search for",
    )
    """ search_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Optional output file path",
    ) """

    # 2. vidrl_seq init
    subparsers.add_parser("init", help="Initialize project configuration or database")

    # 3. vidrl_seq add [path]
    add_parser = subparsers.add_parser("add", help="Add sequences from a file or directory")
    add_parser.add_argument(
        "path",
        type=Path,
        help="Path to the file or directory to add",
    )

    # 4. vidrl_seq load --medipath-extract [path] --consensus_db [path]
    load_parser = subparsers.add_parser("load", help="Load Medipath extract into consensus DB")
    load_parser.add_argument(
        "--medipath-extract",
        type=Path,
        help="Path to the Medipath extract file",
    )
    load_parser.add_argument(
        "--consensus_db",
        type=Path,
        help="Path to the consensus database",
    )

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DEFAULT_CONFIG = PROJECT_ROOT / "config.toml"
    config_dict = load_config(DEFAULT_CONFIG)

    #print(config_dict)

    if args.command == "search":
        search_by_medipath(config_dict=config_dict, medipath_ids=args.medipath_id)

    elif args.command == "init":
        print("Initializing vidrl_seq...")
        
        #check whether db files are ready
        if check_db_files(config_dict):
            print("Database is ready to use")
        else:
            print("Error in database initialization, please check your config file")


    elif args.command == "add":
        print(f"Adding path: {args.path}")
        # Call your add logic here
        print("function is under development")

    elif args.command == "load":
        # Note: '--medipath-extract' automatically becomes 'args.medipath_extract'
        #load_extract(
         #   medipath_extract=args.medipath_extract,
        #    consensus_db=args.consensus_db,
        #)
        print("Under development for this function")


if __name__ == "__main__":
    main()