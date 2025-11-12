from pathlib import Path
from pprint import pprint

from file_manager import FileManager

SEARCH_DIR = Path(r"C:\Users\micha\OneDrive\CEPLAN\0. Jhon - Subida de fichas")

# fm = FileManager()
# fm.set_search_dir(SEARCH_DIR)
# fm.set_max_depth(1)
# file_paths = fm.filter_files_by_extension(".xlsx")
# pprint(fm.filter_files_by_regex(regex=r"^(?=.*Fracaso)", file_paths=file_paths))

fm = FileManager()
fm.set_search_dir(SEARCH_DIR)
fm.set_max_depth(1)
file_paths = (
    fm.filter_by_extension(".xlsx")
    .filter_by_regex_match(regex=r"^(?=.*Fracaso)")
    .collect()
)
pprint(file_paths)
