import os
import shutil
import tempfile
from typing import Optional


class Cache:
    def __init__(self, location: Optional[str] = None):
        if location and not os.path.exists(location):
            raise ValueError(f"Cache location {location} does not exist.")

        self.location = location or tempfile.gettempdir()
        self.is_tmp = location is None

    def path(self, filename: str) -> str:
        return os.path.join(self.location, filename)

    def exists(self, filename: str) -> bool:
        return os.path.exists(self.path(filename))

    def close(self) -> None:
        if self.is_tmp:
            shutil.rmtree(self.location)
