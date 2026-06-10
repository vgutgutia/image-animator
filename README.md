# Image Animator

First-order motion synthesis with the safety rails built in from day one. An educational deepfake project about understanding synthetic media, not making it.

**Live demo:** [animate.spbdatascience.org](https://animate.spbdatascience.org)

## What it does

Upload a still image, pick a motion preset (talking, nodding, smiling, cinematic pan), and a first-order motion model on the club's RTX 5080 warps the image to follow that motion, frame by frame.

## Why a school club built a deepfake tool

Synthetic media is not going away, and the most reliable way to learn its tells (warped backgrounds, texture shimmer, artifacts around ears and teeth during fast motion) is to see the pipeline from the inside. The project treats the safeguards as part of the curriculum:

- A mandatory ethics gate before first use: no real people without consent, no deception
- Visible watermark on all output, marking it AI-generated
- Server-side job logging
- A media-literacy guide on the page covering how to spot keypoint-model artifacts

## Architecture

The Flask app on the VPS validates uploads and proxies jobs to the GPU worker over a private Tailscale network. When the worker is offline the UI says so honestly instead of queueing into the void.

## Stack

Python, Flask, first-order motion model (GPU worker), Tailscale

## Local development

```bash
pip install flask requests
python app.py
```
