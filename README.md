# Example of Conan middleware that performs code signing

## settings.yml

```
codesign_identity: [None, ANY]
codesign_flags: [None, ANY]
```

## profile

middleware is a reference like build_requires:

```
[settings]
codesign_identity=Garrick Meeker
[middleware]
codesign/0.1@
[env]
```

## local cache

Alternatively, copy to `~/.conan/middleware/codesign.py`
The ConanFile part can be removed, and [middleware] is just the middleware name:

```
[settings]
codesign_identity=Garrick Meeker
[middleware]
codesign
[env]
```
