# Migration notes

## CrewAI security quarantine (0.46.0)

The CrewAI extra is removed from package metadata and `[all]` because its SDK graph brings unresolved ChromaDB advisories. Existing adapter modules and callable APIs remain for legacy callers, but native CrewAI support is suspended. Recreate environments using supported extras; removing an extra does not uninstall old dependencies. Restoration gates and review limits are documented in SECURITY.md. The Semantic Kernel extra separately requires Werkzeug>=3.1.9 to exclude its affected transitive versions.

## Python support by installation path

The core package remains supported on Python 3.10+. `llama-index`, `autogen`, `semantic-kernel` and `all` require Python 3.11+ because the patched Pillow 13 / dnspython 2.9 dependency versions no longer support 3.10. These fixed dependencies are unconditional: requesting an affected extra on Python 3.10 fails dependency resolution rather than silently omitting its SDK or selecting an affected older fallback. The native SDK CI matrix for these paths runs on Python 3.11 and 3.12. Other extras and core tests retain their declared Python 3.10 support.
