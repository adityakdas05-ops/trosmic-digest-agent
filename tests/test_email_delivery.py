from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from trosmic_digest_agent.delivery.email import (
    MISSING_SMTP_SETTINGS_MESSAGE,
    EmailSettings,
    MissingSMTPSettingsError,
    build_digest_email,
    load_email_settings,
    send_digest_email,
)


class EmailDeliveryTests(unittest.TestCase):
    def test_missing_settings_raises_clear_error(self) -> None:
        with self.assertRaises(MissingSMTPSettingsError) as context:
            load_email_settings({})

        self.assertEqual(str(context.exception), MISSING_SMTP_SETTINGS_MESSAGE)

    def test_builds_digest_email_with_body_and_existing_attachments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            markdown_path = root / "2026-05-17.md"
            json_path = root / "2026-05-17.json"
            debug_path = root / "debug-2026-05-17.json"
            markdown_path.write_text("# Digest\n\nBody", encoding="utf-8")
            json_path.write_text('{"ok": true}', encoding="utf-8")
            debug_path.write_text('{"debug": true}', encoding="utf-8")

            message = build_digest_email(
                markdown_path,
                json_path,
                debug_path,
                digest_date="2026-05-17",
                settings=_settings(),
            )

        self.assertEqual(
            message["Subject"],
            "Trosmic Daily Intelligence Digest - 2026-05-17",
        )
        self.assertEqual(message["From"], "digest@example.com")
        self.assertEqual(message["To"], "you@example.com")
        self.assertEqual(message["Cc"], "ops@example.com")
        body = message.get_body()
        self.assertIsNotNone(body)
        self.assertIn("# Digest", body.get_content())
        filenames = [part.get_filename() for part in message.iter_attachments()]
        self.assertEqual(
            filenames,
            ["2026-05-17.md", "2026-05-17.json", "debug-2026-05-17.json"],
        )

    def test_send_uses_smtp_with_tls_and_login(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            markdown_path = Path(directory) / "2026-05-17.md"
            markdown_path.write_text("# Digest", encoding="utf-8")
            smtp = MagicMock()
            smtp_context = MagicMock()
            smtp_context.__enter__.return_value = smtp

            smtp_patch_target = "trosmic_digest_agent.delivery.email.smtplib.SMTP"
            with patch(smtp_patch_target, return_value=smtp_context):
                send_digest_email(
                    markdown_path,
                    digest_date="2026-05-17",
                    settings=_settings(),
                )

        smtp.starttls.assert_called_once_with()
        smtp.login.assert_called_once_with("user", "password")
        smtp.send_message.assert_called_once()


def _settings() -> EmailSettings:
    return EmailSettings(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="user",
        smtp_password="password",
        email_from="digest@example.com",
        email_to=["you@example.com"],
        email_cc=["ops@example.com"],
    )


if __name__ == "__main__":
    unittest.main()
