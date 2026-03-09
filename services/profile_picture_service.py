import re
import sys
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError


class ProfilePictureService:
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
    STORAGE_FOLDER = "profile_pictures"
    SAVE_SIZE = (200, 200)

    def get_app_base_dir(self):
        # When bundled as an EXE, save uploaded pictures beside the executable.
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parent.parent

    def get_storage_dir(self):
        storage_dir = self.get_app_base_dir() / self.STORAGE_FOLDER
        storage_dir.mkdir(parents=True, exist_ok=True)
        return storage_dir

    def save_profile_picture(self, source_path, filename_hint="student"):
        source = Path(source_path)
        extension = source.suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "message": "Unsupported image format. Please choose a JPG, JPEG, or PNG file.",
            }

        destination = self.get_storage_dir() / f"{self._sanitize_filename_hint(filename_hint)}_{uuid.uuid4().hex[:10]}.png"

        try:
            with Image.open(source) as image:
                prepared = self._prepare_image(image, self.SAVE_SIZE)
                prepared.save(destination, format="PNG")
        except FileNotFoundError:
            return {"success": False, "message": "The selected image file could not be found."}
        except (UnidentifiedImageError, OSError):
            return {"success": False, "message": "The selected file is not a valid image."}

        return {
            "success": True,
            "relative_path": destination.relative_to(self.get_app_base_dir()).as_posix(),
            "full_path": str(destination),
        }

    def load_profile_picture(self, relative_path, size=(150, 150)):
        if not relative_path:
            return {"success": False, "message": "No profile picture uploaded yet.", "image": None}

        image_path = self.resolve_profile_picture(relative_path)
        if not image_path.exists():
            return {"success": False, "message": "Saved profile picture file is missing.", "image": None}

        try:
            with Image.open(image_path) as image:
                return {
                    "success": True,
                    "image": self._prepare_image(image, size),
                    "full_path": str(image_path),
                }
        except (UnidentifiedImageError, OSError):
            return {"success": False, "message": "Could not load the saved profile picture.", "image": None}

    def delete_profile_picture(self, relative_path):
        if not relative_path:
            return

        image_path = self.resolve_profile_picture(relative_path)
        try:
            if image_path.exists() and image_path.is_file():
                image_path.unlink()
        except OSError:
            pass

    def resolve_profile_picture(self, relative_path):
        return (self.get_app_base_dir() / relative_path).resolve()

    def _prepare_image(self, image, size):
        # Normalize every uploaded format into one square PNG for consistent display.
        converted = image.convert("RGBA")
        return ImageOps.fit(converted, size, method=Image.Resampling.LANCZOS)

    def _sanitize_filename_hint(self, filename_hint):
        cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", (filename_hint or "student").strip())
        return cleaned or "student"
