from __future__ import annotations

import re
from urllib.parse import urlparse

from trosmic_digest_agent.models import Article

TROSMIC_CONTEXT = (
    "Trosmic is building an integrated sports operating company across WKCL and "
    "global kabaddi, Flux Halo venue infrastructure, media rights and OTT distribution, "
    "sponsorship, franchise economics, league governance, D2F fan data, sports content, "
    "combat sports, Rumil intelligence, investor relations, and the India/GCC/global "
    "sports platform opportunity."
)

DIGEST_MISSION_PROMPT = (
    "Build a sports-business-first intelligence digest for Trosmic. Include AI only when "
    "it directly connects to sports, media rights, OTT, fan engagement, content production, "
    "venue operations, sponsorship analytics, league operations, athlete data, or Rumil/D2F."
)

TROSMIC_RELEVANCE_THRESHOLD = 14

SPORTS_FIRST_QUERY_GROUPS = {
    "media_rights": [
        "latest sports media rights deal",
        "latest OTT sports streaming rights",
        "latest broadcast rights sports league deal",
        "latest Netflix Amazon YouTube sports rights",
    ],
    "sponsorship": [
        "latest sports sponsorship deal",
        "latest stadium naming rights deal",
        "latest jersey sponsorship sports deal",
        "latest sports brand partnership activation",
    ],
    "venues": [
        "latest stadium arena project financing",
        "latest sports venue investment",
        "latest live entertainment venue project",
        "latest arena naming rights deal",
    ],
    "capital": [
        "latest sports franchise sale valuation",
        "latest sports private equity investment",
        "latest sovereign wealth sports investment",
        "latest sports M&A deal",
    ],
    "india_sports": [
        "latest IPL BCCI sponsorship media rights",
        "latest WPL viewership sponsorship rights",
        "latest Pro Kabaddi League media rights sponsorship",
        "latest kabaddi international federation news",
    ],
    "global_leagues": [
        "latest UFC TKO media rights sponsorship",
        "latest WWE Netflix sports entertainment",
        "latest Formula 1 sponsorship media rights",
        "latest NBA media rights franchise valuation",
        "latest NFL media rights franchise valuation",
    ],
    "gcc": [
        "latest Saudi sports investment",
        "latest UAE sports investment",
        "latest Dubai sports entertainment venue",
        "latest Qatar sports investment",
    ],
    "fan_data": [
        "latest sports fan engagement platform",
        "latest fantasy sports regulation",
        "latest sports data analytics sponsorship",
        "latest AI sports broadcast production fan analytics",
    ],
}

SPORTS_FIRST_QUERIES = [
    query
    for queries in SPORTS_FIRST_QUERY_GROUPS.values()
    for query in queries
]

DEFAULT_TROSMIC_INTERESTS = [
    "sports media rights",
    "OTT sports streaming",
    "league expansion",
    "franchise valuation",
    "sports sponsorship",
    "naming rights",
    "stadium financing",
    "arena development",
    "sports private equity",
    "sovereign wealth sports investment",
    "kabaddi",
    "Pro Kabaddi League",
    "IPL",
    "WPL",
    "BCCI",
    "UFC",
    "TKO",
    "WWE",
    "Formula 1",
    "NBA",
    "NFL",
    "FIFA",
    "IOC",
    "EPL",
    "MLS",
    "Saudi sports investment",
    "UAE sports investment",
    "Qatar sports investment",
    "fan engagement",
    "fantasy sports",
    "sports gaming",
    "sports data",
    "direct-to-fan",
    "sports AI",
    "broadcast production",
    "athlete data",
]

