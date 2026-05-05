# Agent Gram iOS Bootstrap

This repository is a public fork of `TelegramMessenger/Telegram-iOS` with a thin project-specific bootstrap layer for Ethan's fork, `Agent Gram iOS`.

The goal of this document is to get a local developer machine from "fresh clone" to "Telegram login screen opens in the iOS Simulator" without committing secrets or diverging far from upstream.

## Current local status

Observed in `/Users/ethansk/Projects/AgentGram-iOS` on 2026-05-05:

- Full Xcode is installed at `/Applications/Xcode.app`.
- The pinned Bazel binary has been fetched under `build-input/` by the project-generation path.
- `scripts/agentgram/build-run-simulator.sh` can build the debug simulator IPA, unpack it, install it, and launch it on an iPhone Simulator.
- The iPhone 17 Simulator reaches the Telegram welcome / phone-number login flow using the local ignored config at `build-input/agentgram/development.local.json`.
- `scripts/agentgram/smoke-simulator.py` runs the safe Bazel/XCTest UI smoke test up to Telegram's phone-number confirmation screen.

Telegram account authentication is intentionally not automated by default. The smoke test stops before the final confirmation tap that can request a real Telegram login code.

## Telegram constraints

Telegram's upstream README requires the following for forks and third-party clients:

- Do not ship the app as `Telegram` without making it clearly unofficial.
- Do not use the standard Telegram logo.
- Publish your source code to comply with the licenses.
- Protect user privacy and follow Telegram security guidance.
- Obtain your own `api_id` and `api_hash` for this app.

For Agent Gram iOS, that means:

- Use `Agent Gram iOS` or another clearly unofficial product name in user-facing branding.
- Replace Telegram branding assets before App Store distribution.
- Do not commit Telegram API credentials, Apple credentials, phone numbers, or login codes.

## One-time local setup

### 1. Install full Xcode

Install the full Xcode app, not just Command Line Tools.

Options:

- App Store: install Xcode manually.
- Apple Developer downloads: install the current full release that matches [`versions.json`](../versions.json), currently `26.4`.

After installation:

```bash
open /Applications/Xcode.app
```

Then complete the first-launch prompts so Xcode installs its bundled components.

If Terminal still points at Command Line Tools afterwards, switch the active developer directory:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

If you do not have admin access, use a per-shell override instead:

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
```

Verify:

```bash
xcodebuild -version
xcode-select -p
```

Expected outcome:

- `xcodebuild -version` succeeds.
- The selected developer directory resolves inside `/Applications/Xcode.app/...`.
- Xcode version matches `26.4`, or you consciously use `--overrideXcodeVersion`.

### 2. Prepare a local Telegram development config

Create a local-only config file from the upstream template:

```bash
./scripts/agentgram/init-local-config.sh
```

Default output:

```text
build-input/agentgram/development.local.json
```

That path is already ignored by the repository's existing `build-input/*` rule in [`.gitignore`](../.gitignore).

Now edit the generated file and fill in these fields:

- `bundle_id`: a unique bundle identifier for this fork, for example `com.ethansk.agentgram`
- `api_id`: your Telegram application ID from `https://my.telegram.org/apps`
- `api_hash`: your Telegram application hash from `https://my.telegram.org/apps`
- `team_id`: your Apple Developer Team ID

This is the exact place where `api_id` and `api_hash` belong for local development:

```text
build-input/agentgram/development.local.json
```

Do not put real credentials in tracked files under `build-system/`.

### 3. Generate the Xcode project

Recommended path for this repo:

```bash
python3 build-system/Make/Make.py \
  --cacheDir="$HOME/telegram-bazel-cache" \
  generateProject \
  --configurationPath=build-input/agentgram/development.local.json \
  --xcodeManagedCodesigning \
  --disableProvisioningProfiles
```

Notes:

- `Make.py` will fetch the pinned Bazel binary automatically if needed.
- `--disableProvisioningProfiles` keeps the initial run focused on simulator-only work.
- `--xcodeManagedCodesigning` is the least invasive path for local development when you have a valid Apple team configured in Xcode.
- The older [`build-system/generate-xcode-project.sh`](../build-system/generate-xcode-project.sh) script expects `bazel` in `PATH`; prefer `Make.py` for this fork bootstrap.

### 4. Install an iOS simulator runtime if needed

If Xcode opens but no iOS Simulator destination is available:

1. Open Xcode.
2. Go to `Xcode > Settings > Platforms`.
3. Install at least one iOS runtime.
4. Open `Window > Devices and Simulators` and confirm a simulator exists.

### 5. Build and run in the simulator

For the local simulator loop, use the helper script rather than opening Xcode manually:

```bash
./scripts/agentgram/build-run-simulator.sh
```

The script:

- uses `build-input/agentgram/development.local.json` by default
- builds `Telegram/Telegram` for `sim_arm64`
- unpacks `bazel-bin/Telegram/Telegram.ipa` into `build-output/sim-install/`
- boots a preferred iPhone Simulator if needed
- installs and launches the app bundle

Override the simulator if needed:

```bash
SIMULATOR_UDID=<device-udid> ./scripts/agentgram/build-run-simulator.sh
```

Reset the app's simulator data before installing when you want a clean login flow:

```bash
RESET_APP=1 ./scripts/agentgram/build-run-simulator.sh
```

### 6. Device builds and App Store readiness

Do not treat the simulator-only setup as App Store-ready.

Before App Store or TestFlight work, you still need:

- final branding that is not Telegram branding
- production signing and provisioning strategy
- privacy review for stored user data and logs
- a release bundle ID and App Store metadata
- review of any upstream license and compliance obligations

## Helper scripts

### Check prerequisites

```bash
./scripts/agentgram/check-prereqs.sh
```

This reports:

- selected developer directory
- whether full Xcode is present
- detected Xcode version
- required Xcode and Bazel versions from `versions.json`
- presence of Python, Swift, and `curl`
- whether submodules look initialized
- whether the local Agent Gram iOS config file exists

### Initialize local config

```bash
./scripts/agentgram/init-local-config.sh
```

Optional custom output path:

```bash
./scripts/agentgram/init-local-config.sh /tmp/agentgram-dev.json --force
```

### Build, install, and launch the simulator app

```bash
./scripts/agentgram/build-run-simulator.sh
```

This is the fastest repeatable route for the current fork because it avoids Xcode UI state and directly uses the pinned Bazel toolchain.

Use `RESET_APP=1` to wipe the app's simulator data before reinstalling.

### Smoke-test the simulator login flow

Run the safe XCTest smoke test:

```bash
./scripts/agentgram/smoke-simulator.py
```

The script runs `UITests/testPhoneConfirmation` via Bazel. It drives the app from the welcome screen to Telegram's phone-number confirmation screen using accessibility identifiers, then stops before any login-code request.

Override the XCTest filter only when you intentionally want a different test:

```bash
TEST_FILTER=UITests/testLaunch ./scripts/agentgram/smoke-simulator.py
```

## Safe verification performed locally

Verified on 2026-05-05:

- repository is on `master`
- submodules are initialized
- `versions.json` pins Xcode `26.4` and Bazel `8.4.2`
- debug simulator Bazel build completes successfully
- `bazel-bin/Telegram/Telegram.ipa` is produced
- the IPA unpacks to `build-output/sim-install/Payload/Telegram.app`
- the app installs and launches on the iPhone 17 Simulator
- the app reaches the welcome screen, phone-entry screen, and phone-confirmation screen under Bazel/XCTest

Still not performed by default:

- requesting a real Telegram login code
- completing Telegram account authentication
- device build / signing verification
