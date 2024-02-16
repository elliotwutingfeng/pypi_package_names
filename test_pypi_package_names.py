import json
import sys
import unittest

try:
    from typing import Any  # Python 3.5 or later required
except ImportError:
    pass

from pypi_package_names import get_unique_package_names


class TestGetUniquePackageNames(unittest.TestCase):
    @staticmethod
    def _is_str_or_unicode(s):  # type: (Any) -> bool
        if isinstance(s, str):
            return True
        is_python2 = sys.version_info[0] == 2
        return is_python2 and type(s).__name__ == "unicode"

    @staticmethod
    def _check_package_names(package_names):  # type: (list[str]) -> None
        assert isinstance(package_names, list)
        assert all(
            TestGetUniquePackageNames._is_str_or_unicode(s) for s in package_names
        )
        assert "black" in package_names
        assert "requests" in package_names

    def test_get_unique_package_names(self):
        package_names_from_json_api = json.loads(
            get_unique_package_names()
        )  # type: list[str]
        TestGetUniquePackageNames._check_package_names(package_names_from_json_api)

        package_names_from_html_api = json.loads(
            get_unique_package_names(html_only=True)
        )  # type: list[str]
        TestGetUniquePackageNames._check_package_names(package_names_from_html_api)


if __name__ == "__main__":
    unittest.main()