PILLAR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "WKCL / global kabaddi": (
        "kabaddi",
        "pro kabaddi",
        "pkl",
        "ikf",
        "world kabaddi",
        "global kabaddi",
        "indian sport",
    ),
    "Flux Halo / venue infrastructure": (
        "stadium",
        "arena",
        "venue",
        "naming rights",
        "ticketing",
        "live events",
        "facility",
        "mixed-use",
        "district",
        "concessions",
        "hospitality",
        "venue financing",
    ),
    "Media rights and OTT distribution": (
        "media rights",
        "broadcast rights",
        "streaming rights",
        "ott",
        "streaming",
        "netflix",
        "amazon",
        "disney",
        "espn",
        "dazn",
        "jiostar",
        "jiohotstar",
        "star sports",
        "sports broadcast",
    ),
    "Sponsorship and commercial partnerships": (
        "sponsor",
        "sponsorship",
        "commercial partnership",
        "brand partnership",
        "naming rights",
        "advertising",
        "ad sales",
    ),
    "Franchise economics and league governance": (
        "franchise",
        "valuation",
        "team sale",
        "expansion",
        "league launch",
        "restructure",
        "governance",
        "salary cap",
        "revenue share",
        "club sale",
    ),
    "D2F fan ecosystem and fan data": (
        "fan engagement",
        "direct-to-fan",
        "d2f",
        "fantasy",
        "gaming",
        "loyalty",
        "fan data",
        "crm",
        "ticketing data",
        "sports betting",
    ),
    "Sports content and athlete storytelling": (
        "content production",
        "documentary",
        "creator",
        "athlete storytelling",
        "shoulder programming",
        "sports content",
        "broadcast production",
    ),
    "Combat sports": (
        "ufc",
        "tko",
        "wwe",
        "boxing",
        "wrestling",
        "mma",
        "combat sports",
    ),
    "Rumil intelligence layer": (
        "sports ai",
        "athlete data",
        "performance analytics",
        "sponsorship analytics",
        "broadcast automation",
        "venue operations",
        "fan intelligence",
    ),
    "Investor relations and capital strategy": (
        "private equity",
        "venture capital",
        "sovereign wealth",
        "pif",
        "mubadala",
        "adq",
        "qia",
        "family office",
        "sports m&a",
        "investment",
        "financing",
        "capital raise",
    ),
    "GCC / India / global platform opportunity": (
        "gcc",
        "saudi",
        "uae",
        "qatar",
        "dubai",
        "abu dhabi",
        "india",
        "bcci",
        "ipl",
        "wpl",
        "global sports",
    ),
}

COMMERCIAL_KEYWORDS = (
    "rights",
    "deal",
    "sponsor",
    "sponsorship",
    "valuation",
    "sale",
    "investment",
    "funding",
    "financing",
    "revenue",
    "ebitda",
    "merger",
    "acquisition",
    "m&a",
    "private equity",
    "sovereign wealth",
    "naming rights",
    "bid",
    "tender",
)

STRATEGIC_KEYWORDS = (
    "media rights",
    "ott",
    "streaming",
    "league",
    "expansion",
    "franchise",
    "venue",
    "arena",
    "stadium",
    "fan data",
    "direct-to-fan",
    "regulation",
    "governance",
    "sovereign",
    "gcc",
    "india",
    "kabaddi",
    "broadcast",
    "content",
    "ai",
    "analytics",
)

AI_TERMS = (
    "ai",
    "artificial intelligence",
    "openai",
    "anthropic",
    "llm",
    "generative ai",
    "model launch",
    "foundation model",
)
TECH_PRODUCT_TERMS = (
    "product launch",
    "developer tool",
    "coding tool",
    "app launch",
    "saas",
    "cloud",
    "chip",
    "semiconductor",
    "workflow",
    "enterprise ai",
)
STARTUP_FUNDING_TERMS = ("startup", "seed round", "series a", "series b", "raises", "funding")
CRYPTO_TERMS = ("crypto", "web3", "blockchain", "token", "nft", "stablecoin")
POLITICS_TERMS = ("election", "minister", "parliament", "senate", "government")

GENERIC_AI_PENALTY = 8
GENERIC_TECH_PENALTY = 6
AI_TOP_10_CAP = 1

NON_AI_TROSMIC_PILLARS = {
    pillar for pillar in PILLAR_KEYWORDS if pillar != "Rumil intelligence layer"
}

GENERIC_AI_OR_TECH_REJECTION_REASONS = {
    "generic AI story",
    "generic tech/startup story",
    "generic crypto/Web3 story",
}

SPORTS_MEDIA_CONTEXT_TERMS = tuple(
    sorted({keyword for values in PILLAR_KEYWORDS.values() for keyword in values})
)

