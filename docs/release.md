# Create a new release

This project is published through GitHub Releases.

## Stable release

1. Update the version in `pyproject.toml`.
2. Commit and push your changes.
3. Create the release with the GitHub CLI:

   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z"
   ```

   Example:

   ```bash
   gh release create v1.0.5 --title "v1.0.5"
   ```

4. Publish the release.

GitHub Actions will then:
- build the package
- publish it to PyPI

## Pre-release

1. Update the version in `pyproject.toml`.
2. Commit and push your changes.
3. Create the pre-release with the GitHub CLI:

   ```bash
   gh release create vX.Y.Zrc1 --title "vX.Y.Zrc1" --prerelease
   ```

   Example:

   ```bash
   gh release create v1.1.0rc1 --title "v1.1.0rc1" --prerelease
   ```

4. Publish the release.

GitHub Actions will then:
- build the package
- publish it to TestPyPI

## Notes

- The workflow uses the GitHub release tag as the published version.
- Tags should start with `v`.
- Release automation is defined in `.github/workflows/release.yml`.
