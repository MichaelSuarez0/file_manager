import shutil
from pathlib import Path
from typing import Callable, Protocol, Self, runtime_checkable


@runtime_checkable
class StringMethodsProtocol(Protocol):
    """Protocol que declara todos los métodos de str para autocompletado"""

    def capitalize(self) -> Self: ...
    def casefold(self) -> Self: ...
    def center(self, width: int, fillchar: str = " ") -> Self: ...
    def count(self, sub: str, start: int = 0, end: int = -1) -> Self: ...
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> Self: ...
    def endswith(
        self, suffix: str | tuple[str, ...], start: int = 0, end: int = -1
    ) -> Self: ...
    def expandtabs(self, tabsize: int = 8) -> Self: ...
    def format(self, *args, **kwargs) -> Self: ...
    def format_map(self, mapping) -> Self: ...
    def index(self, sub: str, start: int = 0, end: int = -1) -> Self: ...
    def isalnum(self) -> Self: ...
    def isalpha(self) -> Self: ...
    def isascii(self) -> Self: ...
    def isdecimal(self) -> Self: ...
    def isdigit(self) -> Self: ...
    def isidentifier(self) -> Self: ...
    def islower(self) -> Self: ...
    def isnumeric(self) -> Self: ...
    def isprintable(self) -> Self: ...
    def isspace(self) -> Self: ...
    def istitle(self) -> Self: ...
    def isupper(self) -> Self: ...
    def join(self, iterable) -> Self: ...
    def ljust(self, width: int, fillchar: str = " ") -> Self: ...
    def lower(self) -> Self: ...
    def lstrip(self, chars: str | None = None) -> Self: ...
    def partition(self, sep: str) -> Self: ...
    def removeprefix(self, prefix: str) -> Self: ...
    def removesuffix(self, suffix: str) -> Self: ...
    def replace(self, old: str, new: str, count: int = -1) -> Self: ...
    def rfind(self, sub: str, start: int = 0, end: int = -1) -> Self: ...
    def rindex(self, sub: str, start: int = 0, end: int = -1) -> Self: ...
    def rjust(self, width: int, fillchar: str = " ") -> Self: ...
    def rpartition(self, sep: str) -> Self: ...
    def rsplit(self, sep: str | None = None, maxsplit: int = -1) -> Self: ...
    def rstrip(self, chars: str | None = None) -> Self: ...
    def split(self, sep: str | None = None, maxsplit: int = -1) -> Self: ...
    def splitlines(self, keepends: bool = False) -> Self: ...
    def startswith(
        self, prefix: str | tuple[str, ...], start: int = 0, end: int = -1
    ) -> Self: ...
    def strip(self, chars: str | None = None) -> Self: ...
    def swapcase(self) -> Self: ...
    def title(self) -> Self: ...
    def translate(self, table) -> Self: ...
    def upper(self) -> Self: ...
    def zfill(self, width: int) -> Self: ...


