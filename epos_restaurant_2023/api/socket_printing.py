import contextlib
import fcntl
import logging
import os
import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path

import frappe
from escpos.exceptions import DeviceNotFoundError

from html2image import Html2Image
from PIL import Image, ImageChops


PRINTER_IP = "192.168.10.240"
PRINTER_PORT = 9100
RENDER_WIDTH_PX = 576
RENDER_HEIGHT_PX = 2600
FRAGMENT_HEIGHT = 4096
HTML_FILE = "receipt.hml"
LOCK_TIMEOUT = 120
RETRIES = 3
RETRY_DELAY = 0.5
AFTER_PRINT_DELAY = 0.1
CUT_PAPER = True
PULSE_CASH_DRAWER = False
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "log.txt"
CACHED_IMAGE_FILE = BASE_DIR / "receipt_escpos.png"


@frappe.whitelist()
def print_me():
    setup_logging()
    job_started_at = time.monotonic()
    job_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

    logging.info(
        "PRINT_START job_id=%s ip=%s port=%s file=%s width=%s height=%s",
        job_id,
        PRINTER_IP,
        PRINTER_PORT,
        HTML_FILE,
        RENDER_WIDTH_PX,
        RENDER_HEIGHT_PX,
    )

    try:
        image_path = get_print_image()
        print_image(
            image_path=image_path,
            printer_ip=PRINTER_IP,
            port=PRINTER_PORT,
            fragment_height=FRAGMENT_HEIGHT,
            lock_timeout=LOCK_TIMEOUT,
            retries=RETRIES,
            retry_delay=RETRY_DELAY,
            after_print_delay=AFTER_PRINT_DELAY,
            cut=CUT_PAPER,
            pulse=PULSE_CASH_DRAWER,
        )
        duration = time.monotonic() - job_started_at
        logging.info("PRINT_SUCCESS job_id=%s duration=%.2fs", job_id, duration)
        flush_logs()
        return {
            "ok": True,
            "job_id": job_id,
            "duration": duration,
            "printer_ip": PRINTER_IP,
            "printer_port": PRINTER_PORT,
            "html_file": str(BASE_DIR / HTML_FILE),
            "image_file": str(image_path),
        }
    except Exception as error:
        logging.exception(
            "PRINT_FAIL job_id=%s duration=%.2fs error=%r",
            job_id,
            time.monotonic() - job_started_at,
            error,
        )
        flush_logs()
        frappe.throw(f"Print failed: {error}")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")],
        force=True,
    )


def flush_logs() -> None:
    for handler in logging.getLogger().handlers:
        handler.flush()


def read_html() -> str:
    html_path = BASE_DIR / HTML_FILE
    if not html_path.exists():
        frappe.throw(f"Receipt template not found: {html_path}")
    return html_path.read_text(encoding="utf-8")


@contextlib.contextmanager
def file_lock(lock_name: str, timeout: int):
    lock_file_path = BASE_DIR / lock_name
    lock_file_path.touch(exist_ok=True)

    with lock_file_path.open("r+b") as lock_file:
        deadline = time.monotonic() + timeout

        while True:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out waiting for {lock_name}.")
                time.sleep(0.1)

        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def trim_white_bottom(image_path: Path) -> None:
    image = Image.open(image_path).convert("RGB")
    background = Image.new(image.mode, image.size, "white")
    diff = ImageChops.difference(image, background)
    bbox = diff.getbbox()

    if bbox:
        cropped = image.crop((0, 0, image.width, bbox[3] + 10))
        cropped.save(image_path)


def optimize_for_escpos(image_path: Path) -> Path:
    optimized_path = image_path.with_name("receipt_escpos.png")
    image = Image.open(image_path).convert("L")
    image = image.point(lambda pixel: 0 if pixel < 200 else 255, mode="1")
    image.save(optimized_path)
    return optimized_path


def html_to_png(html: str, output_dir: Path, width: int, height: int) -> Path:
    image_name = "receipt.png"
    html_temp_dir = output_dir / "html2image"
    chrome_user_dir = output_dir / "chrome-user-data"
    chrome_cache_dir = output_dir / "chrome-cache"
    html_temp_dir.mkdir()
    chrome_user_dir.mkdir()
    chrome_cache_dir.mkdir()

    renderer = Html2Image(
        output_path=str(output_dir),
        temp_path=str(html_temp_dir),
        custom_flags=[
            f"--user-data-dir={chrome_user_dir}",
            f"--disk-cache-dir={chrome_cache_dir}",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--hide-scrollbars",
        ],
    )
    renderer.screenshot(
        html_str=html,
        save_as=image_name,
        size=(width, height),
    )

    image_path = output_dir / image_name
    trim_white_bottom(image_path)
    return optimize_for_escpos(image_path)


def cache_is_current() -> bool:
    html_path = BASE_DIR / HTML_FILE
    return (
        html_path.exists()
        and CACHED_IMAGE_FILE.exists()
        and CACHED_IMAGE_FILE.stat().st_mtime >= html_path.stat().st_mtime
    )


def get_print_image() -> Path:
    if cache_is_current():
        logging.info("RENDER_CACHE_HIT image=%s", CACHED_IMAGE_FILE)
        return CACHED_IMAGE_FILE

    with file_lock(".render-cache.lock", LOCK_TIMEOUT):
        if cache_is_current():
            logging.info("RENDER_CACHE_HIT image=%s", CACHED_IMAGE_FILE)
            return CACHED_IMAGE_FILE

        logging.info("RENDER_CACHE_MISS file=%s", HTML_FILE)
        html = read_html()

        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = html_to_png(
                html=html,
                output_dir=Path(temp_dir),
                width=RENDER_WIDTH_PX,
                height=RENDER_HEIGHT_PX,
            )
            temp_cache_path = CACHED_IMAGE_FILE.with_suffix(".tmp.png")
            shutil.copyfile(image_path, temp_cache_path)
            os.replace(temp_cache_path, CACHED_IMAGE_FILE)

        return CACHED_IMAGE_FILE


@contextlib.contextmanager
def printer_lock(printer_ip: str, timeout: int):
    lock_name = f".printer-{printer_ip.replace('.', '-')}.lock"
    with file_lock(lock_name, timeout):
        yield


def print_image(
    image_path: Path,
    printer_ip: str,
    port: int,
    fragment_height: int,
    lock_timeout: int,
    retries: int,
    retry_delay: float,
    after_print_delay: float,
    cut: bool,
    pulse: bool,
) -> None:
    pass

def main() -> None:
    print_me()


if __name__ == "__main__":
    main()
