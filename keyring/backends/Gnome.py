import os

from keyring.backend import KeyringBackend
from keyring.errors import PasswordSetError, PasswordDeleteError

class Keyring(KeyringBackend):
    """Gnome Keyring"""

    # Name of the keyring to store the passwords in.
    # Use None for the default keyring.
    KEYRING_NAME = None

    def supported(self):
        try:
            from gi.repository import GnomeKeyring
        except ImportError:
            return -1
        else:
            if ("GNOME_KEYRING_CONTROL" in os.environ and
                "DISPLAY" in os.environ and
                "DBUS_SESSION_BUS_ADDRESS" in os.environ):
                return 1
            else:
                return 0
    
    def dump(self, print_passwords=False):
        """Get all keyring entries (with or without passwords)
        """
        from gi.repository import GnomeKeyring
        dump = ""
        (result, ids) = GnomeKeyring.list_item_ids_sync(self.KEYRING_NAME)
        for id in ids:	
            (result, item) = GnomeKeyring.item_get_info_sync(self.KEYRING_NAME, id)
            if result == GnomeKeyring.Result.IO_ERROR:
                return None
            if result == GnomeKeyring.Result.NO_MATCH:
                return None
            if result == GnomeKeyring.Result.CANCELLED:
                # The user pressed "Cancel" when prompted to unlock their keyring.
                return None
            dump += item.get_display_name()
            if print_passwords:
                dump += " = " + item.get_secret()
            dump += "\n"
        return dump

    def get_password(self, service, username):
        """Get password of the username for the service
        """
        from gi.repository import GnomeKeyring

        service = self._safe_string(service)
        username = self._safe_string(username)
        attrs = GnomeKeyring.Attribute.list_new()
        GnomeKeyring.Attribute.list_append_string(attrs, 'username', username)
        GnomeKeyring.Attribute.list_append_string(attrs, 'domain', service)
        result, items = GnomeKeyring.find_items_sync(
            GnomeKeyring.ItemType.NETWORK_PASSWORD, attrs)
        if result == GnomeKeyring.Result.IO_ERROR:
            return None
        if result == GnomeKeyring.Result.NO_MATCH:
            return None
        if result == GnomeKeyring.Result.CANCELLED:
            # The user pressed "Cancel" when prompted to unlock their keyring.
            return None

        assert len(items) == 1, 'no more than one entry should ever match'
        secret = items[0].secret
        return secret if isinstance(secret, unicode) else secret.decode('utf-8')

    def set_password(self, service, username, password):
        """Set password for the username of the service
        """
        from gi.repository import GnomeKeyring

        service = self._safe_string(service)
        username = self._safe_string(username)
        password = self._safe_string(password)
        attrs = GnomeKeyring.Attribute.list_new()
        GnomeKeyring.Attribute.list_append_string(attrs, 'username', username)
        GnomeKeyring.Attribute.list_append_string(attrs, 'domain', service)
        result = GnomeKeyring.item_create_sync(
            self.KEYRING_NAME, GnomeKeyring.ItemType.GENERIC_SECRET,
            "%s (%s)" % (service, username),

            attrs, password, True)[0]
        if result == GnomeKeyring.Result.CANCELLED:
            # The user pressed "Cancel" when prompted to unlock their keyring.
            raise PasswordSetError("Cancelled by user")

    def set_password(self, service, username, password, url, notes):
        """Set password for the username of the service
        """
        from gi.repository import GnomeKeyring

        service = self._safe_string(service)
        username = self._safe_string(username)
        password = self._safe_string(password)
        url = self._safe_string(url)
        notes = self._safe_string(notes)
        attrs = GnomeKeyring.Attribute.list_new()
        GnomeKeyring.Attribute.list_append_string(attrs, 'username', username)
        GnomeKeyring.Attribute.list_append_string(attrs, 'domain', service)
        GnomeKeyring.Attribute.list_append_string(attrs, 'url', url)
        GnomeKeyring.Attribute.list_append_string(attrs, 'notes', notes)
        result = GnomeKeyring.item_create_sync(
            self.KEYRING_NAME, GnomeKeyring.ItemType.GENERIC_SECRET,
            "%s (%s)" % (service, username),
            attrs, password, True)[0]
        if result == GnomeKeyring.Result.CANCELLED:
            # The user pressed "Cancel" when prompted to unlock their keyring.
            raise PasswordSetError("Cancelled by user")

    def delete_password(self, service, username):
        """Delete the password for the username of the service.
        """
        from gi.repository import GnomeKeyring
        attrs = GnomeKeyring.Attribute.list_new()
        GnomeKeyring.Attribute.list_append_string(attrs, 'username', username)
        GnomeKeyring.Attribute.list_append_string(attrs, 'domain', service)
        result, items = GnomeKeyring.find_items_sync(
            GnomeKeyring.ItemType.NETWORK_PASSWORD, attrs)
        if result == GnomeKeyring.Result.NO_MATCH:
            raise PasswordDeleteError("Password not found")
        for current in items:
            result = GnomeKeyring.item_delete_sync(current.keyring,
                                                   current.item_id)
            if result == GnomeKeyring.Result.CANCELLED:
                raise PasswordDeleteError("Cancelled by user")

    def _safe_string(self, source, encoding='utf-8'):
        """Convert unicode to string as gnomekeyring barfs on unicode"""
        if not isinstance(source, str):
            return source.encode(encoding)
        return str(source)
