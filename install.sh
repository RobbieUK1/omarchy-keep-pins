#!/usr/bin/env bash
set -euo pipefail

# Install the versioned release, including its unpacked Chromium companion.
for dependency in curl tar python3 omarchy; do
  if ! command -v "$dependency" >/dev/null 2>&1; then
    printf 'Keep Pins needs %s. Install it and try again.\n' "$dependency" >&2
    exit 1
  fi
done
if [[ $(id -u) == 0 ]]; then
  printf 'Run this installer as your desktop user, without sudo.\n' >&2
  exit 1
fi
keep_pins_tmp=$(mktemp -d)
trap 'rm -rf -- "$keep_pins_tmp"' EXIT
curl --fail --silent --show-error --location --retry 3 --connect-timeout 15 --max-time 120 \
  https://github.com/RobbieUK1/omarchy-keep-pins/archive/refs/tags/v1.1.0.tar.gz \
  --output "$keep_pins_tmp/source.tar.gz"
tar -xzf "$keep_pins_tmp/source.tar.gz" --directory "$keep_pins_tmp" --no-same-owner
python3 "$keep_pins_tmp/omarchy-keep-pins-1.1.0/install.py"