TIER_1_TERMS = (
    "official",
    "league",
    "bcci",
    "nba",
    "nfl",
    "ufc",
    "tko",
    "wwe",
    "fifa",
    "ioc",
    "formula 1",
    "sec",
    "government",
    ".gov",
)
TIER_2_TERMS = (
    "reuters",
    "bloomberg",
    "financial times",
    "ft",
    "cnbc",
    "sbj",
    "sportbusiness",
    "sportsbusiness",
    "sports business journal",
    "sportspro",
    "espn",
    "variety",
    "deadline",
    "economic times",
    "mint",
    "business standard",
    "sportstar",
)
TIER_3_TERMS = (
    "kpmg",
    "deloitte",
    "pwc",
    "ey",
    "ficci",
    "groupm",
    "wpp",
    "nielsen",
    "barc",
    "kearney",
    "houlihan lokey",
)
TIER_4_TERMS = ("linkedin", "x.com", "twitter", "instagram", "facebook", "substack")


def score_trosmic_relevance(article: Article, configured_interests: list[str]) -> tuple[int, dict[str, int]]:
    text = _article_text(article)
    pillar_matches = _matched_pillars(text)
    pillar_score = _pillar_score(pillar_matches)
    commercial_score = _keyword_score(text, COMMERCIAL_KEYWORDS, cap=5)
    strategic_score = _strategic_score(text, pillar_matches, configured_interests)
    actionability_score = _actionability_score(text, pillar_score, commercial_score, strategic_score)
    source_credibility = source_credibility_score(article)
    total = pillar_score + commercial_score + strategic_score + actionability_score + source_credibility
    if is_generic_ai_story(article):
        total -= GENERIC_AI_PENALTY
    if is_generic_tech_startup_story(article):
        total -= GENERIC_TECH_PENALTY
    return total, {
        "direct_relevance_to_trosmic_pillar": pillar_score,
        "commercial_materiality": commercial_score,
        "strategic_insight_value": strategic_score,
        "actionability_for_trosmic": actionability_score,
        "source_credibility": source_credibility,
        "generic_ai_penalty": -GENERIC_AI_PENALTY if is_generic_ai_story(article) else 0,
        "generic_tech_penalty": -GENERIC_TECH_PENALTY if is_generic_tech_startup_story(article) else 0,
    }


def passes_hard_exclusion(article: Article) -> bool:
    return rejection_reason(article) == ""


def rejection_reason(article: Article) -> str:
    text = f" {_article_text(article)} "
    has_trosmic_context = has_sports_business_link(article)
    if is_generic_ai_story(article):
        return "generic AI story"
    if is_generic_tech_startup_story(article):
        return "generic tech/startup story"
    if _has_any(text, STARTUP_FUNDING_TERMS) and not has_trosmic_context:
        return "generic tech/startup story"
    if _has_any(text, CRYPTO_TERMS) and not _has_any(
        text,
        ("ticketing", "fan engagement", "sports collectibles", "venue payments", "stadium"),
    ):
        return "generic crypto/Web3 story"
    if _has_any(text, POLITICS_TERMS) and not _has_any(
        text,
        (
            "sports",
            "media regulation",
            "foreign investment",
            "data privacy",
            "betting",
            "fantasy",
            "tourism",
            "visa",
            "venue",
            "infrastructure",
            "india",
            "gcc",
            "saudi",
            "uae",
            "qatar",
        ),
    ):
        return "general politics without Trosmic sports-business impact"
    if not has_trosmic_context:
        return "no sports/media/entertainment/venue/capital link"
    if not has_clear_trosmic_implication(article):
        return "no clear Trosmic implication"
    return ""


def is_ai_led(article: Article) -> bool:
    title = article.title.lower()
    text = _article_text(article)
    return _has_any(title, AI_TERMS) or (
        _has_any(text, AI_TERMS)
        and _keyword_score(text, AI_TERMS, cap=5) >= 2
    )


def is_generic_ai_story(article: Article) -> bool:
    return is_ai_led(article) and not has_sports_business_link(article)


def is_generic_tech_startup_story(article: Article) -> bool:
    text = _article_text(article)
    return _has_any(text, TECH_PRODUCT_TERMS + STARTUP_FUNDING_TERMS) and not has_sports_business_link(article)


