## LTX Video Generation Experiments

This repository explores long-form audio–video generation using Lightricks LTX models on Replicate.

### Aim

Generate 15–30s short-form videos (ads / narratives)

Compare scene-based seeded generation vs single-prompt generation

Study temporal continuity and audio–visual alignment

### Models

LTX Fast – faster, better temporal consistency

LTX Pro – higher capacity, more cinematic but stylized

Both share the same core audio–visual diffusion architecture.

### Approaches

Seeded scenes: short clips chained via last-frame seeding (more realistic cuts)

Single prompt: one continuous generation (smoother but more AI-stylized)
