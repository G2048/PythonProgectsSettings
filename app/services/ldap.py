import json
import logging

from ldap3.utils.ciDict import CaseInsensitiveDict

from app.drivers.ldap import LdapConnection

logger = logging.getLogger("app.services.ldap")


class LdapJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            obj = obj.decode("utf-8")
            return obj
        elif isinstance(obj, CaseInsensitiveDict):
            obj = dict(obj)
            return obj

        return super().default(self, obj)


class LdapSearch:
    def __init__(self, ldap: LdapConnection):
        self.connection = ldap.connection
        self.search_base = "dc=katren,dc=net"

    @property
    def entries(self):
        return self.connection.entries or ["No entries"]

    @staticmethod
    def dump_to_json(entries):
        return json.dumps(entries, ensure_ascii=False, cls=LdapJsonEncoder)

    def _search(self, search_base: str, search_filter: str, attributes=None):
        logger.info(f"Search base: {search_base}, Search filter: {search_filter}")
        status, result, response, request = self.connection.search(
            search_base, search_filter, attributes=attributes
        )  # usually you don't need the original request (4th element of the returned tuple)
        logger.info("Search is done")

        # logger.debug(f"{status=}, {result=}, {response=}")
        logger.debug(f"{request=}")
        return status, result, response

    def all_users(self):
        search_filter = "(&(objectCategory=person)(objectClass=user))"
        return self._search(self.search_base, search_filter)

    def email(self, email: str):
        search_filter = (
            f"(&(objectClass=user)(proxyAddresses=smtp:{email})(mail={email}))"
        )
        return self._search(
            self.search_base,
            search_filter,
            attributes=["sAMAccountName", "displayName", "distinguishedName", "mail"],
        )

    def user(self, username):
        search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
        return self._search(
            self.search_base,
            search_filter,
            attributes=["sAMAccountName", "displayName", "distinguishedName", "mail"],
        )

    def ou(self):
        search_filter = "(objectClass=organizationalUnit)"
        return self._search(self.search_base, search_filter)
