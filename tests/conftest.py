from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT_DIR / "examples"


def _wait_for_app(
    base_url: str, process: subprocess.Popen[str], timeout: float = 30.0
) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(
                f"Streamlit app exited while starting {base_url}.\n{output}"
            )

        try:
            with urllib.request.urlopen(base_url) as response:
                if response.status < 500:
                    return
        except (OSError, urllib.error.URLError) as error:
            last_error = error
            time.sleep(0.5)

    output = process.stdout.read() if process.stdout else ""
    raise RuntimeError(f"Timed out waiting for {base_url}.\n{output}") from last_error


@pytest.fixture(scope="session")
def streamlit_app_factory() -> Iterator[Callable[[str, int], str]]:
    processes: list[subprocess.Popen[str]] = []

    def _launch(example_name: str, port: int) -> str:
        script_path = EXAMPLES_DIR / example_name
        base_url = f"http://127.0.0.1:{port}"
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(script_path),
                "--server.headless=true",
                "--browser.gatherUsageStats=false",
                "--server.port",
                str(port),
            ],
            cwd=ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        _wait_for_app(base_url, process)
        processes.append(process)
        return base_url

    yield _launch

    for process in processes:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page_with_errors(browser: Browser) -> Iterator[tuple[Page, list[str]]]:
    console_errors: list[str] = []
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.on(
        "console",
        lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
    )

    yield page, console_errors

    page.close()
