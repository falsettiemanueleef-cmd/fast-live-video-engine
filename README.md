# FAST LIVE — Cloud MP4 test

This repository contains a minimal GitHub Actions test that renders a real MP4 in GitHub's cloud runner. It does not publish to YouTube and does not need API keys.

## Run from Android

1. Open the repository on GitHub.
2. Open the Actions tab.
3. If GitHub asks, enable workflows for this repository.
4. Select FAST LIVE - Cloud MP4 test.
5. Tap Run workflow, then confirm.
6. When the run finishes successfully, open it and download the fastlive-cloud-test artifact.

## What this test verifies

- A GitHub-hosted Ubuntu runner starts.
- FFmpeg renders a 15-second vertical 1080×1920 MP4.
- FFprobe can read the generated video.
- GitHub stores the MP4 as a downloadable artifact for 2 days.

## Costs and limits

The workflow is manual only (workflow_dispatch): it does not run on a schedule and does not publish anything. GitHub Actions usage may be subject to account plan limits. Check Settings → Billing and licensing → Usage before enabling any paid extra usage. Do not add a payment method or enable paid overages for this test.

## Scope

This is only a cloud-rendering proof of concept. It does not yet include AI generation, English voice-over, automatic editing, YouTube OAuth, or publishing.
