from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from trosmic_digest_agent.connectors.base import Connector
from trosmic_digest_agent.models import Article
from trosmic_digest_agent.source_policy import normalize_domain


class RSSConnector(Connector):
    def fetch(self) -> list[Article]:
        if not self.source.url:
            return []
        request = Request(self.source.url, headers={"User-Agent": "trosmic-digest-agent/0.1"})
        with urlopen(request, timeout=self.timeout) as response:
            payload = response.read()
        return parse_rss(
            payload,
            source_name=self.source.name,
            connector="rss",
            query_group=self.source.query_group,
            query_used=self.source.query_used,
        )


def parse_rss(
    payload: bytes | str,
    source_name: str,
    connector: str = "rss",
    query_group: str = "",
    query_used: str = "",
) -> list[Article]:
    root = ElementTree.fromstring(payload)
    articles: list[Article] = []

    for item in root.findall(".//item"):
        title = _text(item, "title") or "Untitled"
        url = _text(item, "link") or _text(item, "guid") or ""
        summary = _text(item, "description") or ""
        published = _parse_date(_text(item, "pubDate") or _text(item, "published"))
        source_element = item.find("source")
        item_source_name = _text(item, "source") or source_name
        source_url = source_element.attrib.get("url", "") if source_element is not None else ""
        if url:
            articles.append(
                Article(
                    title=title.strip(),
                    url=url.strip(),
                    source=item_source_name.strip(),
                    published_at=published,
                    summary=summary.strip(),
                    source_domain=normalize_domain(source_url or url),
                    connector=connector,
                    query_group=query_group,
                    query_used=query_used,
                )
            )

    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        title = _text(entry, "{http://www.w3.org/2005/Atom}title") or "Untitled"
        link = entry.find("{http://www.w3.org/2005/Atom}link")
        url = link.attrib.get("href", "") if link is not None else ""
        summary = (
            _text(entry, "{http://www.w3.org/2005/Atom}summary")
            or _text(entry, "{http://www.w3.org/2005/Atom}content")
            or ""
        )
        published = _parse_date(
            _text(entry, "{http://www.w3.org/2005/Atom}published")
            or _text(entry, "{http://www.w3.org/2005/Atom}updated")
        )
        if url:
            articles.append(
                Article(
                    title=title.strip(),
                    url=url.strip(),
                    source=source_name,
                    published_at=published,
                    summary=summary.strip(),
                    source_domain=normalize_domain(url),
                    connector=connector,
                    query_group=query_group,
                    query_used=query_used,
                )
            )

    return articles


def _text(element: ElementTree.Element, tag: str) -> str | None:
    child = element.find(tag)
    if child is None or child.text is None:
        return None
    return child.text


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        pass
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None
