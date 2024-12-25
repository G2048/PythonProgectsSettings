from dataclasses import dataclass
from pathlib import Path

# from memory_profiler import profile


@dataclass
class Dirs:
    templates = Path(__file__).parent / 'templates'
    app = templates / 'app'
    api = app / 'api'
    main = app / 'main.py'

    configs = app / 'configs'
    init_configs = configs / '__init__.py'
    log_settings = configs / 'log_settings.py'
    settings = configs / 'settings.py'

    @classmethod
    def list_dirs(cls):
        return list(filter(lambda x: isinstance(x, Path), cls.__dict__.values()))


@dataclass
class App:
    templates = Path(__file__).parent / 'templates'
    app = templates / 'app'
    main = app / 'main.py'

    @classmethod
    def list_dirs(cls):
        return list(
            filter(
                lambda x: isinstance(x, Path) and x.suffix != '.py',
                cls.__dict__.values(),
            )
        )

    @classmethod
    def list_files(cls):
        return list(
            filter(
                lambda x: isinstance(x, Path) and x.suffix == '.py',
                cls.__dict__.values(),
            )
        )


class Api(App):
    api = App.app / 'api'


class Configs(App):
    configs = App.app / 'configs'
    init_configs = configs / '__init__.py'
    log_settings = configs / 'log_settings.py'
    settings = configs / 'settings.py'


class Registrator:
    def add(self, class_):
        class_
        pass


class Creator:
    def dirs(self):
        pass

    def files(self):
        pass

    def fill_files(self):
        pass


@profile
def init():
    # templates = Path(__file__).parent / 'templates'
    # templates.touch()
    # for dir_ in Dirs.list_dirs():
    #     dir_.mkdir(parents=True, exist_ok=True)
    # dir_.touch()
    for file in Configs.list_dirs():
        file.mkdir(parents=True, exist_ok=True)
    for file in Configs.list_files():
        file.touch()


if __name__ == '__main__':
    init()
