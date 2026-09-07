from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

VALID = {
    "full_name": "Jane Buyer",
    "company": "Acme Foods GmbH",
    "phone": "+49 30 123456",
    "email": "jane@acme.example",
    "product_interest": "Oilseeds",
    "message": "2x20FCL Humera sesame, Q1 shipment.",
    "next": "contact",
    "subject": "Quote request",
    "website": "",
}


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EnquiryFormTests(TestCase):
    """The form used to be a mailto: link, which lost every enquiry from a
    phone or webmail visitor. These pin the server-side replacement."""

    url = "/enquiry/"

    def test_valid_enquiry_is_emailed_to_the_sales_mailbox(self):
        response = self.client.post(self.url, VALID)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, settings.ENQUIRY_RECIPIENTS)
        self.assertIn("Jane Buyer", sent.subject)
        self.assertIn("2x20FCL Humera sesame", sent.body)

    def test_reply_to_is_the_enquirer_but_from_stays_our_mailbox(self):
        # Putting the enquirer in From would fail SPF/DMARC and bounce.
        self.client.post(self.url, VALID)

        sent = mail.outbox[0]
        self.assertEqual(sent.reply_to, ["jane@acme.example"])
        self.assertEqual(sent.from_email, settings.DEFAULT_FROM_EMAIL)

    def test_honeypot_submission_is_dropped_without_sending(self):
        response = self.client.post(self.url, {**VALID, "website": "http://spam.example"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_submission_sends_nothing(self):
        response = self.client.post(
            self.url,
            {**VALID, "email": "not-an-email", "full_name": "", "message": ""},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_get_is_rejected(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_next_only_redirects_to_pages_we_serve(self):
        # `next` must not be usable to bounce a visitor off-site.
        response = self.client.post(self.url, {**VALID, "next": "https://evil.example"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], f"{reverse('pages:dashboard')}?sent=1#enquiry")

    def test_failure_to_send_tells_the_visitor_instead_of_500ing(self):
        with override_settings(
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
            EMAIL_HOST="127.0.0.1",
            EMAIL_PORT=1,  # nothing listening -> send() raises
        ):
            response = self.client.post(self.url, VALID, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "could not send your message")


class PageTests(TestCase):
    def test_every_public_page_renders(self):
        for path in [
            "/",
            "/about/",
            "/products/",
            "/contact/",
            "/imports/",
            "/sister-companies/",
            "/privacy/",
            "/terms/",
        ]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_no_mailto_forms_remain(self):
        for path in ["/", "/contact/", "/imports/"]:
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertIn('action="/enquiry/"', html)
                self.assertNotIn('<form action="mailto:', html)