class ESNameBuilder(StringMethodsProtocol):
    def __init__(self):
        #  self.path = path
        self._pipeline: list[Callable] = []
        self._excepciones = (
            "de",
            "del",
            "la",
            "el",
            "en",
            "y",
            "con",
            "a",
            "los",
            "las",
            "e",
        )

    def __getattr__(self, name: str):
        """
        Intercepta cualquier método que no exista y verifica si es un método de str.
        Si lo es, crea dinámicamente un método que lo envuelve en el pipeline.
        """
        # Verificar si el atributo existe en la clase str
        if hasattr(str, name):
            str_method = getattr(str, name)

            # Si es un método callable
            if callable(str_method):

                def wrapper(*args, **kwargs) -> Self:
                    """Envuelve el método de str para agregarlo al pipeline"""

                    def _f(s: str) -> str:
                        return str_method(s, *args, **kwargs)

                    self._pipeline.append(_f)
                    return self

                return wrapper

        # Si no es un método de str, lanzar AttributeError normal
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    # ==== Métodos de construcción del pipeline ====
    def filter(self, keyword: str, filter_out: bool = False) -> Self:
        def _f(name: str) -> str:
            if filter_out:
                return name if keyword not in name else ""
            else:
                return name if keyword in name else ""

        self._pipeline.append(_f)
        return self

    def keep_after(self, char: str = "-") -> Self:
        def _f(name: str) -> str:
            parts = name.split(char)
            if len(parts) == 1:
                return parts[0].split(".")[-1].strip()
            return " ".join(parts[1:]).strip()

        self._pipeline.append(_f)
        return self

    def replace(self, old: str, new: str) -> Self:
        def _f(name: str) -> str:
            return name.replace(old, new)

        self._pipeline.append(_f)
        return self

    def normalize_spaces_lower(self) -> Self:
        self._pipeline.append(lambda s: " ".join(s.split()).lower())
        return self

    def add_dash_after_keywords(
        self, keywords=("encuentro prospectivo", "nota de actualidad")
    ):
        def _f(name: str) -> str:
            for k in keywords:
                if k in name:
                    name = name.replace(k, f"{k} -")
            return name

        self._pipeline.append(_f)
        return self

    # Si toda la palabra está en mayúsculas dejarla así
    def smart_title(self, excepciones=None) -> Self:
        if excepciones:
            self._excepciones = excepciones

        def _f(name: str) -> str:
            palabras = name.split()
            resultado = []
            for i, palabra in enumerate(palabras):
                if palabra.lower() in self._excepciones and i != 0:
                    resultado.append(palabra.lower())
                else:
                    resultado.append(palabra.capitalize())
            return " ".join(resultado)

        self._pipeline.append(_f)
        return self

    # ==== Aplicación ====
    def build(self) -> str:
        # nombre inicial (stem si archivo, name si carpeta)
        name = self.path.name if self.path.is_dir() else self.path.stem
        for f in self._pipeline:
            name = f(name)
        return name

    def rename(self) -> Path:
        new_name = self.build()
        if not new_name:
            return self.path
        else:
            if self.path.is_dir():
                new_path = self.path.with_name(new_name)
            else:
                new_path = self.path.with_stem(new_name)

            self.path.rename(new_path)
        return new_path


def flatten_to_base(base_dir: Path, pattern: str = "*") -> None:
    """
    Copia un nivel arriba (al directorio base) todos los archivos contenidos en subdirectorios.
    - Mantiene solo archivos (no copia carpetas).
    - Si hay colisión de nombre, antepone el nombre de la carpeta origen.
    """
    if not base_dir.is_dir():
        raise NotADirectoryError(f"{base_dir} no es un directorio")

    for file_path in base_dir.rglob(pattern):
        if file_path.is_file() and file_path.parent != base_dir:
            target = base_dir / file_path.name
            if target.exists():
                # Resolver colisión con el nombre de la carpeta origen y un contador si hiciera falta
                parent_name = file_path.parent.name
                candidate = base_dir / f"{parent_name} - {file_path.name}"
                i = 1
                while candidate.exists():
                    candidate = base_dir / f"{parent_name} - {i} - {file_path.name}"
                    i += 1
                target = candidate
            # copiar en lugar de mover
            shutil.copy2(str(file_path), str(target))


if __name__ == "__main__":
    DIR_PATH = Path(r"C:\Users\micha\OneDrive\CEPLAN\0. Subir últimas fichas")
    for path in DIR_PATH.iterdir():
        builder = (
            ESNameBuilder(path)
            # .filter("PPT", filter_out=True)
            # .keep_after("-")
            # .replace(".", " -")
            # .normalize_spaces_lower()
            # .add_dash_after_keywords()
            .smart_title()
        )
        new_name = builder.build()
        print(new_name)
    # dry run: solo mostrar, no renombrar
    # print(f"[DRY-RUN] {path.name} -> {new_name}")

    # flatten_to_base(DIR_PATH)
