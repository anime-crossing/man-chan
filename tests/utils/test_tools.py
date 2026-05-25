import pytest

from utils.tools import *


class TestDig:
    example1 = {
        "test": 1,
        "array": [1, 2, 3, "abc"],
        "arrayhash": [{"opt": 1}, {"opt": 2}],
        "hash": {"json": {"recur": [1, 2, {"again": "wumbo"}]}},
        55: 67,
        "empty": [],
    }

    def test_dig_gets_first_key(self):
        assert dig(self.example1, "test") == 1

    def test_dig_can_return_array(self):
        assert dig(self.example1, "array") == [1, 2, 3, "abc"]

    def test_dig_can_return_element_in_array(self):
        assert dig(self.example1, "array", 2) == 3
        assert dig(self.example1, "array", 3) == "abc"
        assert dig(self.example1, "array", 0) == 1

    def test_dig_returns_none_on_wrong_index_array(self):
        assert dig(self.example1, "array", 100) == None

    def test_dig_returns_none_on_wrong_key(self):
        assert dig(self.example1, "tester") == None
        assert dig(self.example1, "hash", "unknown") == None

    def test_dig_can_return_value_with_array_and_hash(self):
        assert dig(self.example1, "arrayhash", 1, "opt") == 2

    def test_dig_can_return_value_deeply_nested(self):
        assert dig(self.example1, "hash", "json", "recur", 2, "again") == "wumbo"

    def test_dig_throws_error_on_wrong_component_to_index(self):
        with pytest.raises(ValueError, match=r"Invalid type to index: abc using \[1\]"):
            dig(self.example1, "array", 3, 1)

    def test_dig_throws_error_when_indexing_array_with_string(self):
        with pytest.raises(
            ValueError,
            match=r"Invalid type to index: \[1, 2, 3, 'abc'\] using \[error\]",
        ):
            dig(self.example1, "array", "error")

    def test_dig_can_return_value_when_key_in_hash_is_int(self):
        assert dig(self.example1, 55) == 67

    def test_dig_can_return_none_on_empty_array(self):
        assert dig(self.example1, "empty", 0) == None

    def test_dig_returns_none_early_when_indexing_failed_early(self):
        assert dig(self.example1, "empty", 0, 1, "test") == None
        assert dig(self.example1, "arrayhash", 0, "test", "opt") == None
