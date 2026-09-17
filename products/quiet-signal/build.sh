#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
task_start=$(date +%s)
task_target="$(uname -m)-apple-macosx14.0"
xcrun swiftc -target "$task_target" -module-cache-path /tmp/quiet-signal-swift-cache -swift-version 5 -O Core.swift CoreTests.swift -o build/core-tests
build/core-tests
xcrun swiftc -target "$task_target" -module-cache-path /tmp/quiet-signal-swift-cache -swift-version 5 -O Core.swift Camera.swift Journal.swift PipelineTests.swift -o build/pipeline-tests -framework AVFoundation -framework Vision -framework CryptoKit
build/pipeline-tests
xcrun swiftc -target "$task_target" -module-cache-path /tmp/quiet-signal-swift-cache -swift-version 5 -O Core.swift Journal.swift SessionSupport.swift SessionSupportTests.swift -o build/session-tests -framework CryptoKit
build/session-tests
app='build/Quiet Signal.app'
mkdir -p "$app/Contents/MacOS"
xcrun swiftc -target "$task_target" -module-cache-path /tmp/quiet-signal-swift-cache -swift-version 5 -O -parse-as-library Core.swift Camera.swift Journal.swift SessionSupport.swift App.swift -o build/QuietSignal-next -framework SwiftUI -framework AppKit -framework AVFoundation -framework Vision -framework CryptoKit
mv build/QuietSignal-next "$app/Contents/MacOS/QuietSignal"
cat > "$app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>QuietSignal</string>
<key>CFBundleIdentifier</key><string>org.neurodecodekit.quietsignal</string>
<key>CFBundleName</key><string>Quiet Signal</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>0.2</string>
<key>LSMinimumSystemVersion</key><string>14.0</string>
<key>NSCameraUsageDescription</key><string>Quiet Signal tests whether local camera features correlate with your silent YES/NO choices. Audio and video recordings are not saved.</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
codesign --force --sign - --timestamp=none "$app"
printf 'Build seconds: %s\n' "$(( $(date +%s)-task_start ))"
du -sh "$app"
