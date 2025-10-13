#! python
import pathlib


def main():
    PATHS = (
        "app",
        "app/api",
        "app/api/models",
        "app/api/dependencies",
        "app/api/v1",
        "app/api/v1/routers",
        "app/configs",
        "app/drivers",
        "app/services",
        "app/core/interfaces",
        "app/adapters",
        "tests",
    )
    for p in PATHS:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)
        with open(p + "/__init__.py", "w") as f:
            f.write("")


if __name__ == "__main__":
    main()