def has_sports_business_link(article: Article) -> bool:
    text = _article_text(article)
    pillars = _matched_pillars(text)
    if any(pillar in NON_AI_TROSMIC_PILLARS for pillar in pillars):
        return True
    return _has_any(
        text,
        (
            "sports",
            "league",
            "team",
            "athlete",
            "media rights",
            "broadcast",
            "streaming",
            "ott",
            "venue",
            "stadium",
            "arena",
            "fan data",
            "fan engagement",
            "sponsorship",
            "franchise",
            "entertainment",
            "live event",
            "kabaddi",
            "ipl",
            "wpl",
            "bcci",
            "ufc",
            "wwe",
            "tko",
            "boxing",
            "mma",
            "formula 1",
            "nba",
            "nfl",
            "saudi",
            "uae",
            "qatar",
            "dubai",
        ),
    )


def has_clear_trosmic_implication(article: Article) -> bool:
    text = _article_text(article)
    pillars = _matched_pillars(text)
    if any(pillar in NON_AI_TROSMIC_PILLARS for pillar in pillars):
        return True
    if is_ai_led(article):
        return _has_any(
            text,
            (
                "sports ai",
                "broadcast production",
                "fan analytics",
                "fan data",
                "venue operations",
                "sponsorship analytics",
                "athlete data",
                "media rights",
            ),
        )
    return False


def matched_pillars(article: Article) -> list[str]:
    return _matched_pillars(_article_text(article))


def primary_pillar(article: Article) -> str:
    pillars = matched_pillars(article)
    return pillars[0] if pillars else "Trosmic sports-business thesis"


def source_status(article: Article) -> str:
    text = _source_text(article)
    if _has_any(text, TIER_1_TERMS):
        return "official"
    if "estimate" in _article_text(article) or "estimated" in _article_text(article):
        return "estimated"
    if _has_any(text, TIER_2_TERMS + TIER_3_TERMS):
        return "reported"
    return "inference"


def source_credibility_score(article: Article) -> int:
    text = _source_text(article)
    if _has_any(text, TIER_1_TERMS):
        return 3
    if _has_any(text, TIER_2_TERMS):
        return 3
    if _has_any(text, TIER_3_TERMS):
        return 2
    if _has_any(text, TIER_4_TERMS):
        return 1
    return 2


def confidence_level(article: Article) -> str:
    status = article.source_status or source_status(article)
    if status == "official":
        return "High"
    if status == "reported" and article.relevance_score >= 16:
        return "High"
    if status in {"reported", "estimated"}:
        return "Medium"
    return "Low"


def why_it_matters(article: Article) -> str:
    pillar = article.affected_pillar or primary_pillar(article)
    if "Media rights" in pillar:
        return "Sports rights are still the anchor asset for audience aggregation, pricing power, and OTT retention."
    if "venue" in pillar.lower():
        return "Venue economics shape year-round utilization, premium inventory, live event yield, and Flux Halo infrastructure demand."
    if "Sponsorship" in pillar:
        return "Commercial partnerships are a leading indicator of sponsor appetite, category pricing, and measurable fan-data inventory."
    if "Franchise" in pillar:
        return "Franchise transactions reset valuation comps and governance expectations for new leagues and team owners."
    if "kabaddi" in pillar.lower():
        return "Kabaddi signals help benchmark WKCL positioning against Indian and global league demand."
    if "Investor" in pillar or "GCC" in pillar:
        return "Sports capital flows reveal where strategic investors see platform, tourism, and media-rights leverage."
    if "Rumil" in pillar:
        return "Applied intelligence in sports creates operating leverage across content, fan data, sponsorship, and venue decisions."
    return "The development affects the commercial architecture around sports, media, venues, fans, and capital."


def trosmic_implication(article: Article) -> str:
    pillar = article.affected_pillar or primary_pillar(article)
    if "Media rights" in pillar:
        return "Use this as a comp for WKCL rights packaging, OTT windows, regional language distribution, and sponsor-integrated content."
    if "venue" in pillar.lower():
        return "Map the economics against Flux Halo: capex model, event calendar density, premium hospitality, and operating data capture."
    if "Sponsorship" in pillar:
        return "Translate the deal logic into Trosmic sponsorship inventory, measurement promises, and category exclusivity strategy."
    if "Franchise" in pillar:
        return "Feed valuation and governance signals into WKCL franchise design, owner selection, and revenue-share assumptions."
    if "kabaddi" in pillar.lower():
        return "Track rights, federation, athlete, and market signals for WKCL launch timing and international expansion."
    if "Investor" in pillar or "GCC" in pillar:
        return "Use the capital signal for investor narrative, GCC/India platform framing, and potential strategic partner mapping."
    if "Rumil" in pillar:
        return "Prioritize Rumil use cases that convert intelligence into revenue: rights insights, fan cohorts, sponsor ROI, and venue operations."
    return "Assess whether this changes Trosmic's operating plan, investor story, or partnership sequencing."


