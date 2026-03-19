"""
Email service using SendGrid.

Provides async email sending for transactional notifications.
All methods are fire-and-forget from the perspective of the caller —
email failures are logged and captured by Sentry but never propagate
as HTTP errors to the end user.

SendGrid is only active when SENDGRID_API_KEY is set. When the key
is absent, all send calls log a warning and return without sending.
This allows local development without a SendGrid account.

Usage:
    from app.core.email import EmailService
    await EmailService.send_welcome_email(payload)
    await EmailService.send_match_notification(payload)
"""
import asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From, Content
from app.core.config import settings
from app.core.logging_config import get_logger
from app.schemas.email import (
    WelcomeEmailPayload,
    MatchNotificationPayload,
    RecruiterMatchPayload,
)

logger = get_logger(__name__)


class EmailService:
    """
    Static email service. All methods are async and handle their
    own exceptions — callers never need to wrap in try/except.
    """

    @staticmethod
    async def _send(
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
    ) -> bool:
        """
        Internal method. Sends a single email via SendGrid.

        Returns True on success, False on failure.
        Never raises an exception.
        """
        if not settings.sendgrid_api_key:
            logger.warning(
                "email_skipped",
                reason="SENDGRID_API_KEY not configured",
                to_email=to_email,
                subject=subject,
            )
            return False

        try:
            message = Mail(
                from_email=From(
                    settings.sendgrid_from_email,
                    settings.sendgrid_from_name,
                ),
                to_emails=To(to_email, to_name),
                subject=subject,
                html_content=Content("text/html", html_content),
            )

            # Run blocking SendGrid call in thread pool to avoid
            # blocking the async event loop
            loop = asyncio.get_event_loop()
            sg = SendGridAPIClient(settings.sendgrid_api_key)
            response = await loop.run_in_executor(
                None, lambda: sg.send(message)
            )

            if response.status_code in (200, 201, 202):
                logger.info(
                    "email_sent",
                    to_email=to_email,
                    subject=subject,
                    status_code=response.status_code,
                )
                return True
            else:
                logger.error(
                    "email_send_failed",
                    to_email=to_email,
                    subject=subject,
                    status_code=response.status_code,
                )
                return False

        except Exception as exc:
            logger.error(
                "email_exception",
                to_email=to_email,
                subject=subject,
                error=str(exc),
            )
            try:
                import sentry_sdk
                sentry_sdk.capture_exception(exc)
            except ImportError:
                pass
            return False

    @staticmethod
    async def send_welcome_email(payload: WelcomeEmailPayload) -> bool:
        """Send a welcome email after successful account creation."""
        role_label = "recruiter" if payload.role == "recruiter" \
            else "candidate"
        subject = f"Welcome to Resume Matcher, {payload.to_name}!"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
          <h2 style="color: #2563eb;">Welcome to Resume Matcher!</h2>
          <p>Hi {payload.to_name},</p>
          <p>Your {role_label} account has been created successfully.</p>
          <p>
            <a href="{settings.frontend_url}/login"
               style="background: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px;">
              Get Started
            </a>
          </p>
          <p style="color: #6b7280; font-size: 12px;">
            If you did not create this account, please ignore this email.
          </p>
        </div>
        """
        return await EmailService._send(
            to_email=payload.to_email,
            to_name=payload.to_name,
            subject=subject,
            html_content=html_content,
        )

    @staticmethod
    async def send_match_notification(
        payload: MatchNotificationPayload,
    ) -> bool:
        """Notify a student when their resume matches a job posting."""
        subject = (
            f"New Match: {payload.job_title} at {payload.company_name} "
            f"— {payload.match_score}% fit"
        )
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
          <h2 style="color: #2563eb;">You have a new job match!</h2>
          <p>Hi {payload.to_name},</p>
          <p>
            Your resume matched <strong>{payload.job_title}</strong>
            at <strong>{payload.company_name}</strong> with a
            <strong>{payload.match_score}% compatibility score</strong>.
          </p>
          <p>
            <a href="{payload.dashboard_url}"
               style="background: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px;">
              View Match Details
            </a>
          </p>
        </div>
        """
        return await EmailService._send(
            to_email=payload.to_email,
            to_name=payload.to_name,
            subject=subject,
            html_content=html_content,
        )

    @staticmethod
    async def send_recruiter_match_notification(
        payload: RecruiterMatchPayload,
    ) -> bool:
        """Notify a recruiter when a candidate matches their job posting."""
        subject = (
            f"New Candidate Match: {payload.candidate_name} "
            f"for {payload.job_title} — {payload.match_score}% fit"
        )
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
          <h2 style="color: #2563eb;">New Candidate Match!</h2>
          <p>Hi {payload.to_name},</p>
          <p>
            <strong>{payload.candidate_name}</strong> matched your
            <strong>{payload.job_title}</strong> posting with a
            <strong>{payload.match_score}% compatibility score</strong>.
          </p>
          <p>
            <a href="{payload.dashboard_url}"
               style="background: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px;">
              Review Candidate
            </a>
          </p>
        </div>
        """
        return await EmailService._send(
            to_email=payload.to_email,
            to_name=payload.to_name,
            subject=subject,
            html_content=html_content,
        )
