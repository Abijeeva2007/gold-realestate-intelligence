"""
Base Collector Module.
Provides robust HTTP requests with retries, exponential backoff, rate limiting,
and automatic raw data persistence with provenance metadata.
"""

import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import requests

from src.config import RAW_DATA_DIR, setup_logging

logger = setup_logging()

class BaseCollector:
    """Base class for all data collectors."""

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"gold_pipeline.collector.{name}")
        self.raw_dir = Path(RAW_DATA_DIR)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def fetch_url(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        retries: int = 3,
        backoff_factor: float = 2.0,
        timeout: int = 25,
        verify_ssl: bool = True
    ) -> Optional[requests.Response]:
        """
        Executes an HTTP GET request with retries and exponential backoff.
        
        Args:
            url: Target URL
            headers: Optional HTTP headers
            retries: Max retry attempts
            backoff_factor: Multiplier for retry sleep delay
            timeout: Timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        req_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        
        for attempt in range(1, retries + 1):
            try:
                self.logger.info(f"[{self.name}] Fetching {url} (Attempt {attempt}/{retries})...")
                response = requests.get(
                    url,
                    headers=req_headers,
                    timeout=timeout,
                    verify=verify_ssl
                )
                if response.status_code == 200:
                    self.logger.info(f"[{self.name}] Successfully fetched {len(response.content):,} bytes from {url}")
                    return response
                elif response.status_code in (403, 401):
                    self.logger.warning(f"[{self.name}] Access restricted (HTTP {response.status_code}) for {url}")
                    return response
                else:
                    self.logger.warning(f"[{self.name}] HTTP {response.status_code} received from {url}")
            except (requests.RequestException, Exception) as exc:
                self.logger.warning(f"[{self.name}] Attempt {attempt} failed for {url}: {exc}")
            
            if attempt < retries:
                sleep_time = backoff_factor ** attempt
                self.logger.info(f"[{self.name}] Sleeping {sleep_time:.1f}s before next retry...")
                time.sleep(sleep_time)
                
        self.logger.error(f"[{self.name}] All {retries} fetch attempts failed for {url}")
        return None

    def save_raw_file(
        self,
        filename: str,
        content: bytes | str,
        source_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Saves raw downloaded bytes or string to the raw data directory,
        accompanied by an immutable JSON metadata file with timestamps and origin.
        """
        file_path = self.raw_dir / filename
        meta_path = self.raw_dir / f"{filename}.meta.json"

        # Write data file
        if isinstance(content, str):
            file_path.write_text(content, encoding="utf-8")
        else:
            file_path.write_bytes(content)

        # Write provenance metadata
        provenance = {
            "source_name": source_name,
            "filename": filename,
            "collected_at_utc": datetime.now(timezone.utc).isoformat(),
            "file_size_bytes": file_path.stat().st_size,
            "metadata": metadata or {}
        }
        meta_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
        self.logger.info(f"[{self.name}] Saved raw file: {file_path} ({provenance['file_size_bytes']:,} bytes)")
        return file_path
