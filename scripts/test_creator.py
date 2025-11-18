from pathlib import Path
from pprint import pprint

from file_manager import FileManager

TEST_DIR = Path(__file__).parent / "test_folders"
TEST_DIR.mkdir()

def test_touch():
    fm = FileManager()
    fm.touch("prueba.txt")

def test_create_files():
    fm = FileManager()
    base_file = "cuentas_{}.xlsx"
    files = [base_file.format(n) for n in range(1, 5)]
    fm.create_files(files, target_dir=TEST_DIR)
    
# def test_touch():
#     fm = FileManager()
#     fm.touch("prueba.txt")
#     assert fm.SEARCH_DIR / "prueba.txt"

if __name__ == "__main__":
    test_create_files()