"""
Top-level package API documentation would go here.

Here we just fetch the version from the distribution and expose as __version__.
"""

# Machinery to extract the version from package metadata.

from importlib.metadata import version as _version

# Passing in the distribution name which is not always the package name:
__version__ = _version("pm_utils")
