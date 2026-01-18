import replicate
import requests

OUTPUT_VIDEO = "ltx_single_20s.mp4"

PROMPT = """
A cinematic winter adventure unfolds in a single continuous sequence.
A woman wearing premium winterwear stands on a snowy mountain ridge at sunrise, soft wind moving through the fabric, distant birds faintly audible.
The camera begins behind her shoulder and slowly glides forward, revealing vast snow-covered peaks under warm golden light.
She starts walking through a snow-covered forest trail, boots crunching softly, light snow drifting through the air, the jacket resisting wind and frost naturally.
Ambient orchestral music slowly builds as the environment becomes harsher, wind growing stronger yet controlled.
The camera follows her in smooth tracking shots, highlighting the jacket’s texture, insulation, and movement in realistic lighting.
She reaches a high summit as clouds part, sunlight breaking through dramatically, snow sparkling in the air.
The camera slowly pulls back into a wide aerial view of endless winter landscapes.
 The mood is powerful, aspirational, cinematic, and inspiring, with cohesive ambient sound design and natural motion throughout.
 """


print("Generating single-shot 20s video with LTX-2...")

output = replicate.run(
    "lightricks/ltx-2-fast",
    input={
        "prompt": PROMPT,
        "duration": 20,
        "fps": 24
    }
)

# LTX returns a FileOutput object
video_url = output.url

with open(OUTPUT_VIDEO, "wb") as f:
    f.write(requests.get(video_url).content)

print("Done.")
print("Saved video:", OUTPUT_VIDEO)
