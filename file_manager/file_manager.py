import logging
import re
import shutil
import warnings
from pathlib import Path
from typing import Optional, Self, Sequence

# Configuración del logging para guardar en el archivo con ruta personalizada


# TODO: Add function to copy files with a specific extension
class FileManager:
    def __init__(self):
        """
        Initializes File Manager for managing files in the specified directory.

        Args:
            search_directory (str): Directory to search for files. Should be a valid path string.
        """
        self.SEARCH_DIR: str | Path
        self.USER_CWD = Path.cwd()
        self.max_depth: int = 0
        self.current_depth: int = 0
        self.file_paths: list[Path] = []

    # -----------------------------------------
    # --------  Basic functionality
    # -----------------------------------------

    def _validate_dir(self, search_dir: str | Path):
        if isinstance(search_dir, str):
            search_dir = Path(search_dir)
        if not isinstance(search_dir, Path):
            raise NotADirectoryError(
                f"'search_dir' should be of type 'Path', got: {type(search_dir)}"
            )
        if not search_dir.is_dir():
            raise NotADirectoryError(
                "'search_dir' should be a valid directory, not a file path"
            )

    def set_search_dir(self, search_dir: Path):
        self._validate_dir(search_dir)
        self.SEARCH_DIR = search_dir

    def set_max_depth(self, max_depth: int):
        self.max_depth = max_depth

    def copy(self, paths: list[Path], target_dir: Path):
        for path in paths:
            if path.is_dir():
                shutil.copytree(src=path, dst=target_dir)
            elif path.is_file():
                shutil.copy(src=path, dst=target_dir)
            else:
                raise TypeError(
                    f"All paths should be of type 'Path', got: {type(path)}"
                )

    def delete(self, paths: list[Path]):
        for item in paths:
            item.unlink(missing_ok=True)

    def rename(self, paths: list[Path], mapping: dict[str, str]):
        not_used_names = set(list(mapping.values()))
        for item in paths:
            try:
                new_name = mapping[item.name]
            except KeyError:
                continue
            item.with_name(new_name)
            try:
                not_used_names.remove(new_name)
            except KeyError:
                pass

        if not_used_names:
            warnings.warn(
                f"Some new names were not used in the mapping: {not_used_names}"
            )

    def append_to_name(self, paths: list[Path]):
        pass

    def list_files_recursive(self, search_dir: Path) -> list[Path]:
        """
        Lista los nombres de archivos presentes en el directorio de búsqueda.
        Si encuentra un folder, entra al folder y busca archivos recursivamente
        dependiendo de max_depth.

        Args:
        ---------
            max_depth (int):
                Máximo de iteraciones recursivas

        Returns:
            list: Lista de nombres de archivos filtrados y formateados según los parámetros.
        """
        self.current_depth += 1
        self._validate_dir(search_dir)

        found_file_paths = []
        for file in search_dir.iterdir():
            if file.is_dir():
                if self.current_depth <= self.max_depth:
                    found_file_paths.extend(self.list_files_recursive(file))
                else:
                    found_file_paths.append(file)
            elif file.is_file():
                found_file_paths.append(file)

        if not found_file_paths:
            raise ValueError("No se encontraron archivos en la carpeta")

        self.current_depth = 0
        return found_file_paths

    # TODO: Move to file_filterer or smth
    def filter_by_extension(
        self,
        extension: str,
        filter_out: bool = False,
        # file_paths: Optional[list[Path]] = None,
    ) -> Self:
        if extension and not extension[0] == ".":
            raise ValueError("'extension' should start with a '.'")

        if not self.file_paths:
            self.file_paths = self.list_files_recursive(self.SEARCH_DIR)

        if filter_out:
            self.file_paths = [item for item in self.file_paths if item.suffix != extension]
        else:
            self.file_paths = [item for item in self.file_paths if item.suffix == extension]
        return self

    def filter_by_regex_match(
        self,
        regex: str,
        filter_out: bool = False,
        # file_paths: Optional[list[Path]] = None,
    ) -> Self:
        
        if not self.file_paths:
            self.file_paths = self.list_files_recursive(self.SEARCH_DIR)

        if filter_out:
            self.file_paths = [
                item
                for item in self.file_paths
                if not re.match(pattern=regex, string=item.name)
            ]
        else:
            self.file_paths = [
                item for item in self.file_paths if re.match(pattern=regex, string=item.name)
            ]
        return self

    def filter_by_names(
        self,
        names: Sequence[str],
        filter_out: bool = False
    ) -> Self:
        
        if not self.file_paths:
            self.file_paths = self.list_files_recursive(self.SEARCH_DIR)    
        names_set = set(names)
        
        if filter_out:
            self.file_paths = [item for item in self.file_paths if item.name in names_set]
        else:
            self.file_paths = [item for item in self.file_paths if item.name in names_set]
        return self
    
    def collect(self):
        file_paths = self.file_paths
        self.file_paths = []
        return file_paths

    @staticmethod
    def sort_files_by_number(file_list: list) -> list:
        def extract_number(text: str) -> int:
            # This finds all numbers in the string and returns the first occurrence.
            numbers = re.findall(r"\d+", text)
            return int(numbers[0]) if numbers else float("inf")

        return sorted(file_list, key=extract_number)
