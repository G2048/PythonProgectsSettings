from typing import Self, Protocol

from ldap3 import AUTO_BIND_NO_TLS, NTLM, SAFE_SYNC, Connection, Server


class LdapException(Exception):
    pass


class LdapConfig(Protocol):
    host: str
    port: int = 636
    dc: str

    user: str | None = None
    password: str | None = None

    @property
    def username(self):
        return f"{self.dc}\\{self.user}"


# For ldap3 library must be installed the pycryptodome library!
class LdapConnection:
    __slots__ = ("connection", "server")

    def __init__(self, settings: LdapConfig):
        self.server = Server(settings.host, settings.port, use_ssl=True)
        self.connection = Connection(
            self.server,
            settings.username,
            settings.password,
            client_strategy=SAFE_SYNC,
            auto_bind=AUTO_BIND_NO_TLS,
            authentication=NTLM,
        )

    def __enter__(self) -> Self:
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.connection.__exit__(exc_type, exc_value, traceback)
