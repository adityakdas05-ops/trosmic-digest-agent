from __future__ import annotations

import mimetypes
import os
import smtplib
from collections.abc import Mapping
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

REQUIRED_SMTP_SETTINGS = (
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "EMAIL_FROM",
    "EMAIL_TO",
)

MISSING_SMTP_SETTINGS_MESSAGE = (
    "SMTP settings missing. Configure SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
    "SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO."
)


class MissingSMTPSettingsError(RuntimeError):
    pass


@dataclass(slots=True)
class EmailSettings:
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    email_from: str
    email_to: list[str]
    email_cc: list[str]
    use_tls: bool = True


def load_email_settings(env: Mapping[str, str] | None = None) -> EmailSettings:
    values = os.environ if env is None else env
    missing = [name for name in REQUIRED_SMTP_SETTINGS if not values.get(name)]
    if missing:
        raise MissingSMTPSettingsError(MISSING_SMTP_SETTINGS_MESSAGE)

    try:
        smtp_port = int(values["SMTP_PORT"])
    except ValueError as exc:
        raise MissingSMTPSettingsError("SMTP_PORT must be an integer.") from exc

    return EmailSettings(
        smtp_host=values["SMTP_HOST"],
        smtp_port=smtp_port,
        smtp_username=values["SMTP_USERNAME"],
        smtp_password=values["SMTP_PASSWORD"],
        email_from=values["EMAIL_FROM"],
        email_to=_split_addresses(values["EMAIL_TO"]),
        email_cc=_split_addresses(values.get("EMAIL_CC", "")),
        use_tls=_as_bool(values.get("SMTP_USE_TLS", "true")),
    )


def send_digest_email(
    markdown_path: str | Path,
    json_path: str | Path | None = None,
    debug_json_path: str | Path | None = None,
    *,
    digest_date: str,
    settings: EmailSettings | None = None,
) -> None:
    resolved_settings = settings or load_email_settings()
    message = build_digest_email(
        markdown_path,
        json_path,
        debug_json_path,
        digest_date=digest_date,
        settings=resolved_settings,
    )

    if resolved_settings.smtp_port == 465:
        with smtplib.SMTP_SSL(
            resolved_settings.smtp_host,
            resolved_settings.smtp_port,
            timeout=30,
        ) as smtp:
            smtp.login(resolved_settings.smtp_username, resolved_settings.smtp_password)
            smtp.send_message(message)
        return

    with smtplib.SMTP(
        resolved_settings.smtp_host,
        resolved_settings.smtp_port,
        timeout=30,
    ) as smtp:
        if resolved_settings.use_tls:
            smtp.starttls()
        smtp.login(resolved_settings.smtp_username, resolved_settings.smtp_password)
        smtp.send_message(message)


def build_digest_email(
    markdown_path: str | Path,
    json_path: str | Path | None = None,
    debug_json_path: str | Path | None = None,
    *,
    digest_date: str,
    settings: EmailSettings,
) -> EmailMessage:
    markdown_file = Path(markdown_path)
    markdown = markdown_file.read_text(encoding="utf-8")

    message = EmailMessage()
    message["Subject"] = f"Trosmic Daily Intelligence Digest - {digest_date}"
    message["From"] = settings.email_from
    message["To"] = ", ".join(settings.email_to)
    if settings.email_cc:
        message["Cc"] = ", ".join(settings.email_cc)
    message.set_content(markdown)

    attachment_paths = (
        markdown_file,
        _optional_path(json_path),
        _optional_path(debug_json_path),
    )
    for attachment_path in attachment_paths:
        if attachment_path and attachment_path.exists():
            _attach_file(message, attachment_path)

    return message


def _attach_file(message: EmailMessage, path: Path) -> None:
    content_type, _ = mimetypes.guess_type(path.name)
    maintype, subtype = (content_type or "application/octet-stream").split("/", 1)
    message.add_attachment(
        path.read_bytes(),
        maintype=maintype,
        subtype=subtype,
        filename=path.name,
    )


def _optional_path(path: str | Path | None) -> Path | None:
    return Path(path) if path else None


def _split_addresses(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _as_bool(value: str) -> bool:
    return value.strip().lower() not in {"0", "false", "no", "off"}
