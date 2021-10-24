import os

from conans import ConanFile
from conans.client.tools.apple import is_apple_os
from conans.model import Middleware


"""
An example middleware that performs code signing

Add to settings.yml:

codesign_identity: [None, ANY]
codesign_flags: [None, ANY]

Or as options:

Add to profile (middleware is a reference like build_requires):

[settings]
codesign_identity=Garrick Meeker
[middleware_requires]
codesign/0.1@
[middleware]
codesign
[env]

As options:

[options]
codesign:identity=Garrick Meeker

Or:
copy to ~/.conan/middleware/codesign.py
The ConanFile part can be removed, and [middleware_required] is not used:

[settings]
codesign_identity=Garrick Meeker
[middleware]
codesign
[env]

[middleware] and [middleware_requires] can be applied to specific recipes, like build requirements:

[middleware_requires]
 my_pkg*: codesign/0.1@
 &: codesign/0.1@
 &!: codesign/0.1@
[middleware]
 my_pkg*: codesign
 &: codesign
 &!: codesign

"""

# The middleware name will be the literal class name (not the filename)
class codesign(Middleware):
    settings = "os", "codesign_identity", "codesign_flags"
    options = {"identity": [None, "ANY"], "flags": [None, "ANY"]}
    default_options = {"identity": None, "flags": None}

    @property
    def identity(self):
        return self.settings.codesign_identity or self.options.identity

    @property
    def flags(self):
        return self.settings.codesign_flags or self.options.flags

    def should_apply(self, base):
        if not Middleware.is_binary(base):
            return False
        if not self.identity:
            return False
        if self.settings.os == "Windows":
            return True
        if is_apple_os(self.settings.os):
            return True
        return False

    def __call__(self, base):
        class CodeSignConan(base):
            # Some settings might only be used in 'should_apply' but we use all here
            settings = Middleware.extend(base.settings, codesign.settings)
            options = Middleware.extend(base.options, codesign.options)
            default_options = Middleware.extend(base.default_options, codesign.default_options)

            @property
            def identity(self):
                return self.settings.codesign_identity or self.options.identity

            @property
            def flags(self):
                return self.settings.codesign_flags or self.options.flags

            def package(self):
                # TODO: Find macOS packages, app bundles, and single executables
                super(CodeSignConan, self).package()
                if not Middleware.is_binary(self):
                    return
                cmd = None
                identity = self.identity
                flags = self.flags or ""
                exts = []
                if identity:
                    identity = str(identity)
                    if self.settings.os == "Windows":
                        cmd = "signtool sign /n"
                        exts = [".dll", ".exe"]
                    elif is_apple_os(self.settings.os):
                        identity = "Developer ID Application: " + identity
                        cmd = "codesign -s "
                        exts = [".dylib"]
                if cmd:
                    for root, dirs, files in os.walk(self.package_folder):
                        for f in files:
                            path = os.path.join(root, f)
                            if os.path.splitext(path)[1] in exts and not os.path.islink(path):
                                self.run(cmd + '"{}" {} {}'.format(identity, flags, path))

        return CodeSignConan

class CodesignPackage(ConanFile):
    name = "codesign"
    version = "0.1"
    build_policy = "missing"
