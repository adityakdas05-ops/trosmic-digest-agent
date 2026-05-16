from __future__ import annotations

import re
from dataclasses import dataclass

from trosmic_digest_agent.models import Article

PIPELINE_VERSION = "SPORTS_BUSINESS_FIRST_V3"

generic_ai_terms = [
    "AI model",
    "large language model",
    "LLM",
    "enterprise AI",
    "AI agent",
    "AI startup",
    "AI chip",
    "AI infrastructure",
    "cloud AI",
    "AI coding",
    "AI assistant",
    "foundation model",
    "AI partnership",
    "AI funding",
    "AI app",
]

sports_adjacency_terms = [
    "sports",
    "league",
    "team",
    "fan",
    "broadcast",
    "media rights",
    "OTT",
    "streaming rights",
    "stadium",
    "arena",
    "venue",
    "sponsorship",
    "athlete",
    "ticketing",
    "fantasy",
    "gaming",
    "viewership",
    "rights deal",
    "franchise",
    "club",
    "kabaddi",
    "IPL",
    "WPL",
    "PKL",
    "UFC",
    "WWE",
    "NBA",
    "NFL",
    "Formula 1",
]

PRIMARY_TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "sports": ("sports", "sport", "athlete", "team", "club"),
    "league": ("league", "competition", "tournament"),
    "media rights": ("media rights", "broadcast rights", "rights deal"),
    "OTT / streaming sports": ("ott", "streaming rights", "sports streaming", "streaming"),
    "broadcast": ("broadcast", "broadcaster", "broadcast production"),
    "sponsorship": ("sponsorship", "sponsor", "brand partnership", "activation"),
    "naming rights": ("naming rights",),
    "stadium": ("stadium",),
    "arena": ("arena",),
    "venue": ("venue", "facility", "mixed-use district"),
    "live entertainment": ("live entertainment", "live event", "concert venue"),
    "franchise sale": ("franchise sale", "team sale", "club sale"),
    "team valuation": ("team valuation", "franchise valuation", "valuation"),
    "sports private equity": ("sports private equity", "private equity"),
    "sports M&A": ("sports m&a", "sports merger", "sports acquisition"),
    "sovereign sports investment": ("sovereign sports investment", "pif", "qia", "mubadala"),
    "family office sports investment": ("family office",),
    "kabaddi": ("kabaddi",),
    "PKL": ("pkl", "pro kabaddi"),
    "IPL": ("ipl",),
    "WPL": ("wpl",),
    "BCCI": ("bcci",),
    "UFC": ("ufc",),
    "TKO": ("tko",),
    "WWE": ("wwe",),
    "Formula 1": ("formula 1", "f1", "liberty media"),
    "NBA": ("nba",),
    "NFL": ("nfl",),
    "FIFA": ("fifa",),
    "IOC": ("ioc", "olympic"),
    "EPL": ("epl", "premier league"),
    "MLS": ("mls",),
    "combat sports": ("combat sports", "boxing", "mma", "wrestling"),
    "fan engagement": ("fan engagement", "fan platform", "fan experience"),
    "fantasy sports": ("fantasy sports", "fantasy gaming"),
    "sports gaming": ("sports gaming", "gaming"),
    "athlete storytelling": ("athlete storytelling", "athlete creator"),
    "sports documentary": ("sports documentary", "documentary"),
    "GCC sports": ("gcc sports", "gcc"),
    "UAE sports": ("uae sports", "uae", "dubai", "abu dhabi"),
    "Saudi sports": ("saudi sports", "saudi", "qiddiya"),
    "Qatar sports": ("qatar sports", "qatar"),
    "India sports regulation": ("india sports regulation", "sports regulation india"),
    "betting/fantasy regulation": ("betting regulation", "fantasy regulation"),
    "sports data": ("sports data", "fan data", "athlete data"),
    "sports analytics": ("sports analytics", "fan analytics", "sponsorship analytics"),
}

