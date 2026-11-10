"""Resize and optimize validated images before R2 upload."""

import io
import math

from PIL import ExifTags, Image, ImageOps, features

from .config import fail

MAX_UPLOAD_WIDTH = 500
MAX_RESIZED_ANIMATION_PIXELS = 32_000_000


def prepare_image(image):
	image = ImageOps.exif_transpose(image)
	mode = "RGBA" if "A" in image.getbands() or "transparency" in image.info else "RGB"
	profile = image.info.get("icc_profile")
	if profile:
		from PIL import ImageCms

		try:
			image = ImageCms.profileToProfile(
				image,
				ImageCms.ImageCmsProfile(io.BytesIO(profile)),
				ImageCms.createProfile("sRGB"),
				outputMode=mode,
			)
		except (ImageCms.PyCMSError, OSError, ValueError):
			# Invalid profiles are ignored by browsers too; use the normal mode conversion.
			image = image.convert(mode)
	else:
		image = image.convert(mode)
	# Rotation has been applied and colors converted. Drop EXIF/GPS/XMP/ICC metadata.
	image.info.clear()
	return image


def encode_webp(image, quality):
	stream = io.BytesIO()
	image.save(stream, format="WEBP", quality=quality, method=4, exact=True)
	return stream.getvalue()


def resize_image(image, config):
	image = prepare_image(image)
	max_dimension = config.optimize_max_dimension
	image.thumbnail((min(MAX_UPLOAD_WIDTH, max_dimension), max_dimension), Image.Resampling.LANCZOS)
	return image


def static_webp(image, config):
	image = resize_image(image, config)
	quality_floor = min(config.optimize_quality, 65)
	qualities = sorted(
		{config.optimize_quality, max(quality_floor, config.optimize_quality - 10), quality_floor},
		reverse=True,
	)
	best = None
	for quality in qualities:
		candidate = encode_webp(image, quality)
		if best is None or len(candidate) < len(best):
			best = candidate
		if len(candidate) <= config.optimize_target_bytes:
			return candidate
	# Difficult images get smaller dimensions, with a 640px longest-edge floor (or
	# their existing size if smaller). The target is best effort, not a reason to
	# reduce a product image to an unusable thumbnail. Never upscale the source.
	minimum_edge = min(640, max(image.size))
	for _ in range(4):
		if max(image.size) <= minimum_edge:
			break
		factor = min(0.85, math.sqrt(config.optimize_target_bytes / len(best)) * 0.95)
		edge = max(minimum_edge, int(max(image.size) * factor))
		image.thumbnail((edge, edge), Image.Resampling.LANCZOS)
		candidate = encode_webp(image, quality_floor)
		if len(candidate) < len(best):
			best = candidate
		if len(candidate) <= config.optimize_target_bytes:
			break
	return best


def animated_webp(image, config):
	Image.init()
	if "WEBP" not in Image.SAVE_ALL:
		raise OSError("Animated WebP encoder unavailable")
	loop = image.info.get("loop", 1)
	if image.format == "GIF" and image.info.get("loop"):
		# GIF counts repeats after the first play. WebP counts all plays.
		loop = min(loop + 1, 65535)
	# The optional APNG poster is outside the animation timeline.
	first_frame = int(bool(image.info.get("default_image")))
	frames = []
	durations = []
	remaining_pixels = MAX_RESIZED_ANIMATION_PIXELS
	for index in range(first_frame, image.n_frames):
		image.seek(index)
		frame = resize_image(image, config)
		remaining_pixels -= frame.width * frame.height
		if remaining_pixels < 0:
			fail("This animation has too many pixels to resize safely. Upload a shorter or smaller image.")
		frames.append(frame)
		durations.append(round(image.info.get("duration", 0)))

	stream = io.BytesIO()
	frames[0].save(
		stream,
		format="WEBP",
		save_all=True,
		append_images=frames[1:],
		duration=durations,
		loop=loop,
		quality=config.optimize_quality,
	)
	return stream.getvalue()


def optimize_image(content, image_format, config):
	should_optimize = config.optimize_images and len(content) >= config.optimize_threshold_bytes
	failed = False
	try:
		with Image.open(io.BytesIO(content)) as image:
			orientation = image.getexif().get(ExifTags.Base.Orientation)
			display_width = image.height if orientation in (5, 6, 7, 8) else image.width
			# Enforce the cap on the stored raster even if EXIF would rotate it later.
			must_resize = max(image.width, display_width) > MAX_UPLOAD_WIDTH
			is_animated = getattr(image, "is_animated", False)
			if not must_resize and (is_animated or not should_optimize):
				return content, image_format
			if not features.check("webp"):
				raise OSError("WebP encoder unavailable")
			optimized = animated_webp(image, config) if is_animated else static_webp(image, config)
	except (OSError, ValueError, ImportError):
		failed = True
	if failed:
		fail("Image optimization failed. Check the image and Pillow WebP encoder support.")
	if not must_resize and len(optimized) >= len(content):
		return content, image_format
	return optimized, ("webp", "image/webp")
