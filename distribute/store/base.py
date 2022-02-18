
class AppPackage:

    def __init__(self):
        self._package_download_url = ''
        self._fingerprint = ''
        self._bundle_identifier = ''
        self.version = 0
        self.short_version = ''
        self.release_notes = ''

    @property
    def package_download_url(self):
        return self._package_download_url

    @package_download_url.setter
    def package_download_url(self, value):
        self._package_download_url = value

    @property
    def fingerprint(self):
        return self._fingerprint

    @fingerprint.setter
    def fingerprint(self, value):
        self._fingerprint = value

    @property
    def bundle_identifier(self):
        return self._bundle_identifier

    @bundle_identifier.setter
    def bundle_identifier(self, value):
        self._bundle_identifier = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def short_version(self):
        return self._short_version

    @short_version.setter
    def short_version(self, value):
        self._short_version = value

    @property
    def release_notes(self):
        return self._release_notes

    @release_notes.setter
    def release_notes(self, value):
        self._release_notes = value

class StoreBase:
    def __init__(self, auth_data):
        pass

    @classmethod
    def name():
        return ''

    @classmethod
    def display_name():
        return ''

    @classmethod
    def icon():
        return ''

    @classmethod
    def channel():
        return ''

    def submit(self, package):
        pass

    def submit_result(self, submit_id):
        pass

    def current_version(self):
        return ''
