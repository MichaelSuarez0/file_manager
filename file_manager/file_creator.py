from pathlib import Path
from typing import Optional


class FileCreator:
    USER_WD = Path.cwd()

    def __init__(self) -> None:
        pass

    @staticmethod
    def _create_file(file_name: str, target_dir: Path) -> Path:
        created_path = target_dir / file_name
        created_path.touch()
        return created_path

    def create_file(self, file_name: str) -> Path:
        return self._create_file(file_name, self.USER_WD)

    def create_files(
        self, files: list[str | Path], target_dir: Path
    ) -> Optional[list[Path]]:
        if all(isinstance(f, str) for f in files):
            return [self._create_file(file, target_dir) for file in files]

        elif all(isinstance(f, Path) for f in files):
            return [self._create_file(file.name, target_dir) for file in files]
        else:
            raise TypeError("Files should a list of str or Path, do not combine types")
