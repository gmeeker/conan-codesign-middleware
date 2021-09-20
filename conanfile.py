import os

from conans import ConanFile
from conans.client.tools.apple import is_apple_os
from conans.model import Middleware


"""
An example middleware that performs code signing

Add to settings.yml:

codesign_identity: [None, ANY]
codesign_flags: [None, ANY]

Add to profile (middleware is a reference like build_requires):

[settings]
codesign_identity=Garrick Meeker
[middleware]
codesign/0.1@
[env]

Or:
copy to ~/.conan/middleware/codesign.py
The ConanFile part can be removed, and [middleware] is just a name:

[settings]
codesign_identity=Garrick Meeker
[middleware]
codesign
[env]

"""

# The middleware name will be the literal class name (not the filename)
class codesign(Middleware):
    settings_middleware = "os", "codesign_identity", "codesign_flags"

    def __init__(self, conanfile):
        super().__init__(conanfile)

    def valid(self):
        if not self.settings_middleware.codesign_identity:
            return False
        if self.settings_middleware.os == "Windows":
            return True
        if is_apple_os(self.settings_middleware.os):
            return True
        return False

    def package(self):
        # TODO: Find macOS packages, app bundles, and single executables
        self.conanfile.package()
        cmd = None
        identity = self.settings_middleware.codesign_identity
        flags = self.settings_middleware.codesign_flags or ""
        exts = []
        if identity:
            identity = str(identity)
            if self.settings_middleware.os == "Windows":
                cmd = "signtool sign /n"
                exts = [".dll", ".exe"]
            elif is_apple_os(self.settings_middleware.os):
                identity = "Developer ID Application: " + identity
                cmd = "codesign -s "
                exts = [".dylib"]
        if cmd:
            for root, dirs, files in os.walk(self.package_folder):
                for f in files:
                    path = os.path.join(root, f)
                    if os.path.splitext(path)[1] in exts and not os.path.islink(path):
                        self.run(cmd + "'{}' {} {}".format(identity, flags, path))

class CodesignPackage(ConanFile):
    name = "codesign"
    version = "0.1"
    build_policy = "missing"
