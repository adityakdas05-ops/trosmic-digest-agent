from __future__ import annotations

import json
from pathlib import Path

from trosmic_digest_agent.models import Article, Digest
from trosmic_digest_agent.summarizer import summarize_article
from trosmic_digest_agent.trosmic_policy import TROSMIC_CONTEXT, extract_key_facts


def render_markdown(digest: Digest, summary_sentences: int = 3) -> str:
    lines = [
        f"# {digest.title}",
        "",
        f"Generated: {digest.generated_at.isoformat()}",
    ]
    if digest.date:
        lines.append(f"Digest date: {digest.date}")
    lines.append("")

    if digest.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in digest.warnings)
        lines.append("")

    lines.extend(
        [
            "## 1. Executive Signal of the Day",
            "",
            _executive_signal(digest),
            "",
            "## 2. Top 10 Trosmic-Relevant Developments",
            "",
        ]
    )

    if not digest.articles:
        lines.extend(
            [
                "No qualifying items crossed the Trosmic Relevance Gate today. Generic AI, generic tech, generic crypto, and general political stories are intentionally excluded unless tied to sports, media, venues, fan data, or Trosmic strategy.",
                "",
            ]
        )
    else:
        for index, article in enumerate(digest.articles[:10], start=1):
            lines.extend(_render_development(index, article, summary_sentences))

    lines.extend(
        [
            "## 3. Opportunity Radar",
            "",
            *_opportunity_radar(digest),
            "",
            "## 4. Risk/Weak Signal Watchlist",
            "",
            *_risk_watchlist(digest),
            "",
            "## 5. Data Points to Save",
            "",
            *_data_points(digest),
            "",
            "## 6. Strategic Op-Ed",
            "",
            _strategic_op_ed(digest),
            "",
        ]
    )

    return "\n".join(lines)


def _executive_signal(digest: Digest) -> str:
    if not digest.articles:
        return (
            "The useful signal is absence: nothing should enter Trosmic's daily brief unless it "
            "clears the sports-business relevance bar. The agent is now sports/media/venue/capital "
            "first."
        )
    top = digest.articles[0]
    return (
        f"{top.affected_pillar or 'Sports business'} is the lead signal via "
        f"[{top.title}]({top.url}). {top.trosmic_implication}"
    )


def _render_development(index: int, article: Article, summary_sentences: int) -> list[str]:
    facts = extract_key_facts(article)
    summary = summarize_article(article, summary_sentences) or article.title
    metadata = [
        f"Source: {article.source}",
        f"Gate score: {article.relevance_score}/21",
        f"Confidence: {article.confidence_level}",
    ]
    published = article.normalized_published_at()
    if published:
        metadata.append(f"Published: {published.isoformat()}")
    return [
        f"### {index}. [{article.title}]({article.url})",
        "",
        f"_{' | '.join(metadata)}_",
        "",
        f"- What happened: {summary}",
        f"- Key facts/numbers: {'; '.join(facts) if facts else 'No hard number in the fetched excerpt; save source for follow-up.'}",
        f"- Source status: {article.source_status}",
        f"- Why it matters: {article.why_it_matters}",
        f"- Trosmic implication: {article.trosmic_implication}",
        f"- Affected pillar: {article.affected_pillar or 'Trosmic sports-business thesis'}",
        f"- Action/watch item: {article.action_item}",
        f"- Confidence level: {article.confidence_level}",
        "",
    ]


def _opportunity_radar(digest: Digest) -> list[str]:
    if not digest.articles:
        return [
            "- Keep scanning sports media rights, OTT packaging, venue financing, franchise valuations, sponsorship deals, and India/GCC sports capital flows.",
            "- Use the sports-first query set in config to seed manual monitoring or a future search connector.",
        ]
    bullets: list[str] = []
    for article in digest.articles[:5]:
        bullets.append(f"- {article.affected_pillar or 'Sports business'}: {article.action_item}")
    return bullets


def _risk_watchlist(digest: Digest) -> list[str]:
    risky = [
        article
        for article in digest.articles
        if article.confidence_level == "Low"
        or any(word in f"{article.title} {article.summary}".lower() for word in ("regulation", "betting", "privacy", "delay", "debt", "lawsuit"))
    ]
    if not risky:
        return [
            "- No low-confidence or regulatory weak signal crossed the gate in today's fetched set.",
            "- Continue watching betting/fantasy rules, media regulation, foreign investment, venue financing stress, and data privacy.",
        ]
    return [
        f"- {article.title}: {article.source_status} source status, {article.confidence_level.lower()} confidence. {article.action_item}"
        for article in risky[:5]
    ]


