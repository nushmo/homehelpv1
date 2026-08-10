import logging
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

logger = logging.getLogger("homehelp.controller.legal")

router = APIRouter(tags=["Legal & Compliance"])


@router.get("/privacy-policy", response_class=HTMLResponse)
def privacy_policy():
    """Privacy Policy Endpoint for Meta App Review and Publishing."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Privacy Policy - HomeHelp AI</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1f2937; max-width: 800px; margin: 40px auto; padding: 0 20px; background-color: #f9fafb; }
            .card { background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; }
            h1 { color: #111827; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
            h2 { color: #1f2937; margin-top: 24px; }
            p, li { color: #4b5563; }
            .footer { margin-top: 32px; font-size: 0.875rem; color: #9ca3af; border-top: 1px solid #e5e7eb; padding-top: 16px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Privacy Policy for HomeHelp AI</h1>
            <p><strong>Effective Date:</strong> August 11, 2026</p>

            <p>HomeHelp AI ("we", "our", or "us") respects your privacy and is committed to protecting the personal data of our users. This Privacy Policy describes how we collect, use, and safeguard information when you interact with our WhatsApp-first domestic worker salary management service.</p>

            <h2>1. Information We Collect</h2>
            <ul>
                <li><strong>Phone Number & Profile Name:</strong> Provided automatically by WhatsApp Cloud API when you message our service.</li>
                <li><strong>Worker Salary & Attendance Data:</strong> Names, monthly salaries, weekly off days, attendance exceptions (absent/half days), advances, and bonuses provided directly by you in chat.</li>
                <li><strong>Voice Notes:</strong> Temporary audio files sent by you, processed for speech-to-text transcription via Groq Whisper API. Audio binaries are not retained after intent extraction.</li>
            </ul>

            <h2>2. How We Use Information</h2>
            <ul>
                <li>To calculate monthly salary payments, deductions, advances, bonuses, and net payable amounts.</li>
                <li>To format and send WhatsApp salary summaries to you.</li>
                <li>To maintain product analytics and user lifecycle records.</li>
            </ul>

            <h2>3. Data Security</h2>
            <p>All data is stored securely using encrypted cloud database infrastructure (Supabase PostgreSQL). We do not sell, rent, or trade your personal data to third parties.</p>

            <h2>4. Your Rights & Data Deletion</h2>
            <p>You may request the deletion of your account and worker data at any time by sending <code>Remove [Worker Name]</code> in WhatsApp or emailing our support contact at <strong>vicks8cool@gmail.com</strong>.</p>

            <h2>5. Contact Us</h2>
            <p>If you have questions about this policy, please contact us at <strong>vicks8cool@gmail.com</strong>.</p>

            <div class="footer">
                &copy; 2026 HomeHelp AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/terms", response_class=HTMLResponse)
def terms_of_service():
    """Terms of Service Endpoint for Meta App Review and Publishing."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Terms of Service - HomeHelp AI</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1f2937; max-width: 800px; margin: 40px auto; padding: 0 20px; background-color: #f9fafb; }
            .card { background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; }
            h1 { color: #111827; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
            h2 { color: #1f2937; margin-top: 24px; }
            p, li { color: #4b5563; }
            .footer { margin-top: 32px; font-size: 0.875rem; color: #9ca3af; border-top: 1px solid #e5e7eb; padding-top: 16px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Terms of Service for HomeHelp AI</h1>
            <p><strong>Effective Date:</strong> August 11, 2026</p>

            <h2>1. Acceptance of Terms</h2>
            <p>By using HomeHelp AI via WhatsApp, you agree to these Terms of Service. If you do not agree, please discontinue using the service.</p>

            <h2>2. Description of Service</h2>
            <p>HomeHelp AI is an automated domestic worker salary and attendance tracking assistant provided via Meta WhatsApp Cloud API.</p>

            <h2>3. User Responsibilities</h2>
            <p>You are responsible for ensuring the accuracy of worker salary details, working days, and attendance exceptions logged in your account.</p>

            <h2>4. Limitation of Liability</h2>
            <p>HomeHelp AI provides deterministic salary calculations based on user input. We are not liable for errors resulting from inaccurate user data entry.</p>

            <h2>5. Service Contact</h2>
            <p>For questions or support, email <strong>vicks8cool@gmail.com</strong>.</p>

            <div class="footer">
                &copy; 2026 HomeHelp AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/data-deletion", response_class=HTMLResponse)
def data_deletion():
    """User Data Deletion Instructions Endpoint for Meta App Review."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>User Data Deletion Instructions - HomeHelp AI</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1f2937; max-width: 800px; margin: 40px auto; padding: 0 20px; background-color: #f9fafb; }
            .card { background: #ffffff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; }
            h1 { color: #111827; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
            h2 { color: #1f2937; margin-top: 24px; }
            p, li { color: #4b5563; }
            .footer { margin-top: 32px; font-size: 0.875rem; color: #9ca3af; border-top: 1px solid #e5e7eb; padding-top: 16px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>User Data Deletion Instructions</h1>
            <p><strong>HomeHelp AI</strong> values user privacy and provides straightforward mechanisms to delete your stored data.</p>

            <h2>Option 1: In-App WhatsApp Command (Instant)</h2>
            <p>To delete a registered worker and associated event logs, send a message in your WhatsApp chat:</p>
            <pre style="background:#f3f4f6; padding:12px; border-radius:6px;">Remove [Worker Name]</pre>
            <p>Example: <code>Remove Sunita</code></p>

            <h2>Option 2: Complete Account Deletion Request via Email</h2>
            <p>To request complete deletion of your phone number, account history, workers, and events from our databases:</p>
            <ol>
                <li>Send an email from your registered contact address to <strong>vicks8cool@gmail.com</strong>.</li>
                <li>Include the subject line: <code>Data Deletion Request - [Your Phone Number]</code>.</li>
                <li>Our team will purge all records associated with your account from Supabase within 48 hours and send you a confirmation.</li>
            </ol>

            <div class="footer">
                &copy; 2026 HomeHelp AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
