# CHANGELOG


## v0.2.0 (2026-02-14)

### Features

* feat: setup automatic versioning and tagging with semantic-release ([`34648fe`](https://github.com/naylsonferreira/hard-lint-py/commit/34648fe75677a283d462433d0f64a21760cd68a6))

### Fixes

* fix: remove build_command from semantic-release config ([`87b4cc0`](https://github.com/naylsonferreira/hard-lint-py/commit/87b4cc0c375371b3fd690f14e16ae5d516fdb18d))

* fix: add Poetry setup to semantic-release workflow ([`a6d92aa`](https://github.com/naylsonferreira/hard-lint-py/commit/a6d92aac4b4adec64ba983b69e529b7a51ed07a5))


## v0.1.3 (2026-02-13)

### Chores

* chore: remove test artifacts ([`390f177`](https://github.com/naylsonferreira/hard-lint-py/commit/390f1777e922668f95cb477711a913f3f902528c))

* chore: remove .hardlint generated hooks from repo ([`01f8faf`](https://github.com/naylsonferreira/hard-lint-py/commit/01f8faf7e4bdce4df50e869002cbef1ee075e762))

### Features

* feat: add validate-no-prints script and integrate with pre-commit hook ([`f1abf3a`](https://github.com/naylsonferreira/hard-lint-py/commit/f1abf3a710678b7fbc843ec8ca8b079e4103824c))

* feat: add validate-no-comments script and integrate with pre-commit hook ([`decdeb9`](https://github.com/naylsonferreira/hard-lint-py/commit/decdeb9189898b73e9c890f3591846c86ff46bf8))

* feat: prohibit print statements - add T rule to Ruff, remove all print calls ([`80daeba`](https://github.com/naylsonferreira/hard-lint-py/commit/80daeba884a88b1a9f35244d6b5469a02deb23f4))

* feat: prohibit docstrings - remove D rule enforcement from Ruff ([`ac54537`](https://github.com/naylsonferreira/hard-lint-py/commit/ac545377380442a84c773b42fe3365d5c5773967))

* feat: align Ruff, Black, isort configuration - enforce docstrings, remove conflicts ([`38b27eb`](https://github.com/naylsonferreira/hard-lint-py/commit/38b27eb36d74982131882bdc70be93296340c54d))

* feat: add docstring linting rules to enforce proper documentation over comments ([`8e6e94e`](https://github.com/naylsonferreira/hard-lint-py/commit/8e6e94e6e30e0d8a93330277379c90710926b8a7))

* feat: add test-cov command and fix coverage report format ([`735e54b`](https://github.com/naylsonferreira/hard-lint-py/commit/735e54bf2a04ebca935bb8b8edb682230f24589b))

* feat: add coverage to dev dependencies ([`dfb6d27`](https://github.com/naylsonferreira/hard-lint-py/commit/dfb6d273ac7b060379b6d669b0cbdbbc5b137f03))

* feat: add GitHub Actions workflows for CI/CD ([`f55dc7d`](https://github.com/naylsonferreira/hard-lint-py/commit/f55dc7dfabb23f6b7add700f5832ff22c0d3b668))

* feat: add Makefile with build/test/publish tasks ([`5e74ec9`](https://github.com/naylsonferreira/hard-lint-py/commit/5e74ec902972873858a0bab6f2da27a15265eba2))

* feat: test valid message ([`6f2b5db`](https://github.com/naylsonferreira/hard-lint-py/commit/6f2b5db060532395c722b73c952a2411517fc0af))

* feat: initial hard-lint-py setup with poetry ([`21673d1`](https://github.com/naylsonferreira/hard-lint-py/commit/21673d1445476865feaefa03a6a5a0d612a2a572))

### Fixes

* fix: correct import sorting in __init__.py ([`9617ced`](https://github.com/naylsonferreira/hard-lint-py/commit/9617ced43f8cc5a6b8629e01d30ecc18e4685885))

* fix: ensure all code follows established linting rules (ruff, black, isort) ([`c53e215`](https://github.com/naylsonferreira/hard-lint-py/commit/c53e21584cc02d0bb18233b483192ab7ce3583c9))

### Refactoring

* refactor: remove redundant validate-no-prints script - Ruff T rule handles it ([`d4b7da1`](https://github.com/naylsonferreira/hard-lint-py/commit/d4b7da12eac4fbc4991fdc7837dd91b196b09377))

* refactor: remove all comments from installer.py ([`94c95e2`](https://github.com/naylsonferreira/hard-lint-py/commit/94c95e25d166def6bfefb0b523d0fe0cb3a2a842))

* refactor: remove all docstrings from code - enforce no documentation comments ([`c22f7df`](https://github.com/naylsonferreira/hard-lint-py/commit/c22f7df728cc3deabd3706e45d9009e07e8374c6))

### Testing

* test: add comprehensive test suite with 99% coverage ([`74285b9`](https://github.com/naylsonferreira/hard-lint-py/commit/74285b9879ba7dc2e14ada82ea957f85654fa4e0))
