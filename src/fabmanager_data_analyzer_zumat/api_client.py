"""
FabManager API Client

This module provides a client for interacting with the FabManager Open API.
"""

import logging
from typing import Dict, Generator, List, Optional, Union

import requests
from requests.structures import CaseInsensitiveDict

logger = logging.getLogger(__name__)


class FabManagerAPIClient:
    """Client for interacting with the FabManager Open API."""

    def __init__(self, base_url: str, api_token: str):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the API
            api_token: Your API authentication token
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update(
            {
                "Authorization": f"Token token={self.api_token}",
                "Accept": "application/json",
            }
        )

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the API connection and authentication.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Try to fetch first page of users with minimal data
            endpoint = f"{self.base_url}/open_api/v1/users"
            params = {"page": 1, "per_page": 1}

            logger.info("Testing API connection...")
            response = self.session.get(endpoint, params=params, timeout=10)

            if response.status_code == 200:
                return True, "Connection successful"
            elif response.status_code == 401:
                return False, "Authentication failed - Invalid API token"
            elif response.status_code == 403:
                return False, "Access forbidden - Check API permissions"
            elif response.status_code == 404:
                return False, "API endpoint not found - Check base URL"
            else:
                return False, f"Unexpected response: HTTP {response.status_code}"

        except requests.exceptions.ConnectionError:
            return False, "Connection error - Check base URL and internet connection"
        except requests.exceptions.Timeout:
            return False, "Connection timeout - Server not responding"
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def _get_endpoint_data(
        self, endpoint: str, data_key: str, page: int = 1, per_page: int = 100
    ) -> Dict:
        """
        Generic method to fetch data from any endpoint.

        Args:
            endpoint: API endpoint path (e.g., '/open_api/v1/users')
            data_key: Key in response containing the data array
            page: Page number to fetch
            per_page: Number of items per page

        Returns:
            Dictionary containing 'data' and 'pagination' information
        """
        full_endpoint = f"{self.base_url}{endpoint}"
        params = {"page": page, "per_page": per_page}

        try:
            logger.info(f"Fetching page {page} from {endpoint}")
            response = self.session.get(full_endpoint, params=params)
            response.raise_for_status()

            # Extract pagination metadata from headers
            pagination_info = self._extract_pagination_info(response.headers)

            # Parse response
            response_data = response.json()

            # Handle both direct array and wrapped response
            if isinstance(response_data, dict) and data_key in response_data:
                data = response_data[data_key]
            else:
                data = response_data

            return {"data": data, "pagination": pagination_info}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from {endpoint}: {e}")
            raise

    def _get_all_data(
        self,
        endpoint: str,
        data_key: str,
        per_page: int = 100,
        max_pages: Optional[int] = None,
        show_progress: bool = True,
    ) -> Generator[Dict, None, None]:
        """
        Generator that fetches all data across all pages.

        Args:
            endpoint: API endpoint path
            data_key: Key in response containing the data array
            per_page: Number of items per page
            max_pages: Maximum number of pages to fetch (optional)
            show_progress: Whether to show progress in console (default: True)

        Yields:
            Individual data records
        """
        page = 1
        total_items = 0

        while True:
            if max_pages and page > max_pages:
                logger.info(f"Reached max_pages limit ({max_pages})")
                if show_progress:
                    print(
                        f"\r✓ Fetched {total_items} items from {page-1} pages",
                        flush=True,
                    )
                break

            result = self._get_endpoint_data(endpoint, data_key, page, per_page)
            data = result["data"]
            pagination = result["pagination"]

            # Show progress
            if show_progress:
                total = pagination.get("total")
                if total:
                    percentage = min(100, (total_items / total) * 100)
                    print(
                        f"\rFetching... {total_items}/{total} items ({percentage:.1f}%) - Page {page}",
                        end="",
                        flush=True,
                    )
                else:
                    print(
                        f"\rFetching... Page {page} ({total_items} items so far)",
                        end="",
                        flush=True,
                    )

            # Yield each item
            if data:
                for item in data:
                    total_items += 1
                    yield item

            # Check if there are more pages
            if not pagination.get("has_next") or not data:
                logger.info(f"Fetched all pages (total: {page})")
                if show_progress:
                    print(
                        f"\r✓ Fetched {total_items} items from {page} pages" + " " * 20,
                        flush=True,
                    )
                break

            page += 1

    def fetch_all_as_list(
        self,
        endpoint: str,
        data_key: str,
        per_page: int = 100,
        max_pages: Optional[int] = None,
        show_progress: bool = True,
    ) -> List[Dict]:
        """
        Fetch all data and return as a list.

        Args:
            endpoint: API endpoint path
            data_key: Key in response containing the data array
            per_page: Number of items per page
            max_pages: Maximum number of pages to fetch (optional)
            show_progress: Whether to show progress in console (default: True)

        Returns:
            List of all data records
        """
        all_data = list(
            self._get_all_data(endpoint, data_key, per_page, max_pages, show_progress)
        )
        logger.info(f"Total items fetched: {len(all_data)}")
        return all_data

    def _extract_pagination_info(
        self, headers: Union[Dict, CaseInsensitiveDict[str]]
    ) -> Dict:
        """
        Extract pagination information from response headers.

        Args:
            headers: Response headers

        Returns:
            Dictionary with pagination metadata
        """
        pagination: Dict = {
            "total": None,
            "per_page": None,
            "has_next": False,
            "has_prev": False,
            "links": {},
        }

        # Extract Total
        if "Total" in headers:
            try:
                pagination["total"] = int(headers["Total"])
            except ValueError:
                pass

        # Extract Per-Page
        if "Per-Page" in headers:
            try:
                pagination["per_page"] = int(headers["Per-Page"])
            except ValueError:
                pass

        # Parse Link header (RFC-5988)
        if "Link" in headers:
            links = self._parse_link_header(headers["Link"])
            pagination["links"] = links
            pagination["has_next"] = "next" in links
            pagination["has_prev"] = "prev" in links

        return pagination

    def _parse_link_header(self, link_header: str) -> Dict[str, str]:
        """
        Parse RFC-5988 Link header.

        Args:
            link_header: Link header string

        Returns:
            Dictionary mapping rel types to URLs
        """
        links = {}

        for link in link_header.split(","):
            link = link.strip()
            if not link:
                continue

            # Extract URL and rel
            parts = link.split(";")
            if len(parts) >= 2:
                url = parts[0].strip().strip("<>")
                rel = None

                for part in parts[1:]:
                    if "rel=" in part:
                        rel = part.split("=")[1].strip().strip("\"'")
                        break

                if rel:
                    links[rel] = url

        return links