def _data_points(digest: Digest) -> list[str]:
    points: list[str] = []
    for article in digest.articles:
        for fact in extract_key_facts(article, max_facts=2):
            points.append(f"- {article.affected_pillar or 'Sports business'}: {fact}")
            if len(points) == 8:
                return points
    if points:
        return points
    return [
        "- No hard numbers were available in today's qualifying excerpts.",
        "- Prioritize saving rights fees, deal terms, franchise valuations, sponsorship value, venue capex, audience metrics, and investor identity.",
    ]


def _strategic_op_ed(digest: Digest) -> str:
    lead = digest.articles[0] if digest.articles else None
    lead_title = lead.title if lead else "today's sports-rights and venue-capital scan"
    lead_pillar = lead.affected_pillar if lead else "media rights, venues, sponsorship, fan data, and capital"
    lead_implication = (
        lead.trosmic_implication
        if lead
        else "Trosmic should keep the daily operating lens on rights, venues, sponsorship, fan data, league economics, and capital flows."
    )
    return (
        f"{TROSMIC_CONTEXT}\n\n"
        f"The central signal from {lead_title} is not just the item itself. It is the way {lead_pillar} now works as a connected operating system. Sports companies are no longer rewarded only for owning a team, staging an event, or selling a broadcast package. The premium is moving toward groups that can join rights, venues, sponsorship, data, content, and capital into one repeatable machine. That is the strategic frame Trosmic should keep in front of investors and partners.\n\n"
        "The first-order reading is commercial: rights fees, sponsorship prices, venue capex, and franchise values remain the most visible scoreboard. Those numbers matter because they create comparables for WKCL, Flux Halo, media distribution, and investor conversations. But the second-order reading is more important. A rights deal is rarely just a rights deal now. It changes the shape of content windows, the bargaining power of platforms, the data a league can capture, the sponsor formats it can sell, and the local venues that benefit from demand. A venue project is rarely just real estate. It becomes a live-events calendar, a hospitality engine, a ticketing data source, a brand-experience surface, and sometimes a government tourism asset.\n\n"
        "That is why a sports-business-first digest is the right operating lens for Trosmic. The core questions are commercial and operational: Who controls the fan relationship? Which platform is paying for live scarcity? What inventory can a sponsor measure? Which venues can be filled beyond matchday? Which investors are buying strategic exposure rather than vanity ownership? Where do India and the GCC create a bridge between audience scale, capital appetite, and entertainment infrastructure? Rumil should be built around those questions as a sports operating intelligence layer.\n\n"
        "The third-order implication is that Trosmic's advantage will come from compounding information across pillars. WKCL should not be designed only as a kabaddi property. It should be designed as a rights product, a franchise product, a venue-utilization product, a sponsor-measurement product, and a D2F fan-data product from day one. Flux Halo should not be positioned only as infrastructure. It should be positioned as the physical layer that lets rights, content, hospitality, ticketing, and fan identity become measurable. Rumil should tell management where rights value is moving, which fan cohorts are monetizable, which sponsors need proof, which athletes have storytelling leverage, and which markets can support league expansion.\n\n"
        "This matters especially in the India/GCC corridor. India offers audience density, cricket-proof lessons in rights monetization, emerging sports demand, and digital fan behavior. The GCC offers capital, venue ambition, tourism strategy, and a willingness to use sport as platform infrastructure. Trosmic can sit between those forces if it avoids the trap of becoming a single-asset company. The thesis is not simply 'build a league' or 'build venues.' The thesis is to build a sports operating company where each pillar improves the economics of the others.\n\n"
        f"The action from today's signal is therefore practical: {lead_implication} Every qualifying story should be converted into a data point, a comparable, a watch item, or a partner map. Rights stories should feed packaging assumptions. Venue stories should feed capex and utilization models. Sponsorship stories should feed inventory and measurement design. Franchise stories should feed governance and valuation architecture. Fan-data and broadcast-technology stories should feed Rumil only when they improve revenue, operations, content, or measurable audience ownership. That discipline is what keeps the company from chasing noise.\n\n"
        "For investors, this produces a sharper narrative. Trosmic is not pitching exposure to a sport alone. It is pitching a platform that can capture value as sport, media, entertainment, venues, and data converge. For operators, it creates a daily decision system. The right question is not whether a story is interesting. The right question is whether it changes what Trosmic should build, price, partner, buy, finance, or monitor. That is the line this digest now enforces."
    )


def write_digest_files(
    digest: Digest,
    output_dir: str | Path,
    summary_sentences: int = 3,
) -> tuple[Path, Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stem = digest.date or digest.generated_at.date().isoformat()
    markdown_path = directory / f"{stem}.md"
    json_path = directory / f"{stem}.json"
    debug_path = directory / f"debug-{stem}.json"
    markdown_path.write_text(render_markdown(digest, summary_sentences), encoding="utf-8")
    json_path.write_text(json.dumps(digest.to_dict(), indent=2), encoding="utf-8")
    debug_path.write_text(json.dumps(digest.debug.to_dict(), indent=2), encoding="utf-8")
    return markdown_path, json_path, debug_path
