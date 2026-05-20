import requests
from app.utils.logger import info, error, warning


SERPER_API_URL = "https://google.serper.dev/search"


class WebResearcher:
    """Performs web research using the Serper API for real search data."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }

    def _make_request(self, payload: dict) -> dict:
        """Make a request to the Serper API."""
        try:
            response = requests.post(
                SERPER_API_URL,
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            error(f"Serper API request failed: {e}")
            return {}

    def search_keywords(self, keywords_list: list) -> list:
        """Search each keyword and collect results."""
        info(f"Searching {len(keywords_list)} keywords...")
        all_results = []

        for keyword in keywords_list:
            payload = {"q": keyword, "num": 5}
            data = self._make_request(payload)

            organic = data.get("organic", [])
            for item in organic:
                all_results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source_type": "web",
                    "query": keyword,
                })

        info(f"Collected {len(all_results)} results from keyword search")
        return all_results

    def get_people_also_ask(self, query: str) -> list:
        """Get People Also Ask data for a query."""
        info(f"Getting PAA for: {query}")
        payload = {"q": query, "num": 10}
        data = self._make_request(payload)

        paa = data.get("peopleAlsoAsk", [])
        results = []
        for item in paa:
            results.append({
                "title": item.get("question", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source_type": "people_also_ask",
                "query": query,
            })

        return results

    def search_news(self, query: str) -> list:
        """Search news articles for a query."""
        info(f"Searching news for: {query}")
        payload = {"q": query, "type": "news", "num": 10}
        data = self._make_request(payload)

        news = data.get("news", [])
        results = []
        for item in news:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source_type": "news",
                "query": query,
            })

        return results

    def search_social(self, query: str) -> list:
        """Search social media mentions for a query."""
        info(f"Searching social for: {query}")
        social_query = f"{query} site:reddit.com OR site:twitter.com OR site:linkedin.com"
        payload = {"q": social_query, "num": 10}
        data = self._make_request(payload)

        organic = data.get("organic", [])
        results = []
        for item in organic:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source_type": "social_media",
                "query": query,
            })

        return results
