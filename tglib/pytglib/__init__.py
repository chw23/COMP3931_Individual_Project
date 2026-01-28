import sys
from ._pytglib import *

if sys.version_info >= (3, 8):
    from importlib.metadata import version, PackageNotFoundError
else:
    # Fallback for Python 3.7
    from importlib_metadata import version, PackageNotFoundError

try:
    # This will look for the installed package named "temporalgraphlib" and read its version
    __version__ = version("temporalgraphlib")
except PackageNotFoundError:
    # This is a fallback for when the package is not installed (e.g., when running locally)
    __version__ = "0.0.0-unknown"
