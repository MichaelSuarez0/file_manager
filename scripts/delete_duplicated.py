import re
from pathlib import Path

from file_manager import FileManager


def delete_duplicated(search_dir: Path, dry_run: bool = False):
    fm = FileManager()
    fm.set_search_dir(search_dir)

    # 1: Get files that end with (1), (2), (#)...
    dupli_regex = r"\(\d\)$"
    fm.filter_by_regex_search(dupli_regex)
    maybe_duplicated = fm.collect()

    # 2: We have to make sure their equivalent without (#) exist
    # We don't want to delete files with (#) that don't have originals
    duplicated_original_dict: dict[Path, Path] = {}
    for duplicated_path in maybe_duplicated:
        original_path = duplicated_path.with_name(
            re.sub(dupli_regex, "", duplicated_path.stem).strip()
            + duplicated_path.suffix
        )
        duplicated_original_dict[duplicated_path] = original_path

    real_duplicates: list[Path] = []
    false_duplicates: list[Path] = []
    for duplic, original in duplicated_original_dict.items():
        if original.exists():
            real_duplicates.append(duplic)
        else:
            false_duplicates.append(duplic)

    print(
        f"Paths that end with (#) that are not duplicated: {len(maybe_duplicated) - len(real_duplicates)}/{len(maybe_duplicated)}"
    )
    # 3: We delete real duplicates and get rid of (#) for false duplicates
    if not dry_run:
        for file in real_duplicates:
            file.unlink()
        for file in false_duplicates:
            clean_original_name = file.with_name(
                re.sub(dupli_regex, "", file.stem).strip() + file.suffix
            )
            file.rename(clean_original_name)
    
    print(f"Deleted ({len(real_duplicates)}):")
    for file in real_duplicates:
        print(f"- {file}")
    print(f"Cleaned ({len(false_duplicates)}):")
    for file in false_duplicates:
        print(f"- {file}")
        
    return real_duplicates, false_duplicates


if __name__ == "__main__":
    from pprint import pprint

    path = Path(r"C:\Users\micha\Downloads")
    delete_duplicated(path, dry_run=False)
