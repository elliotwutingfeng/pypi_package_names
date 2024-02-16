import json
import unittest

from pypi_package_names import get_unique_package_names


class TestGetUniquePackageNames(unittest.TestCase):
    @staticmethod
    def _check_package_names(package_names):  # type: (list[str]) -> None
        assert isinstance(package_names, list)
        assert all(isinstance(s, str) for s in package_names)
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
