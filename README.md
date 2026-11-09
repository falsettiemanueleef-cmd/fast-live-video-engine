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

The first workflow is a cloud-rendering proof of concept. The separate English voice-over workflow is configured but must still be executed and verified; neither workflow publishes to YouTube.


## English voice-over pipeline test

A second cloud workflow tests an English neural voice-over and combines it with a vertical MP4. It uses Piper TTS and the LibriTTS-R voice model. The upstream model card is downloaded into the artifact for manual licence and attribution review. Commercial-use rights are not assumed; verify the model and underlying voice-data terms before any commercial deployment.

The workflow is manual only (`workflow_dispatch`); it does not run automatically. It does not publish to YouTube and requires no API key or payment method. GitHub Actions plan limits still apply.

Run: Actions → FAST LIVE - English voice and MP4 test → Run workflow.

The narration is currently a prepared test script, not AI-generated copy. This verifies neural TTS and video assembly only; automated AI script generation remains a separate step.
