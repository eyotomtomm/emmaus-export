from django import forms

PRODUCT_INTEREST_CHOICES = [
    ("", "Select Product Category"),
    ("Oilseeds", "Oilseeds (Sesame, Black Cumin, Niger Seeds, Linseed)"),
    ("Spices", "Spices (Turmeric, Coriander, Fenugreek, etc.)"),
    ("Pulses", "Pulses (Chickpeas, Beans, Mung Beans, etc.)"),
    ("Import - Vehicles", "Import - Vehicles"),
    ("Import - Chemicals", "Import - Chemicals"),
    ("Import - Machinery", "Import - Machinery"),
    ("Import - Electronics", "Import - Electronics"),
    ("Other", "Other"),
]


class EnquiryForm(forms.Form):
    """Quote/enquiry form used by the home, contact and imports pages."""

    full_name = forms.CharField(max_length=120)
    company = forms.CharField(max_length=160, required=False)
    phone = forms.CharField(max_length=40, required=False)
    email = forms.EmailField(max_length=254)
    product_interest = forms.ChoiceField(
        choices=PRODUCT_INTEREST_CHOICES,
        required=False,
    )
    message = forms.CharField(max_length=5000)

    # Bots fill in every field they find; humans never see this one. Keeping it
    # out of the email body entirely - a filled honeypot is dropped silently so
    # the sender gets no signal about why.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def is_spam(self) -> bool:
        return bool(self.data.get("website"))

    def as_email_body(self, *, source_page: str = "") -> str:
        d = self.cleaned_data
        rows = [
            ("Name", d["full_name"]),
            ("Company", d.get("company") or "-"),
            ("Email", d["email"]),
            ("Phone", d.get("phone") or "-"),
            ("Product interest", d.get("product_interest") or "-"),
        ]
        width = max(len(label) for label, _ in rows)
        lines = [f"{label.ljust(width)}  {value}" for label, value in rows]
        if source_page:
            lines.append(f"{'Sent from'.ljust(width)}  {source_page}")
        lines += ["", "Requirements", "------------", d["message"]]
        return "\n".join(lines)
