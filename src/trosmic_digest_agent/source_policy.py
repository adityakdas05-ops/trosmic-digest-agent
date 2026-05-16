from __future__ import annotations

from urllib.parse import urlparse

from trosmic_digest_agent.models import Article, SourceConfig

GENERIC_AI_VENDOR_DOMAINS = (
    "openai.com",
    "platform.openai.com",
    "developers.openai.com",
    "docs.openai.com",
    "anthropic.com",
    "mistral.ai",
    "cohere.com",
    "perplexity.ai",
)

GENERIC_AI_VENDOR_TERMS = (
    "openai",
    "chatgpt",
    "codex",
    "anthropic",
    "claude",
    "mistral",
    "cohere",
    "perplexity",
    "databricks",
    "nvidia ai",
    "enterprise ai",
    "foundation model",
    "large language model",
    "llm",
)

EXPLICIT_SPORTS_BUSINESS_TERMS = (
    "sport",
    "sports",
    "league",
    "team",
    "club",
    "athlete",
    "media rights",
    "broadcast rights",
    "streaming rights",
    "ott",
    "broadcast",
    "venue",
    "stadium",
    "arena",
    "fan data",
    "fan engagement",
    "sponsorship",
    "sponsor",
    "naming rights",
    "franchise",
    "valuation",
    "ipl",
    "wpl",
    "bcci",
    "kabaddi",
    "pro kabaddi",
    "ufc",
    "tko",
    "wwe",
    "formula 1",
    "nba",
    "nfl",
    "fifa",
    "ioc",
    "saudi",
    "uae",
    "qatar",
    "dubai",
)


def normalize_domain(url_or_domain: str | None) -> str:
    if not url_or_domain:
        return ""
    value = url_or_domain.strip()
    parsed = urlparse(value if "://" in value else f"https://{value}")
    domain = (parsed.netloc or parsed.path).lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.split("/")[0]


def article_source_domain(article: Article) -> str:
    return article.source_domain or normalize_domain(article.url)


def is_generic_ai_vendor_domain(domain_or_url: str | None) -> bool:
    domain = normalize_domain(domain_or_url)
    if not domain:
        return False
    return any(
        domain == blocked or domain.endswith(f".{blocked}")
        for blocked in GENERIC_AI_VENDOR_DOMAINS
    )


def is_generic_ai_vendor_article(article: Article) -> bool:
    domain = article_source_domain(article)
    if is_generic_ai_vendor_domain(domain):
        return True
    text = _article_text(article)
    return any(term in text for term in GENERIC_AI_VENDOR_TERMS)


def is_hard_blocked_generic_ai_source(article: Article) -> bool:
    if not is_generic_ai_vendor_domain(article_source_domain(article)):
        return False
    return not story_has_explicit_sports_business_relevance(article)


def story_has_explicit_sports_business_relevance(article: Article) -> bool:
    text = _article_text(article)
    return any(term in text for term in EXPLICIT_SPORTS_BUSINESS_TERMS)


def is_generic_ai_source_config(source: SourceConfig) -> bool:
    urls = [source.url or "", *source.urls]
    return any(is_generic_ai_vendor_domain(url) for url in urls)


def _article_text(article: Article) -> str:
    return f"{article.title} {article.summary} {article.content}".lower()
