import os

from keyring.backend import KeyringBackend
from keyring.errors import PasswordDeleteError
from keyring.errors import PasswordSetError

try:
    from PyKDE4.kdeui import KWallet
    from PyQt4 import QtGui
except ImportError:
    kwallet_support = False
else:
    kwallet_support = True

kwallet = None

def open_kwallet(kwallet_module=None, qt_module=None):

    # If we specified the kwallet_module and/or qt_module, surely we won't need
    # the cached kwallet object...
    if kwallet_module is None and qt_module is None:
        global kwallet
        if not kwallet is None:
            return kwallet

    # Allow for the injection of module-like objects for testing purposes.
    if kwallet_module is None:
        kwallet_module = KWallet.Wallet
    if qt_module is None:
        qt_module = QtGui

    # KDE wants us to instantiate an application object.
    app = None
    if qt_module.qApp.instance() == None:
        app = qt_module.QApplication([])
    try:
        window = qt_module.QWidget()
        kwallet = kwallet_module.openWallet(
            kwallet_module.NetworkWallet(),
            window.winId(),
            kwallet_module.Synchronous)
        if kwallet is not None:
            if not kwallet.hasFolder('Python'):
                kwallet.createFolder('Python')
            kwallet.setFolder('Python')
            return kwallet
    finally:
        if app:
            app.exit()

class Keyring(KeyringBackend):
    """KDE KWallet"""

    def supported(self):
        if kwallet_support and 'KDE_SESSION_UID' in os.environ:
            return 1
        elif kwallet_support:
            return 0
        else:
            return -1
    
    def dump(self, print_passwords=False):
        """Get all keyring entries (with or without passwords)
        """
        # TODO: Implementation
        print "To be implemented"
        return None

    def get_password(self, service, username):
        """Get password of the username for the service
        """
        key = username + '@' + service
        network = KWallet.Wallet.NetworkWallet()
        wallet = open_kwallet()
        if wallet is None:
            # the user pressed "cancel" when prompted to unlock their keyring.
            return None
        if wallet.keyDoesNotExist(network, 'Python', key):
            return None

        result = wallet.readPassword(key)[1]
        # The string will be a PyQt4.QtCore.QString, so turn it into a unicode
        # object.
        return unicode(result)

    def set_password(self, service, username, password):
        """Set password for the username of the service
        """
        wallet = open_kwallet()
        if wallet is None:
            # the user pressed "cancel" when prompted to unlock their keyring.
            raise PasswordSetError("Cancelled by user")
        wallet.writePassword(username+'@'+service, password)

    def set_password(self, service, username, password, url, notes):
        """Set password for the username of the service
        """
        # TODO: Implementation
        print "To be implemented"
        return None 

    def delete_password(self, service, username):
        """Delete the password for the username of the service.
        """
        key = username + '@' + service
        wallet = open_kwallet()
        if wallet is None:
            # the user pressed "cancel" when prompted to unlock their keyring.
            raise PasswordDeleteError("Cancelled by user")
        if wallet.keyDoesNotExist(wallet.walletName(), 'Python', key):
            raise PasswordDeleteError("Password not found")
        wallet.removeEntry(key)
