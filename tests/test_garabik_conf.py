import strec.garabik as garabik
import pytest
from io import StringIO


class Colors:
    @staticmethod
    def get(name: str) -> str:
        data = {
            "blue": "<blue>",
            "red": "<red>",
            "yellow": "<yellow>",
            "reset": "<reset>",
        }
        return data[name]


def test_color_list():
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something <red>world<reset> string"
    output = StringIO()
    rules = [
        garabik.Rule(r"\b(hello) something (world)\b", ["blue", "red"]),
    ]

    parser = garabik.Parser(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected


@pytest.mark.skip()
def test_color_list2():
    """
    What happens if the beginning of the string does not start with a matching
    group?
    """
    input_data = "this is a hello something world string"
    expected = "this is a <blue>hello<reset> something <red>world<reset> string"
    output = StringIO()
    rules = [
        garabik.Rule(r"beginning \b(hello) something (world)\b", ["blue", "red"]),
    ]

    parser = garabik.Parser(rules, output, Colors)
    parser.feed(input_data)
    result = output.getvalue()
    assert result == expected