TROSMIC_PILLAR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "WKCL": ("wkcl", "kabaddi", "pkl", "pro kabaddi", "global kabaddi"),
    "Flux Halo": ("flux halo", "stadium", "arena", "venue", "live entertainment"),
    "media rights / OTT": ("media rights", "broadcast rights", "streaming rights", "ott"),
    "sponsorship": ("sponsorship", "sponsor", "brand partnership", "naming rights"),
    "franchise economics": ("franchise", "valuation", "team sale", "league economics"),
    "D2F / fan data": ("d2f", "direct-to-fan", "fan data", "fan engagement", "fantasy"),
    "content / athlete storytelling": ("content", "documentary", "athlete storytelling"),
    "Rumil / sports intelligence": (
        "sports ai",
        "sports analytics",
        "fan analytics",
        "sponsorship analytics",
        "broadcast production",
        "athlete data",
        "venue operations",
    ),
    "combat sports": ("ufc", "tko", "wwe", "pfl", "one championship", "boxing", "mma"),
    "investor relations / capital strategy": (
        "private equity",
        "sovereign",
        "family office",
        "m&a",
        "investment",
        "financing",
    ),
    "GCC positioning": ("gcc", "uae", "saudi", "qatar", "dubai", "abu dhabi", "qiddiya"),
    "India sports strategy": ("india", "bcci", "ipl", "wpl", "pkl", "kabaddi"),
}

GENERIC_TECH_TERMS = (
    "saas",
    "cloud",
    "cybersecurity",
    "chip",
    "semiconductor",
    "model launch",
    "developer tool",
    "coding tool",
    "workflow",
    "startup funding",
)

GENERIC_CRYPTO_TERMS = ("crypto", "web3", "blockchain", "token", "nft", "stablecoin")

AI_IN_SPORTS_TERMS = (
    "sports ai",
    "broadcast production",
    "fan analytics",
    "fan data",
    "sponsorship analytics",
    "athlete performance",
    "athlete data",
    "venue operations",
    "league operations",
    "media rights",
)


@dataclass(slots=True)
class EligibilityResult:
    eligible: bool
    reason: str = ""
    primary_topics: list[str] | None = None
    pillars: list[str] | None = None
    is_ai_led: bool = False


def is_eligible_for_trosmic_digest(story: Article) -> bool:
    return evaluate_eligibility(story).eligible


def evaluate_eligibility(story: Article) -> EligibilityResult:
    text = _story_text(story)
    primary_topics = detect_primary_topics(story)
    pillars = detect_trosmic_pillars(story)
    ai_led = is_ai_led_story(story)
    has_adjacency = has_sports_adjacency(story)

    if _has_any(text, generic_ai_terms) and not has_adjacency:
        return EligibilityResult(False, "generic_ai", primary_topics, pillars, ai_led)
    if ai_led and not has_direct_ai_sports_relevance(story):
        return EligibilityResult(False, "generic_ai", primary_topics, pillars, ai_led)
    if _has_any(text, GENERIC_TECH_TERMS) and not has_adjacency:
        return EligibilityResult(False, "generic_tech", primary_topics, pillars, ai_led)
    if _has_any(text, GENERIC_CRYPTO_TERMS) and not _has_any(
        text,
        ("sports", "ticketing", "fan engagement", "sports collectibles", "venue payments"),
    ):
        return EligibilityResult(False, "generic_tech", primary_topics, pillars, ai_led)
    if not primary_topics:
        return EligibilityResult(False, "no_primary_topic", primary_topics, pillars, ai_led)
    if not pillars:
        return EligibilityResult(False, "no_trosmic_pillar", primary_topics, pillars, ai_led)
    return EligibilityResult(True, "", primary_topics, pillars, ai_led)


def detect_primary_topics(story: Article) -> list[str]:
    text = _story_text(story)
    return [topic for topic, keywords in PRIMARY_TOPIC_KEYWORDS.items() if _has_any(text, keywords)]


def detect_trosmic_pillars(story: Article) -> list[str]:
    text = _story_text(story)
    return [
        pillar
        for pillar, keywords in TROSMIC_PILLAR_KEYWORDS.items()
        if _has_any(text, keywords)
    ]


def has_sports_adjacency(story: Article) -> bool:
    return _has_any(_story_text(story), sports_adjacency_terms)


def has_direct_ai_sports_relevance(story: Article) -> bool:
    if not is_ai_led_story(story):
        return True
    text = _story_text(story)
    return _has_any(text, AI_IN_SPORTS_TERMS) and has_sports_adjacency(story)


def is_ai_led_story(story: Article) -> bool:
    text = _story_text(story)
    title = story.title.lower()
    return _has_any(title, generic_ai_terms + ["ai"]) or (
        _has_any(text, generic_ai_terms)
        or ("artificial intelligence" in text)
        or ("generative ai" in text)
    )


def _story_text(story: Article) -> str:
    return f"{story.title} {story.summary} {story.content}".lower()


def _has_any(text: str, keywords: tuple[str, ...] | list[str]) -> bool:
    return any(_keyword_in_text(text, keyword.lower()) for keyword in keywords)


def _keyword_in_text(text: str, keyword: str) -> bool:
    if keyword.isalpha() and len(keyword) <= 3:
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
    return keyword in text
