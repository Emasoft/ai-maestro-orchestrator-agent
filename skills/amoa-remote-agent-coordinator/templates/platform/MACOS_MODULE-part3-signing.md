# macOS Module: Code Signing & Notarization

This document covers macOS code signing and notarization requirements. This is Part 3 of the macOS Platform Module documentation.

**Prerequisites**: Read [Part 2: Build Configuration](./MACOS_MODULE-part2-build.md) first.

---

## Code Signing & Notarization

### Code Signing

Required for distribution outside development:

```yaml
code_signing:
  identity: "{{SIGNING_IDENTITY}}"
  team_id: "{{TEAM_ID}}"
  entitlements_file: "{{ENTITLEMENTS_PLIST}}"

  sign_command: |
    codesign \
      --sign "{{SIGNING_IDENTITY}}" \
      --timestamp \
      --options runtime \
      --entitlements "{{ENTITLEMENTS_PLIST}}" \
      --force \
      "{{BINARY_PATH}}"

  verify_command: |
    codesign --verify --verbose "{{BINARY_PATH}}"
```

**Variables**:
- `{{SIGNING_IDENTITY}}`: Code signing certificate (e.g., "Developer ID Application: Company Name (TEAM_ID)")
- `{{TEAM_ID}}`: Apple Developer Team ID (10-character string)
- `{{ENTITLEMENTS_PLIST}}`: Path to entitlements file (e.g., "entitlements.plist")
- `{{BINARY_PATH}}`: Path to binary to sign

**Example Entitlements File** (`entitlements.plist`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Hardened Runtime -->
    <key>com.apple.security.cs.allow-jit</key>
    <{{JIT_REQUIRED}}/>

    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <{{UNSIGNED_EXEC_REQUIRED}}/>

    <key>com.apple.security.cs.disable-library-validation</key>
    <{{DISABLE_LIB_VALIDATION}}/>

    <!-- Network Access -->
    <key>com.apple.security.network.client</key>
    <{{NETWORK_CLIENT}}/>

    <key>com.apple.security.network.server</key>
    <{{NETWORK_SERVER}}/>

    <!-- File System Access -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <{{USER_SELECTED_FILES}}/>

    <key>com.apple.security.files.downloads.read-write</key>
    <{{DOWNLOADS_ACCESS}}/>
</dict>
</plist>
```

### Notarization

Required for distribution outside App Store:

```yaml
notarization:
  apple_id: "{{APPLE_ID}}"
  team_id: "{{TEAM_ID}}"
  app_specific_password: "{{APP_PASSWORD}}"  # Store in Keychain

  submit_command: |
    xcrun notarytool submit \
      "{{BINARY_PATH}}" \
      --apple-id "{{APPLE_ID}}" \
      --team-id "{{TEAM_ID}}" \
      --password "{{APP_PASSWORD}}" \
      --wait

  staple_command: |
    xcrun stapler staple "{{BINARY_PATH}}"

  verify_command: |
    spctl -a -v "{{BINARY_PATH}}"
```

**Notarization Workflow**:
```bash
#!/bin/bash
set -e

BINARY_PATH="{{BINARY_PATH}}"
APPLE_ID="{{APPLE_ID}}"
TEAM_ID="{{TEAM_ID}}"

# Get app-specific password from Keychain
APP_PASSWORD=$(security find-generic-password -a "${APPLE_ID}" -s "notarization-password" -w)

# Create ZIP for notarization (required format)
echo "Creating archive..."
ditto -c -k --keepParent "${BINARY_PATH}" "${BINARY_PATH}.zip"

# Submit for notarization
echo "Submitting for notarization..."
xcrun notarytool submit \
  "${BINARY_PATH}.zip" \
  --apple-id "${APPLE_ID}" \
  --team-id "${TEAM_ID}" \
  --password "${APP_PASSWORD}" \
  --wait

# Staple notarization ticket
echo "Stapling ticket..."
xcrun stapler staple "${BINARY_PATH}"

# Verify
echo "Verifying..."
spctl -a -v "${BINARY_PATH}"

echo "Notarization complete"
```

---

## Next Parts

- [Part 4: Testing & Platform APIs](./MACOS_MODULE-part4-testing-apis.md)
- [Part 5: CI/CD & Troubleshooting](./MACOS_MODULE-part5-cicd-troubleshooting.md)
