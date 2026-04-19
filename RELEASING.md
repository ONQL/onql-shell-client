# Releasing ONQL Shell

Releases are automated. PyInstaller builds a single-file binary for Linux, Windows, and macOS (Intel + Apple Silicon), and the GitHub Actions workflow publishes them to the Releases page on tag push.

## Cut a release

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow in `.github/workflows/release.yml` runs on the tag and:

1. Spins up four runners in parallel: Ubuntu (Linux x86_64), Windows (x86_64), macOS-13 (Intel), macOS-14 (Apple Silicon).
2. Installs Python 3.11 + requirements + PyInstaller on each.
3. Runs `pyinstaller --onefile --name onql main.py` → produces a single `onql` binary (or `onql.exe` on Windows) with all Python deps bundled.
4. Packages each into `onql-shell_<version>_<os>_<arch>.tar.gz` (Unix) or `.zip` (Windows).
5. Collects all artifacts into one GitHub Release, with a SHA-256 `checksums.txt`.

## Output formats

| Platform | Architecture | Format |
|---|---|---|
| Linux | x86_64 | `.tar.gz` |
| Windows | x86_64 | `.zip` |
| macOS | x86_64 (Intel) | `.tar.gz` |
| macOS | arm64 (Apple Silicon) | `.tar.gz` |

Linux arm64 and Windows MSI will be added later.

## Versioning

Semver: `v<MAJOR>.<MINOR>.<PATCH>`. Pre-release suffixes (`v0.2.0-rc.1`) are auto-marked as prereleases by the workflow.

## Local dry-run

```bash
pip install pyinstaller
pyinstaller --onefile --name onql --clean main.py
./dist/onql
```

## Size notes

PyInstaller bundles the Python interpreter + every dependency. The resulting binary is typically 20–40 MB. If it gets bigger than ~60 MB, check `requirements.txt` for accidentally-added heavy packages.

## Troubleshooting

- **"tag already exists"** — `git tag -d v0.1.0 && git push origin :refs/tags/v0.1.0`.
- **Windows build fails with "missing DLL"** — a dep uses C extensions that PyInstaller didn't catch. Add `--hidden-import=<module>` to the pyinstaller command.
- **Apple Silicon binary crashes with "bad CPU type"** — someone downloaded the Intel build on an M-series Mac. Document download URLs clearly on the release page.
- **Antivirus flags the Windows binary** — PyInstaller single-files sometimes trigger heuristics. Code signing (separate setup, not included yet) fixes this.
