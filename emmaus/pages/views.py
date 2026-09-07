import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.views.decorators.http import require_POST

from pages.forms import EnquiryForm

logger = logging.getLogger(__name__)

# Only ever redirect back to a page we serve, so `next` can't be used to bounce
# a visitor off-site.
SAFE_RETURN_TEMPLATES = {"contact", "imports", "products", "about", "sister-companies"}


def root_page_view(request):
    try:
        return render(request, 'pages/index.html')
    except TemplateDoesNotExist:
        return render(request, 'pages/404.html')


def dynamic_pages_view(request, template_name):
    try:
        return render(request, f'pages/{template_name}.html')
    except TemplateDoesNotExist:
        return render(request, f'pages/404.html')


def _return_url(request) -> str:
    nxt = (request.POST.get("next") or "").strip("/")
    if nxt in SAFE_RETURN_TEMPLATES:
        return reverse("pages:dynamic_pages", kwargs={"template_name": nxt})
    return reverse("pages:dashboard")


@require_POST
def enquiry_view(request):
    """Receive a quote/enquiry and email it to the sales mailbox.

    Replaces the previous mailto: forms, which only opened the visitor's local
    mail client - so every enquiry from a phone or webmail user was lost.
    """
    form = EnquiryForm(request.POST)
    target = _return_url(request)

    if not form.is_valid():
        messages.error(
            request,
            "Please check the highlighted fields and send the form again.",
        )
        return redirect(f"{target}#enquiry")

    # Drop bot submissions without telling the sender anything.
    if form.is_spam():
        return redirect(f"{target}?sent=1#enquiry")

    subject = request.POST.get("subject") or "Website enquiry"
    email = EmailMessage(
        subject=f"[Emmaus website] {subject} - {form.cleaned_data['full_name']}",
        body=form.as_email_body(source_page=request.build_absolute_uri(target)),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.ENQUIRY_RECIPIENTS,
        # From must stay our own authenticated mailbox or SPF/DMARC rejects it;
        # Reply-To is what makes "Reply" reach the enquirer.
        reply_to=[form.cleaned_data["email"]],
    )

    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception("Enquiry email failed to send")
        messages.error(
            request,
            "Sorry - we could not send your message just now. "
            "Please email info@emmausimportexport.com or call +251 91 1192862.",
        )
        return redirect(f"{target}#enquiry")

    messages.success(
        request,
        "Thank you - your enquiry has been sent. Our team will be in touch shortly.",
    )
    return redirect(f"{target}?sent=1#enquiry")
