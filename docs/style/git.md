# Git Style

## Commit Format

Format: `<prefix>: <description>`

The description shall describe what is done in the commit. Phrase the description in simple tense, eg. “add xyz” instead of “added xyz”. An optional body and/or signature is allowed. The valid commit prefixes are the following:

- Changes in code
    - **feat**: Introduces a new feature.
    - **fix**: Patches a bug.
    - **refactor**: A code change that neither fixes a bug nor adds a feature.
    - **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc).
    - **perf**: Improves performance.
- Other
    - **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation.
    - **docs**: Documentation-only changes.
    - **test**: Adds missing tests or corrects existing tests.
