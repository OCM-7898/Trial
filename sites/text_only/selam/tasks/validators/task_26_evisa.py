from sqlalchemy import select

from app.models.partners import VisaType

from .common import nothing_was_paid


def validate(session, final_url, page_html, *, partner):
    url = final_url or ""
    if partner not in url:
        return False, f"the agent did not reach the {partner} site (final URL: {url!r})"
    if "code=" not in url:
        return False, ("no visa type was selected; the URL carries no code, so the "
                       "documents shown are the generic list rather than one type's")

    code = url.split("code=", 1)[1].split("&", 1)[0].upper()
    visa = session.scalars(select(VisaType).where(VisaType.code == code)).one_or_none()
    if visa is None:
        return False, f"{code} is not a visa type we offer"

    if visa.validity_days < 7:
        return False, (f"{visa.code} is valid for {visa.validity_days} days, which does "
                       f"not cover a seven-day visit")
    if "tourist" not in visa.name_en.lower():
        return False, f"{visa.code} is not a tourist visa"

    ok, reason = nothing_was_paid(session)
    if not ok:
        return False, reason
    return True, f"{visa.code} selected on the {partner} site, {visa.validity_days} days"
