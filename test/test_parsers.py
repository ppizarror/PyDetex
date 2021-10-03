"""
PyDetex
https://github.com/ppizarror/PyDetex

TEST PARSERS
Test several parsers which perform a single operation.
"""

from test._base import BaseTest
import pydetex


class ParserTest(BaseTest):

    def test_version(self) -> None:
        """
        Configure version.
        """
        self.assertNotEqual(pydetex.version.vernum, '')
