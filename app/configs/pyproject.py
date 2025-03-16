import tomllib


class _ParserPyproject:
    def __init__(self, pyproject_toml='pyproject.toml'):
        with open('pyproject.toml', 'rb') as f:
            self._pyproject_toml = tomllib.load(f)
        self._tool = self._pyproject_toml.get('tool', {})
        self._poetry = self._tool.get('poetry', {})

        self.name = self._poetry.get('name', {})
        self.version = self._poetry.get('version')


class ParserPyproject:
    __slots__ = ()
    _parser = _ParserPyproject()
    name = _parser.name
    version = _parser.version


def test_parser_pyproject():
    parser = _ParserPyproject()
    assert parser.version == '0.1.0'
    assert parser.name == 'Audio Tools'
    assert isinstance(parser._tool, dict)
    print(f'{parser._tool=}')


if __name__ == '__main__':
    test_parser_pyproject()
