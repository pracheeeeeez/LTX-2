import os
import subprocess
import requests
import replicate
from PIL import Image

# -------------------------
# CONFIG
# -------------------------

# Pick 3 key scenes for 30s total
SCENES = [
    {
        "name": "scene 1",
        "prompt": ("A young woman stands atop a snowy cliff at sunrise, wearing a sleek short winter red jacket. Golden sunlight reflects off the snow, soft wind swirls around her, and distant birds chirp faintly. The camera starts slightly above her shoulder and glides in a smooth arc to reveal her confident expression. Snowflakes drift slowly in the air, ambient orchestral music with soft piano notes plays in the background, cinematic lighting highlights the jacket's texture and the snow's shimmer.")
    },
    {
        "name": "scene 2",
        "prompt": (
            "The woman hikes through a snowy forest trail, slow snow crunching under her boots, wearing the winter jacket. Light snow flurries blow across the frame, the fabric glistening as she adjusts her hood and zips the jacket. The camera tracks her from side and slightly above, capturing smooth, flowing motion and subtle wind movement. Background audio features gentle wind whooshing and soft piano notes which transcends into soft orchestral beats, emphasizing motion and determination."
        )
    },
    {
        "name": "scene 3",
        "prompt": (
            "The woman reaches the summit, raising her arms in triumph, sunlight piercing through clouds and illuminating her jacket. The camera slowly zooms out for a wide cinematic shot of snow-covered peaks and forests. Snowflakes sparkle in sunbeams, and a soft, uplifting orchestral crescendo with light chimes plays in the background. The mood is empowering, cinematic, and aspirational."
        )
    }
]

FPS = 24
CLIP_DURATION = 10  # seconds
OUTPUT_VIDEO = "final_video_2.mp4"

# -------------------------
# UTILS
# -------------------------

def download_file(url, output_path):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


# -------------------------
# STEP 1: INITIAL ANCHOR IMAGE
# -------------------------

def generate_anchor_image(prompt, output_path="seed_0.png"):
    print("Generating initial anchor image...")

    output = replicate.run(
        "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
        input={
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "num_outputs": 1
        }
    )

    img_url = output[0]
    img = Image.open(requests.get(img_url, stream=True).raw)
    img.save(output_path)

    return output_path


# -------------------------
# STEP 2: LTX VIDEO GENERATION
# -------------------------

def generate_scene_video(image_path, prompt, scene_idx):
    print(f"Generating video for scene {scene_idx}...")

    output = replicate.run(
        "lightricks/ltx-2-fast",
        input={
            "image": open(image_path, "rb"),
            "prompt": prompt,
            "duration": CLIP_DURATION,
            "fps": FPS
        }
    )

    # FileOutput object now returned
    video_url = output.url if hasattr(output, "url") else output

    video_path = f"scene_{scene_idx}.mp4"
    download_file(video_url, video_path)
    return video_path


# -------------------------
# STEP 3: EXTRACT LAST FRAME
# -------------------------

def extract_last_frame(video_path, output_image):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-sseof", "-0.1",
            "-i", video_path,
            "-frames:v", "1",
            "-update", "1",
            output_image
        ],
        check=True
    )


# -------------------------
# STEP 4: ORCHESTRATION
# -------------------------

def generate_full_ad():
    video_clips = []

    # Initial anchor
    seed_image = generate_anchor_image(
        SCENES[0]["prompt"],
        output_path="seed_0.png"
    )

    for idx, scene in enumerate(SCENES):
        print(f"\n--- Scene {idx + 1}: {scene['name']} ---")

        video_path = generate_scene_video(
            image_path=seed_image,
            prompt=scene["prompt"],
            scene_idx=idx
        )

        video_clips.append(video_path)

        # Prepare next seed
        next_seed = f"seed_{idx + 1}.png"
        extract_last_frame(video_path, next_seed)
        seed_image = next_seed

    return video_clips


# -------------------------
# STEP 5: CONCATENATION
# -------------------------

def concatenate_videos(video_paths, output_path):
    with open("videos.txt", "w") as f:
        for v in video_paths:
            f.write(f"file '{v}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", "videos.txt",
            "-c", "copy",
            output_path
        ],
        check=True
    )

    return output_path


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    print("Starting seeded LTX video generation pipeline...\n")

    clips = generate_full_ad()
    final_video = concatenate_videos(clips, OUTPUT_VIDEO)

    print("\n====================================")
    print("DONE")
    print("Final 30s video:", final_video)
    print("====================================")