def action_item(article: Article) -> str:
    pillar = article.affected_pillar or primary_pillar(article)
    if article.relevance_score >= 18:
        prefix = "Act"
    elif article.relevance_score >= TROSMIC_RELEVANCE_THRESHOLD:
        prefix = "Watch"
    else:
        prefix = "Monitor"
    if "Media rights" in pillar:
        return f"{prefix}: capture rights fee, term, platform, territory, and ad-sales model for the rights-comps tracker."
    if "venue" in pillar.lower():
        return f"{prefix}: save capex, financing source, anchor tenant, event mix, and opening timeline."
    if "Sponsorship" in pillar:
        return f"{prefix}: log sponsor category, deal length, inventory, measurement claims, and renewal triggers."
    if "Franchise" in pillar:
        return f"{prefix}: add valuation, buyer profile, league economics, and governance terms to the franchise-comps sheet."
    if "kabaddi" in pillar.lower():
        return f"{prefix}: compare the signal with WKCL market entry, federation relationships, and athlete pipeline needs."
    return f"{prefix}: route to Rumil for follow-up tagging across rights, venue, sponsorship, fan data, and capital implications."


def extract_key_facts(article: Article, max_facts: int = 3) -> list[str]:
    text = f"{article.title}. {article.summary or article.content}"
    sentences = [
        re.sub(r"\s+", " ", sentence).strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]
    facts = [
        sentence
        for sentence in sentences
        if re.search(r"(\$|rs\.?|inr|usd|%|\d)", sentence, flags=re.IGNORECASE)
    ]
    if not facts and article.summary:
        facts = [article.summary.strip()]
    return facts[:max_facts]


def _article_text(article: Article) -> str:
    return f"{article.title} {article.summary} {article.content}".lower()


def _source_text(article: Article) -> str:
    domain = urlparse(article.url).netloc.lower()
    return f"{article.source} {domain}".lower()


def _matched_pillars(text: str) -> list[str]:
    return [
        pillar
        for pillar, keywords in PILLAR_KEYWORDS.items()
        if _has_any(text, keywords)
    ]


def _pillar_score(pillars: list[str]) -> int:
    if not pillars:
        return 0
    if len(pillars) >= 3:
        return 5
    if len(pillars) == 2:
        return 4
    return 3


def _keyword_score(text: str, keywords: tuple[str, ...], cap: int) -> int:
    matches = sum(1 for keyword in keywords if _keyword_in_text(text, keyword))
    if matches >= 5:
        return cap
    if matches >= 3:
        return min(cap, 4)
    if matches >= 2:
        return min(cap, 3)
    if matches == 1:
        return min(cap, 2)
    return 0


def _strategic_score(text: str, pillars: list[str], interests: list[str]) -> int:
    score = _keyword_score(text, STRATEGIC_KEYWORDS, cap=5)
    if len(pillars) >= 2:
        score = max(score, 4)
    if any(interest.lower() in text for interest in interests):
        score = max(score, 3)
    if "india" in text or "gcc" in text or "saudi" in text or "uae" in text or "qatar" in text:
        score = min(5, score + 1)
    return score


def _actionability_score(text: str, pillar_score: int, commercial_score: int, strategic_score: int) -> int:
    if pillar_score == 0:
        return 0
    score = 1
    if commercial_score >= 3 or strategic_score >= 4:
        score += 1
    if _has_any(
        text,
        (
            "india",
            "gcc",
            "saudi",
            "uae",
            "qatar",
            "kabaddi",
            "media rights",
            "sponsorship",
            "venue",
            "franchise",
            "fan data",
        ),
    ):
        score += 1
    return min(score, 3)


def _has_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(_keyword_in_text(text, keyword) for keyword in keywords)


def _keyword_in_text(text: str, keyword: str) -> bool:
    if keyword.isalpha() and len(keyword) <= 3:
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
    return keyword in text
