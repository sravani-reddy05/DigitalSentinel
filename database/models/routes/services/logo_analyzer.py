
from PIL import Image, ImageChops, ImageStat


def calculate_image_similarity(reference_path, candidate_path):
    try:
        with Image.open(reference_path) as ref_image:
            reference = ref_image.convert("RGB").resize((128, 128))

        with Image.open(candidate_path) as candidate_image:
            candidate = candidate_image.convert("RGB").resize((128, 128))

        difference = ImageChops.difference(reference, candidate)
        mean_difference = sum(
            ImageStat.Stat(difference).mean
        ) / 3

        similarity = max(0, min(100, 100 - mean_difference * 100 / 255))

        return {
            "similarity": round(similarity, 2),
            "method": "Resized pixel comparison",
            "notice": (
                "This is a basic visual similarity estimate. "
                "It may be affected by cropping, backgrounds, "
                "colors, and image transformations."
            )
        }
    except (OSError, ValueError) as error:
        return {"similarity": 0, "error": f"Unable to compare the images: {error}"}


def compare_image_upload(reference_path, upload):
    """Compare an uploaded profile/app image to the brand reference logo."""
    try:
        with Image.open(reference_path) as reference, Image.open(upload.stream) as candidate:
            ref = reference.convert("RGB").resize((128, 128))
            probe = candidate.convert("RGB").resize((128, 128))
        diff = ImageChops.difference(ref, probe)
        mean_difference = sum(ImageStat.Stat(diff).mean) / 3
        similarity = max(0, min(100, 100 - mean_difference * 100 / 255))
        return {"similarity": round(similarity, 2), "method": "Basic resized pixel comparison",
                "notice": "Visual similarity is a rough signal; crops and color changes can affect it."}
    except (OSError, ValueError) as error:
        return {
            "similarity": 0,
            "error": f"Unable to compare the images: {error}"
        }
