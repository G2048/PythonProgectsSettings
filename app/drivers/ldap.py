from typing import Self

from ldap3 import AUTO_BIND_NO_TLS, NTLM, SAFE_SYNC, Connection, Server

from app.configs.settings import LDAPUserSettings


class LdapException(Exception):
    pass


# For ldap3 library must be installed the pycryptodome library!
class LdapConnection:
    __slots__ = ('connection', 'server')

    def __init__(self, settings: LDAPUserSettings):
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
