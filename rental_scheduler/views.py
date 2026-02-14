"""
Views for the rental scheduler application.

Optimized for performance:
- Queries use select_related/prefetch_related to avoid N+1
- Calendar feed endpoint is read-only (no DB writes)
- Payloads minimized with .only() where appropriate
"""
import difflib
import json
import logging
import re
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, timedelta

from django import forms
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from rental_scheduler.utils.ai_parser import parse_description_with_ai
from rental_scheduler.utils.events import (
    event_to_calendar_json,
    get_call_reminder_sunday,
    normalize_event_datetimes,
)
from rental_scheduler.utils.phone import format_phone

from .forms import CalendarImportForm, JobForm
from .models import (
    Calendar,
    Job,
    WorkOrderLineV2,
    WorkOrderNumberSequence,
    WorkOrderV2,
)

# ============================================================================
# Work Order (v2) / Classic Accounting helpers
# ============================================================================


def _accounting_is_configured() -> bool:
    """
    Return True when Classic Accounting DB is configured for real use.

    In tests/CI/dev without Classic env vars, we configure a placeholder SQLite
    DB for the alias; in that case we must not attempt to query Classic tables.
    """

    accounting_db = (settings.DATABASES or {}).get("accounting") or {}
    return accounting_db.get("ENGINE") == "django.db.backends.postgresql"


def _get_tax_rate_for_customer(customer_org_id) -> Decimal:
    if not customer_org_id or not _accounting_is_configured():
        return Decimal("0.0000")
    try:
        from accounting_integration.services.tax_applicability import get_effective_tax_rate

        rate, _exempt = get_effective_tax_rate(int(customer_org_id))
        return rate
    except Exception:
        return Decimal("0.0000")


_DUPLICATE_NAME_THRESHOLD = 0.82
_DUPLICATE_MAX_RESULTS = 10
_DUPLICATE_CANDIDATE_LIMIT = 200


def _normalize_simple_text(value: str) -> str:
    text = (value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _strip_classic_name_suffix(value: str) -> str:
    if not value:
        return ""
    value = str(value).strip()
    value = re.sub(r"\s*\(\d+\)\s*$", "", value)
    value = re.sub(r"\s*#\d+\s*$", "", value)
    return value.strip()


def _normalize_name(value: str) -> str:
    return _normalize_simple_text(_strip_classic_name_suffix(value))


def _normalize_phone_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _normalize_phone_tail(value: str) -> str:
    digits = _normalize_phone_digits(value)
    if not digits:
        return ""
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) > 10:
        digits = digits[-10:]
    if len(digits) < 7:
        return ""
    return digits


def _phone_matches(target_digits: str, candidate_digits: str) -> bool:
    if not target_digits or not candidate_digits:
        return False
    if len(target_digits) >= 10 and len(candidate_digits) >= 10:
        return target_digits[-10:] == candidate_digits[-10:]
    return target_digits[-7:] == candidate_digits[-7:]


def _normalize_zip(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _normalize_state(value: str) -> str:
    return (value or "").strip().upper()


def _name_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _address_matches(target: dict, candidate: dict) -> bool:
    target_line = _normalize_simple_text(target.get("address_line1") or "")
    candidate_line = _normalize_simple_text(candidate.get("address_line1") or "")
    if not target_line or not candidate_line or target_line != candidate_line:
        return False

    target_zip = _normalize_zip(target.get("zip") or "")
    candidate_zip = _normalize_zip(candidate.get("zip") or "")
    if target_zip and candidate_zip:
        return target_zip == candidate_zip

    target_city = _normalize_simple_text(target.get("city") or "")
    candidate_city = _normalize_simple_text(candidate.get("city") or "")
    target_state = _normalize_state(target.get("state") or "")
    candidate_state = _normalize_state(candidate.get("state") or "")

    return bool(target_city and target_state and target_city == candidate_city and target_state == candidate_state)


def _find_possible_customer_duplicates(payload: dict) -> list[dict]:
    from accounting_integration.models import Org, OrgAddress

    name_raw = payload.get("name") or ""
    phone_raw = payload.get("phone") or ""
    address_line1 = payload.get("address_line1") or ""
    city = payload.get("city") or ""
    state = payload.get("state") or ""
    zip_code = payload.get("zip") or ""

    normalized_name = _normalize_name(name_raw)
    target_phone_digits = _normalize_phone_tail(phone_raw)
    target_zip = _normalize_zip(zip_code)

    if not (normalized_name or target_phone_digits or address_line1 or target_zip):
        return []

    candidate_ids: set[int] = set()
    org_qs = Org.objects.using("accounting").filter(orgdiscriminator="CUST")

    if normalized_name:
        name_tokens = [t for t in normalized_name.split(" ") if len(t) > 2][:3]
        if name_tokens:
            name_q = models.Q()
            for token in name_tokens:
                name_q |= models.Q(orgname__icontains=token)
            candidate_ids.update(
                list(
                    org_qs.filter(name_q).values_list("org_id", flat=True)[:_DUPLICATE_CANDIDATE_LIMIT]
                )
            )

    if target_phone_digits:
        last4 = target_phone_digits[-4:]
        if last4:
            candidate_ids.update(
                list(
                    org_qs.filter(phone1__icontains=last4).values_list("org_id", flat=True)[:_DUPLICATE_CANDIDATE_LIMIT]
                )
            )

    addr_token = []
    if not target_zip:
        addr_token = [token for token in _normalize_simple_text(address_line1).split(" ") if token]
    if target_zip or addr_token:
        addr_qs = OrgAddress.objects.using("accounting").filter(addresstype="BILLTO")
        if target_zip:
            addr_qs = addr_qs.filter(txtzip__icontains=target_zip)
        elif addr_token:
            addr_qs = addr_qs.filter(streetone__icontains=addr_token[0])
        candidate_ids.update(
            list(addr_qs.values_list("orgid_id", flat=True)[:_DUPLICATE_CANDIDATE_LIMIT])
        )

    if not candidate_ids:
        return []

    candidate_list = list(candidate_ids)[:_DUPLICATE_CANDIDATE_LIMIT]
    orgs = list(org_qs.filter(org_id__in=candidate_list))
    if not orgs:
        return []

    org_ids = [org.org_id for org in orgs]
    address_map: dict[int, dict] = {}
    addr_rows = (
        OrgAddress.objects.using("accounting")
        .filter(orgid_id__in=org_ids, addresstype="BILLTO")
        .order_by("orgid_id", "-is_default", "-gen_addr_id")
    )
    for addr in addr_rows:
        org_id = addr.orgid_id
        if org_id in address_map:
            continue
        address_map[org_id] = {
            "address_line1": addr.streetone or "",
            "address_line2": addr.streettwo or "",
            "city": addr.txtcity or "",
            "state": addr.txtstate or "",
            "zip": addr.txtzip or "",
        }

    results: list[dict] = []
    for org in orgs:
        reasons: list[str] = []
        org_phone_digits = _normalize_phone_tail(org.phone1 or "")
        if target_phone_digits and org_phone_digits and _phone_matches(target_phone_digits, org_phone_digits):
            reasons.append("phone")

        org_name_norm = _normalize_name(org.orgname or "")
        name_score = _name_similarity(normalized_name, org_name_norm)
        if normalized_name and org_name_norm:
            if name_score >= _DUPLICATE_NAME_THRESHOLD or (
                (normalized_name in org_name_norm or org_name_norm in normalized_name)
                and min(len(normalized_name), len(org_name_norm)) >= 4
            ):
                reasons.append("name")

        addr_payload = address_map.get(org.org_id, {})
        if _address_matches(
            {
                "address_line1": address_line1,
                "city": city,
                "state": state,
                "zip": zip_code,
            },
            addr_payload,
        ):
            reasons.append("address")

        if not reasons:
            continue

        score = 0.0
        if "phone" in reasons:
            score += 1.2
        if "address" in reasons:
            score += 0.9
        if "name" in reasons:
            score += 0.5 + (name_score * 0.5)

        results.append(
            {
                "org_id": org.org_id,
                "name": org.orgname or "",
                "phone": org.phone1 or "",
                "contact": org.contact1 or "",
                "email": org.email or "",
                "address_line1": addr_payload.get("address_line1", ""),
                "address_line2": addr_payload.get("address_line2", ""),
                "city": addr_payload.get("city", ""),
                "state": addr_payload.get("state", ""),
                "zip": addr_payload.get("zip", ""),
                "match_reasons": reasons,
                "name_score": round(name_score, 3) if name_score else 0.0,
                "score": round(score, 3),
            }
        )

    results.sort(key=lambda item: (item.get("score", 0), item.get("name", "")), reverse=True)
    return results[:_DUPLICATE_MAX_RESULTS]


def _parse_decimal(value: str, *, field_name: str) -> Decimal:
    cleaned = str(value).strip().replace("$", "").replace(",", "")
    if not cleaned:
        return Decimal("0.00")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, TypeError, ValueError):
        raise forms.ValidationError(f"Invalid number for {field_name}.")


def _parse_line_items_from_post(request) -> list[dict]:
    itemids = request.POST.getlist("line_itemid")
    qtys = request.POST.getlist("line_qty")
    prices = request.POST.getlist("line_price")
    itemnumbers = request.POST.getlist("line_itemnumber_snapshot")
    descs = request.POST.getlist("line_description_snapshot")

    # Normalize lengths (missing lists become empty strings)
    max_len = max(len(itemids), len(qtys), len(prices), len(itemnumbers), len(descs), 0)

    def _get(lst, idx):
        return lst[idx] if idx < len(lst) else ""

    lines: list[dict] = []
    for i in range(max_len):
        raw_itemid = str(_get(itemids, i)).strip()
        if not raw_itemid:
            continue

        try:
            itemid = int(raw_itemid)
        except (TypeError, ValueError):
            raise forms.ValidationError(f"Invalid itemid at line {i + 1}.")

        qty = _parse_decimal(_get(qtys, i), field_name=f"qty (line {i + 1})")
        price = _parse_decimal(_get(prices, i), field_name=f"price (line {i + 1})")

        lines.append(
            {
                "itemid": itemid,
                "qty": qty,
                "price": price,
                "itemnumber_snapshot": str(_get(itemnumbers, i)).strip(),
                "description_snapshot": str(_get(descs, i)).strip(),
            }
        )

    return lines


def _get_workorder_back_context(request, *, job_id: int | None = None) -> dict:
    """
    Compute back_url and back_label for Work Order pages.

    Reads the 'next' query param (GET or POST), validates it is same-host,
    and returns a dict with:
      - back_url: validated URL or fallback to job_list
      - back_label: human-readable label based on the URL
      - next_value: the raw validated value (to embed in form for POST round-trip)
    """

    def _with_query(url: str, extra_params: dict[str, str | int]) -> str:
        """
        Merge query params into a URL while preserving existing duplicates for
        keys we don't touch (e.g., calendars=1&calendars=2).
        """
        from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

        parts = urlsplit(url)
        existing_pairs = parse_qsl(parts.query, keep_blank_values=True)
        extra_keys = set(extra_params.keys())

        merged_pairs = [(k, v) for (k, v) in existing_pairs if k not in extra_keys]
        for k, v in extra_params.items():
            if v is None or v == "":
                continue
            merged_pairs.append((k, str(v)))

        return urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                urlencode(merged_pairs, doseq=True),
                parts.fragment,
            )
        )

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    fallback = reverse("rental_scheduler:job_list")

    # Validate: must be same-host (no open redirect)
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        back_url = next_url
    else:
        back_url = fallback

    # Determine label
    from urllib.parse import urlsplit

    calendar_url = reverse("rental_scheduler:calendar")
    job_list_url = reverse("rental_scheduler:job_list")
    back_path = urlsplit(back_url).path

    if back_path.startswith(calendar_url):
        back_label = "Back to Calendar"
        if job_id:
            back_url = _with_query(back_url, {"open_job": job_id})
    elif back_path.startswith(job_list_url):
        back_label = "Back to Jobs"
        if job_id:
            back_url = _with_query(back_url, {"open_job": job_id})
    else:
        back_label = "Back"

    return {
        "back_url": back_url,
        "back_label": back_label,
        "next_value": back_url if back_url != fallback else "",
    }


def _render_workorder_v2_form(
    request,
    *,
    job: Job,
    work_order: WorkOrderV2 | None,
    initial: dict | None = None,
    errors: dict | None = None,
):
    from rental_scheduler.constants import US_STATE_TERRITORY_CHOICES
    
    sales_reps = []
    if _accounting_is_configured():
        try:
            from accounting_integration.models import AcctSalesRep
            sales_reps = list(AcctSalesRep.objects.using("accounting").filter(active=True).order_by("rep_name"))
        except Exception:
            pass
    back_ctx = _get_workorder_back_context(request, job_id=job.pk)
    # Title format: "Work Order: Customer (Phone)" to match header
    title = f"Work Order: {job.display_name}"
    if job.phone:
        title += f" ({job.phone})"

    initial_data = initial or {}
    initial_customer = None
    customer_org_id = None
    customer_org_id_raw = initial_data.get("customer_org_id", "")
    customer_org_id_raw = str(customer_org_id_raw).strip() if customer_org_id_raw is not None else ""
    if customer_org_id_raw:
        try:
            customer_org_id = int(customer_org_id_raw)
        except (TypeError, ValueError):
            customer_org_id = None

    if customer_org_id:
        initial_customer = {"org_id": customer_org_id}
        if _accounting_is_configured():
            try:
                from accounting_integration.models import Org, OrgAddress

                org = Org.objects.using("accounting").filter(org_id=customer_org_id).first()
                if org:
                    initial_customer.update(
                        {
                            "name": org.orgname or "",
                            "phone": org.phone1 or "",
                            "contact": org.contact1 or "",
                            "email": org.email or "",
                            "taxable": org.taxable,
                        }
                    )
                    address = (
                        OrgAddress.objects.using("accounting")
                        .filter(orgid=org, addresstype="BILLTO")
                        .order_by("-is_default", "-gen_addr_id")
                        .first()
                    )
                    if address:
                        initial_customer.update(
                            {
                                "address_line1": address.streetone or "",
                                "address_line2": address.streettwo or "",
                                "city": address.txtcity or "",
                                "state": address.txtstate or "",
                                "zip": address.txtzip or "",
                            }
                        )
            except Exception:
                pass
    from django.db.models import Max
    seq_number = WorkOrderNumberSequence.get_solo().next_number
    max_existing = WorkOrderV2.objects.aggregate(m=Max('number'))['m'] or 0
    next_wo_number = max(seq_number, max_existing + 1)

    return render(
        request,
        "rental_scheduler/workorders_v2/workorder_form.html",
        {
            "title": title,
            "job": job,
            "work_order": work_order,
            "sales_reps": sales_reps,
            "state_choices": US_STATE_TERRITORY_CHOICES,
            "initial": initial_data,
            "initial_customer": initial_customer,
            "errors": errors or {},
            "back_url": back_ctx["back_url"],
            "back_label": back_ctx["back_label"],
            "next_value": back_ctx["next_value"],
            "next_wo_number": next_wo_number,
        },
    )


def _wo_error_response(request, *, job, work_order, initial, errors):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        flat_errors = {}
        for k, v in errors.items():
            flat_errors[k] = v if isinstance(v, str) else str(v)
        return JsonResponse({"ok": False, "errors": flat_errors}, status=400)
    return _render_workorder_v2_form(
        request, job=job, work_order=work_order, initial=initial, errors=errors,
    )


@require_http_methods(["GET", "POST"])
@csrf_protect
def workorder_new(request):
    job_id = request.GET.get("job")
    if not job_id:
        return HttpResponse("Missing required query param: job", status=400)

    job = get_object_or_404(Job, pk=job_id)

    existing = WorkOrderV2.objects.filter(job=job).first()
    if existing:
        # Preserve 'next' param for back navigation
        next_url = request.GET.get("next") or ""
        edit_url = reverse("rental_scheduler:workorder_edit", args=[existing.pk])
        if next_url:
            from urllib.parse import urlencode

            edit_url = f"{edit_url}?{urlencode({'next': next_url})}"
        return redirect(edit_url)

    if request.method == "GET":
        initial = {
            "notes": job.repair_notes or "",
            "trailer_make_model": job.trailer_details or "",
            "trailer_color": job.trailer_color or "",
            "trailer_serial": job.trailer_serial or "",
            "discount_type": "amount",
            "discount_value": "0.00",
            "customer_org_id": "",
            "job_by_rep_id": "",
            "date": job.start_dt.date().isoformat() if job.start_dt else "",
        }
        return _render_workorder_v2_form(request, job=job, work_order=None, initial=initial)

    # POST: create work order + lines (transactional)
    errors: dict = {}
    try:
        lines = _parse_line_items_from_post(request)
    except forms.ValidationError as e:
        errors["lines"] = str(e)
        lines = []

    if not lines and "lines" not in errors:
        errors["lines"] = "At least one line item is required."

    notes = request.POST.get("notes", "")
    trailer_make_model = job.trailer_details or ""
    trailer_color = job.trailer_color or ""
    trailer_serial = job.trailer_serial or ""
    discount_type = request.POST.get("discount_type", "amount")
    discount_value_raw = request.POST.get("discount_value", "0.00")
    customer_org_id_raw = str(request.POST.get("customer_org_id", "")).strip()
    job_by_rep_id_raw = str(request.POST.get("job_by_rep_id", "")).strip()
    number_raw = str(request.POST.get("number", "")).strip()
    date_raw = request.POST.get("date", "").strip()

    wo_date = None
    if date_raw:
        from datetime import date as date_type
        try:
            wo_date = date_type.fromisoformat(date_raw)
        except (ValueError, TypeError):
            errors["date"] = "Invalid date format."
    else:
        errors["date"] = "Date is required."

    wo_number = None
    if number_raw:
        try:
            wo_number = int(number_raw)
            if wo_number < 1:
                errors["number"] = "Work order number must be a positive integer."
        except (TypeError, ValueError):
            errors["number"] = "Work order number must be a positive integer."

    customer_org_id = None
    if not customer_org_id_raw:
        errors["customer_org_id"] = "Customer is required."
    else:
        try:
            customer_org_id = int(customer_org_id_raw)
        except (TypeError, ValueError):
            errors["customer_org_id"] = "Customer ID must be an integer."

    job_by_rep_id = ""
    job_by_name = ""
    if job_by_rep_id_raw and _accounting_is_configured():
        try:
            from accounting_integration.models import AcctSalesRep
            rep = AcctSalesRep.objects.using("accounting").get(pk=job_by_rep_id_raw)
            job_by_rep_id = rep.id
            job_by_name = rep.rep_name or ""
        except AcctSalesRep.DoesNotExist:
            errors["job_by_rep_id"] = "Invalid sales rep."

    try:
        discount_value = _parse_decimal(discount_value_raw, field_name="discount")
    except forms.ValidationError as e:
        errors["discount_value"] = str(e)
        discount_value = Decimal("0.00")

    if lines and _accounting_is_configured():
        from accounting_integration.models import ItmItems
        requested_ids = {l["itemid"] for l in lines}
        try:
            found_ids = set(
                ItmItems.objects.using("accounting")
                .filter(itemid__in=requested_ids)
                .values_list("itemid", flat=True)
            )
        except Exception as e:
            errors["lines"] = f"Unable to validate Classic items: {e}"
            found_ids = requested_ids
        missing = requested_ids - found_ids
        if missing:
            errors["lines"] = f"Items not found in Classic Accounting: {missing}"

    if errors:
        return _wo_error_response(
            request, job=job, work_order=None,
            initial=request.POST.dict(), errors=errors,
        )

    tax_rate = _get_tax_rate_for_customer(customer_org_id)

    try:
        with transaction.atomic():
            from rental_scheduler.utils.work_orders import quantize_money

            create_kwargs = dict(
                job=job,
                customer_org_id=customer_org_id,
                job_by_rep_id=job_by_rep_id,
                job_by_name=job_by_name,
                date=wo_date,
                notes=notes,
                trailer_make_model=trailer_make_model,
                trailer_color=trailer_color,
                trailer_serial=trailer_serial,
                discount_type=discount_type,
                discount_value=discount_value,
                tax_rate_snapshot=tax_rate,
            )
            if wo_number:
                create_kwargs["number"] = wo_number

            wo = WorkOrderV2.objects.create(**create_kwargs)

            line_objects = [
                WorkOrderLineV2(
                    work_order=wo,
                    itemid=line["itemid"],
                    qty=line["qty"],
                    price=line["price"],
                    amount=quantize_money(line["qty"] * line["price"]),
                    itemnumber_snapshot=line["itemnumber_snapshot"],
                    description_snapshot=line["description_snapshot"],
                )
                for line in lines
            ]
            WorkOrderLineV2.objects.bulk_create(line_objects)

            wo.recalculate_totals(save=True)

            if _accounting_is_configured():
                try:
                    from accounting_integration.services.invoice import create_invoice_from_work_order
                    create_invoice_from_work_order(wo, strict=True)
                except Exception as e:
                    logger.error(f"Invoice creation failed for WO #{wo.number}: {e}", exc_info=True)
                    raise ValidationError(
                        f"Work order saved but invoice creation failed: {e}"
                    )
    except ValidationError as e:
        error_dict = e.message_dict if hasattr(e, "message_dict") else {"__all__": str(e)}
        return _wo_error_response(
            request, job=job, work_order=None,
            initial=request.POST.dict(), errors=error_dict,
        )

    msg = f"Work Order #{wo.number} created."
    after_save = request.POST.get("after_save", "").strip()
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    edit_url = reverse("rental_scheduler:workorder_edit", args=[wo.pk])
    if next_url:
        from urllib.parse import urlencode
        edit_url = f"{edit_url}?{urlencode({'next': next_url})}"
    if after_save == "print":
        edit_url += ("&" if "?" in edit_url else "?") + "auto_print=1"

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        redirect_url = ""
        if after_save == "back":
            back_ctx = _get_workorder_back_context(request, job_id=job.pk)
            redirect_url = back_ctx["back_url"]
        elif after_save == "print":
            redirect_url = edit_url
        return JsonResponse({
            "ok": True,
            "wo_number": wo.number,
            "wo_pk": wo.pk,
            "message": msg,
            "redirect_url": redirect_url,
            "after_save": after_save,
        })

    messages.success(request, msg)
    if after_save == "back":
        back_ctx = _get_workorder_back_context(request, job_id=job.pk)
        return redirect(back_ctx["back_url"])
    return redirect(edit_url)


@require_http_methods(["GET", "POST"])
@csrf_protect
def workorder_edit(request, pk: int):
    wo = get_object_or_404(WorkOrderV2.objects.select_related("job").prefetch_related("lines"), pk=pk)
    job = wo.job

    if request.method == "GET":
        initial = {
            "notes": wo.notes,
            "trailer_make_model": job.trailer_details or "",
            "trailer_color": job.trailer_color or "",
            "trailer_serial": job.trailer_serial or "",
            "discount_type": wo.discount_type,
            "discount_value": str(wo.discount_value),
            "customer_org_id": wo.customer_org_id or "",
            "job_by_rep_id": wo.job_by_rep_id or "",
            "date": wo.date.isoformat() if wo.date else "",
        }
        return _render_workorder_v2_form(request, job=job, work_order=wo, initial=initial)

    errors: dict = {}
    try:
        lines = _parse_line_items_from_post(request)
    except forms.ValidationError as e:
        errors["lines"] = str(e)
        lines = []

    if not lines and "lines" not in errors:
        errors["lines"] = "At least one line item is required."

    notes = request.POST.get("notes", "")
    trailer_make_model = job.trailer_details or ""
    trailer_color = job.trailer_color or ""
    trailer_serial = job.trailer_serial or ""
    discount_type = request.POST.get("discount_type", "amount")
    discount_value_raw = request.POST.get("discount_value", "0.00")
    customer_org_id_raw = str(request.POST.get("customer_org_id", "")).strip()
    job_by_rep_id_raw = str(request.POST.get("job_by_rep_id", "")).strip()
    number_raw = str(request.POST.get("number", "")).strip()
    date_raw = request.POST.get("date", "").strip()

    wo_date = None
    if date_raw:
        from datetime import date as date_type
        try:
            wo_date = date_type.fromisoformat(date_raw)
        except (ValueError, TypeError):
            errors["date"] = "Invalid date format."
    else:
        errors["date"] = "Date is required."

    wo_number = wo.number
    if number_raw:
        try:
            wo_number = int(number_raw)
            if wo_number < 1:
                errors["number"] = "Work order number must be a positive integer."
        except (TypeError, ValueError):
            errors["number"] = "Work order number must be a positive integer."

    customer_org_id = None
    if not customer_org_id_raw:
        errors["customer_org_id"] = "Customer is required."
    else:
        try:
            customer_org_id = int(customer_org_id_raw)
        except (TypeError, ValueError):
            errors["customer_org_id"] = "Customer ID must be an integer."

    job_by_rep_id = ""
    job_by_name = ""
    if job_by_rep_id_raw and _accounting_is_configured():
        try:
            from accounting_integration.models import AcctSalesRep
            rep = AcctSalesRep.objects.using("accounting").get(pk=job_by_rep_id_raw)
            job_by_rep_id = rep.id
            job_by_name = rep.rep_name or ""
        except AcctSalesRep.DoesNotExist:
            errors["job_by_rep_id"] = "Invalid sales rep."

    try:
        discount_value = _parse_decimal(discount_value_raw, field_name="discount")
    except forms.ValidationError as e:
        errors["discount_value"] = str(e)
        discount_value = Decimal("0.00")

    if lines and _accounting_is_configured():
        from accounting_integration.models import ItmItems
        requested_ids = {l["itemid"] for l in lines}
        try:
            found_ids = set(
                ItmItems.objects.using("accounting")
                .filter(itemid__in=requested_ids)
                .values_list("itemid", flat=True)
            )
        except Exception as e:
            errors["lines"] = f"Unable to validate Classic items: {e}"
            found_ids = requested_ids
        missing = requested_ids - found_ids
        if missing:
            errors["lines"] = f"Items not found in Classic Accounting: {missing}"

    if errors:
        return _wo_error_response(
            request, job=job, work_order=wo,
            initial=request.POST.dict(), errors=errors,
        )

    tax_rate = _get_tax_rate_for_customer(customer_org_id)

    try:
        with transaction.atomic():
            from rental_scheduler.utils.work_orders import quantize_money

            WorkOrderLineV2.objects.filter(work_order=wo).delete()

            wo.number = wo_number
            wo.customer_org_id = customer_org_id
            wo.job_by_rep_id = job_by_rep_id
            wo.job_by_name = job_by_name
            wo.date = wo_date
            wo.notes = notes
            wo.trailer_make_model = trailer_make_model
            wo.trailer_color = trailer_color
            wo.trailer_serial = trailer_serial
            wo.discount_type = discount_type
            wo.discount_value = discount_value
            wo.tax_rate_snapshot = tax_rate
            wo.save()

            line_objects = [
                WorkOrderLineV2(
                    work_order=wo,
                    itemid=line["itemid"],
                    qty=line["qty"],
                    price=line["price"],
                    amount=quantize_money(line["qty"] * line["price"]),
                    itemnumber_snapshot=line["itemnumber_snapshot"],
                    description_snapshot=line["description_snapshot"],
                )
                for line in lines
            ]
            WorkOrderLineV2.objects.bulk_create(line_objects)

            wo.recalculate_totals(save=True)

            if _accounting_is_configured():
                try:
                    from accounting_integration.services.invoice import (
                        create_invoice_from_work_order,
                        update_invoice_from_work_order,
                    )
                    if wo.accounting_invoice_id:
                        update_invoice_from_work_order(wo)
                    else:
                        create_invoice_from_work_order(wo, strict=True)
                except Exception as e:
                    logger.error(f"Invoice sync failed for WO #{wo.number}: {e}", exc_info=True)
                    raise ValidationError(
                        f"Work order saved but invoice sync failed: {e}"
                    )
    except ValidationError as e:
        wo.refresh_from_db()
        error_dict = e.message_dict if hasattr(e, "message_dict") else {"__all__": str(e)}
        return _wo_error_response(
            request, job=job, work_order=wo,
            initial=request.POST.dict(), errors=error_dict,
        )

    msg = f"Work Order #{wo.number} saved."
    after_save = request.POST.get("after_save", "").strip()
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    edit_url = reverse("rental_scheduler:workorder_edit", args=[wo.pk])
    if next_url:
        from urllib.parse import urlencode
        edit_url = f"{edit_url}?{urlencode({'next': next_url})}"
    if after_save == "print":
        edit_url += ("&" if "?" in edit_url else "?") + "auto_print=1"

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        redirect_url = ""
        if after_save == "back":
            back_ctx = _get_workorder_back_context(request, job_id=job.pk)
            redirect_url = back_ctx["back_url"]
        elif after_save == "print":
            redirect_url = edit_url
        return JsonResponse({
            "ok": True,
            "wo_number": wo.number,
            "wo_pk": wo.pk,
            "message": msg,
            "redirect_url": redirect_url,
            "after_save": after_save,
        })

    messages.success(request, msg)
    if after_save == "back":
        back_ctx = _get_workorder_back_context(request, job_id=job.pk)
        return redirect(back_ctx["back_url"])
    return redirect(edit_url)


@require_http_methods(["GET"])
def accounting_customers_search(request):
    if not _accounting_is_configured():
        return JsonResponse({"error": "Classic Accounting is not configured."}, status=503)

    q = (request.GET.get("q") or "").strip()

    from accounting_integration.models import Org

    qs = Org.objects.using("accounting").filter(orgdiscriminator="CUST")
    if q:
        qs = qs.filter(
            models.Q(orgname__icontains=q)
            | models.Q(phone1__icontains=q)
            | models.Q(contact1__icontains=q)
            | models.Q(email__icontains=q)
        )

    results = []
    for org in qs.order_by("orgname")[:20]:
        results.append(
            {
                "org_id": org.org_id,
                "name": org.orgname or "",
                "phone": org.phone1 or "",
                "contact": org.contact1 or "",
                "email": org.email or "",
                "taxable": org.taxable,
            }
        )

    return JsonResponse({"results": results})


@require_http_methods(["GET"])
def accounting_items_search(request):
    if not _accounting_is_configured():
        return JsonResponse({"error": "Classic Accounting is not configured."}, status=503)

    q = (request.GET.get("q") or "").strip()

    from accounting_integration.models import ItmItems

    qs = ItmItems.objects.using("accounting").all()
    if q:
        qs = qs.filter(models.Q(itemnumber__icontains=q) | models.Q(salesdesc__icontains=q))

    results = []
    for item in qs.order_by("itemnumber")[:20]:
        results.append(
            {
                "itemid": item.itemid,
                "itemnumber": item.itemnumber,
                "salesdesc": item.salesdesc,
                # Send price as string to preserve precision in JSON
                "price": str(item.price),
            }
        )

    return JsonResponse({"results": results})


@require_http_methods(["GET"])
def api_sales_reps(request):
    if not _accounting_is_configured():
        return JsonResponse({"error": "Classic Accounting is not configured."}, status=503)

    from accounting_integration.models import AcctSalesRep

    reps = AcctSalesRep.objects.using("accounting").filter(active=True).order_by("rep_name")
    results = [
        {"id": rep.id, "rep_name": rep.rep_name or "", "rep_initials": rep.rep_initials or ""}
        for rep in reps
    ]

    customer_default_rep_id = ""
    customer_org_id = (request.GET.get("customer_org_id") or "").strip()
    if customer_org_id:
        try:
            from accounting_integration.models import Org
            org = Org.objects.using("accounting").filter(org_id=int(customer_org_id)).first()
            if org and org.def_sales_rep_id_id:
                customer_default_rep_id = org.def_sales_rep_id_id
        except (ValueError, TypeError):
            pass

    return JsonResponse({"results": results, "customer_default_rep_id": customer_default_rep_id})


@require_http_methods(["GET"])
def work_order_customer_tax_rate(request):
    customer_org_id_raw = (request.GET.get("customer_org_id") or "").strip()
    if not customer_org_id_raw:
        return JsonResponse({"error": "customer_org_id is required."}, status=400)

    try:
        customer_org_id = int(customer_org_id_raw)
    except (TypeError, ValueError):
        return JsonResponse({"error": "customer_org_id must be an integer."}, status=400)

    if not _accounting_is_configured():
        return JsonResponse({"tax_rate": "0.00", "exempt": True})

    from accounting_integration.services.tax_applicability import get_effective_tax_rate

    try:
        rate, exempt = get_effective_tax_rate(customer_org_id)
    except Exception:
        return JsonResponse({"tax_rate": "0.00", "exempt": True})

    return JsonResponse({"tax_rate": str(rate), "exempt": exempt})


@require_http_methods(["POST"])
@csrf_protect
def work_order_compute_totals(request):
    from rental_scheduler.utils.work_orders import compute_work_order_totals

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    line_items = body.get("line_items") or []
    discount_type = body.get("discount_type", "amount")
    discount_value = body.get("discount_value", "0.00")
    tax_rate = body.get("tax_rate", "0.00")

    try:
        subtotal, discount_amount, tax_amount, total = compute_work_order_totals(
            line_items=line_items,
            discount_type=discount_type,
            discount_value=discount_value,
            tax_rate=tax_rate,
            clamp=True,
        )
    except Exception:
        return JsonResponse({"error": "Invalid input."}, status=400)

    return JsonResponse({
        "subtotal": str(subtotal),
        "discount_amount": str(discount_amount),
        "tax_amount": str(tax_amount),
        "total": str(total),
    })


def _normalize_state_code(value: str) -> str:
    """
    Normalize and validate US state/territory code.
    
    Args:
        value: Raw state input (2-letter code or full name)
    
    Returns:
        Normalized 2-letter USPS code (uppercase) or empty string
    
    Raises:
        ValidationError: If value is non-empty and not a valid state/territory
    """
    from rental_scheduler.constants import US_STATE_TERRITORY_CODE_SET, US_STATE_TERRITORY_NAME_TO_CODE
    
    normalized = (value or "").strip().upper()
    
    if not normalized:
        return ""
    
    # Already a valid 2-letter code
    if normalized in US_STATE_TERRITORY_CODE_SET:
        return normalized
    
    # Try mapping full name to code (defensive: allows "Tennessee" → "TN")
    if normalized in US_STATE_TERRITORY_NAME_TO_CODE:
        return US_STATE_TERRITORY_NAME_TO_CODE[normalized]
    
    # Invalid state
    from django.core.exceptions import ValidationError
    raise ValidationError(f"State must be a valid 2-letter USPS code (e.g., TN, KY). Received: {value[:20]}")


def _classic_customer_payload(data: dict) -> dict:
    """Normalize Classic customer payload from JSON/form data."""
    raw_state = (data.get("state") or data.get("txtstate") or "").strip()
    
    return {
        "name": (data.get("name") or data.get("orgname") or "").strip(),
        "phone": (data.get("phone") or data.get("phone1") or "").strip(),
        "contact": (data.get("contact") or data.get("contact1") or "").strip(),
        "email": (data.get("email") or "").strip(),
        "address_line1": (data.get("address_line1") or data.get("streetone") or "").strip(),
        "address_line2": (data.get("address_line2") or data.get("streettwo") or "").strip(),
        "city": (data.get("city") or data.get("txtcity") or "").strip(),
        "state": raw_state,  # Will be normalized/validated separately
        "zip": (data.get("zip") or data.get("txtzip") or "").strip(),
    }


def _create_unique_classic_orgname(name: str) -> str:
    """
    Classic uniqueness constraint: (orgdiscriminator, orgname, org_name_extension).

    We keep org_name_extension blank and add a numeric suffix to orgname when needed.
    """
    from accounting_integration.models import Org

    base = (name or "").strip()[:60]
    if not base:
        return ""

    candidate = base[:60]
    if not Org.objects.using("accounting").filter(
        orgdiscriminator="CUST",
        orgname=candidate,
        org_name_extension="",
    ).exists():
        return candidate

    suffix_num = 2
    while suffix_num < 1000:
        suffix = f" ({suffix_num})"
        max_base = 60 - len(suffix)
        candidate = base[:max_base] + suffix
        if not Org.objects.using("accounting").filter(
            orgdiscriminator="CUST",
            orgname=candidate,
            org_name_extension="",
        ).exists():
            return candidate
        suffix_num += 1

    return base[:50] + f" #{suffix_num}"[:10]


@require_http_methods(["POST"])
@csrf_protect
def accounting_customers_create(request):
    if not _accounting_is_configured():
        return JsonResponse({"error": "Classic Accounting is not configured."}, status=503)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}") if request.content_type == "application/json" else request.POST
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    payload = _classic_customer_payload(data)
    if not payload["name"]:
        return JsonResponse({"error": "Customer name is required."}, status=400)
    
    # Normalize and validate state
    try:
        payload["state"] = _normalize_state_code(payload["state"])
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    allow_duplicate_raw = data.get("allow_duplicate") if isinstance(data, dict) else None
    if allow_duplicate_raw is None and hasattr(data, "get"):
        allow_duplicate_raw = data.get("allow_duplicate")
    allow_duplicate = False
    if isinstance(allow_duplicate_raw, bool):
        allow_duplicate = allow_duplicate_raw
    elif allow_duplicate_raw is not None:
        allow_duplicate = str(allow_duplicate_raw).strip().lower() in {"1", "true", "yes", "on"}

    if not allow_duplicate:
        duplicates = _find_possible_customer_duplicates(payload)
        if duplicates:
            return JsonResponse(
                {
                    "error": "Possible duplicate customers found.",
                    "duplicates": duplicates,
                },
                status=409,
            )

    from accounting_integration.models import Org, OrgAddress

    with transaction.atomic(using="accounting"):
        now = timezone.now()

        org = Org(
            orgdiscriminator="CUST",
            orgname=_create_unique_classic_orgname(payload["name"]),
            org_name_extension="",
            active=True,
            autoactive=False,
            balance=Decimal("0.00"),
            createdate=now,
            phone1=payload["phone"][:45],
            contact1=payload["contact"][:45],
            email=payload["email"][:300],
            fax1="",
            is_cash_customer=False,
            taxable=True,
            is_no_charge_sales=False,
            notes=None,
            alertnotes=None,
            exported=None,
            fiscalmonth=None,
            taxmonth=None,
            logo=None,
            companyname="",
            creditlimit=Decimal("0.0000"),
            tax_exempt_expiration_date=None,
            tax_exempt_number="",
            eligible1099=False,
            taxidno=None,
            lastfcdate=None,
        )
        org.save(using="accounting")

        # Create BILLTO address
        OrgAddress.objects.using("accounting").create(
            addresstype="BILLTO",
            active=True,
            addrname=None,
            streetone=payload["address_line1"][:60],
            streettwo=payload["address_line2"][:60],
            txtcity=payload["city"][:60],
            txtstate=payload["state"][:25],
            txtzip=payload["zip"][:45],
            txtcountry=None,
            createdate=now,
            moddate=None,
            is_default=True,
            orgid=org,
        )

    return JsonResponse({"org_id": org.org_id})


@require_http_methods(["POST"])
@csrf_protect
def accounting_customers_update(request, orgid: int):
    if not _accounting_is_configured():
        return JsonResponse({"error": "Classic Accounting is not configured."}, status=503)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}") if request.content_type == "application/json" else request.POST
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    payload = _classic_customer_payload(data)
    if not payload["name"]:
        return JsonResponse({"error": "Customer name is required."}, status=400)
    
    # Normalize and validate state
    try:
        payload["state"] = _normalize_state_code(payload["state"])
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)

    from accounting_integration.models import Org, OrgAddress

    with transaction.atomic(using="accounting"):
        org = get_object_or_404(Org.objects.using("accounting"), org_id=orgid)

        # Name may need uniquing if changed
        desired_name = _create_unique_classic_orgname(payload["name"])
        org.orgname = desired_name
        org.phone1 = payload["phone"][:45]
        org.contact1 = payload["contact"][:45]
        org.email = payload["email"][:300]
        org.moddate = timezone.now()
        org.save(using="accounting")

        address = (
            OrgAddress.objects.using("accounting")
            .filter(orgid=org, addresstype="BILLTO")
            .order_by("-is_default", "-gen_addr_id")
            .first()
        )
        if address:
            address.streetone = payload["address_line1"][:60]
            address.streettwo = payload["address_line2"][:60]
            address.txtcity = payload["city"][:60]
            address.txtstate = payload["state"][:25]
            address.txtzip = payload["zip"][:45]
            address.moddate = timezone.now()
            address.save(using="accounting")
        else:
            OrgAddress.objects.using("accounting").create(
                addresstype="BILLTO",
                active=True,
                addrname=None,
                streetone=payload["address_line1"][:60],
                streettwo=payload["address_line2"][:60],
                txtcity=payload["city"][:60],
                txtstate=payload["state"][:25],
                txtzip=payload["zip"][:45],
                txtcountry=None,
                createdate=timezone.now(),
                moddate=None,
                is_default=True,
                orgid=org,
            )

    return JsonResponse({"org_id": org.org_id})


def _workorder_pdf_context(request, pk: int):
    wo = get_object_or_404(
        WorkOrderV2.objects.select_related("job").prefetch_related("lines"),
        pk=pk,
    )

    customer_name = ""
    customer_phone = ""
    customer_contact = ""
    customer_email = ""
    customer_address = ""
    customer_city = ""
    customer_state = ""
    customer_zip = ""

    if wo.customer_org_id and _accounting_is_configured():
        from accounting_integration.models import Org, OrgAddress

        org = Org.objects.using("accounting").filter(org_id=wo.customer_org_id).first()
        if org:
            customer_name = org.orgname or ""
            customer_phone = org.phone1 or ""
            customer_contact = org.contact1 or ""
            customer_email = org.email or ""

            addr = (
                OrgAddress.objects.using("accounting")
                .filter(orgid=org, addresstype="BILLTO")
                .order_by("-is_default", "-gen_addr_id")
                .first()
            )
            if addr:
                customer_address = addr.streetone or ""
                customer_city = addr.txtcity or ""
                customer_state = addr.txtstate or ""
                customer_zip = addr.txtzip or ""

    return {
        "work_order": wo,
        "lines": list(wo.lines.all()),
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "customer_contact": customer_contact,
        "customer_email": customer_email,
        "customer_address": customer_address,
        "customer_city": customer_city,
        "customer_state": customer_state,
        "customer_zip": customer_zip,
    }


def workorder_pdf(request, pk: int):
    from django.template.loader import render_to_string
    from django.utils.text import slugify
    from weasyprint import HTML

    context = _workorder_pdf_context(request, pk)
    html = render_to_string("rental_scheduler/workorders_v2/workorder_pdf.html", context)

    base_url = request.build_absolute_uri("/")
    pdf = HTML(string=html, base_url=base_url).write_pdf()

    wo = context["work_order"]
    filename = f"work-order-{slugify(str(wo.number))}.pdf"
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response


def workorder_pdf_preview(request, pk: int):
    from django.conf import settings
    from django.template.loader import render_to_string

    if not settings.DEBUG:
        raise Http404

    context = _workorder_pdf_context(request, pk)
    html = render_to_string("rental_scheduler/workorders_v2/workorder_pdf.html", context)
    return HttpResponse(html, content_type="text/html")

logger = logging.getLogger(__name__)

# HTML5 datetime-local format constant
DATETIME_LOCAL_FMT = "%Y-%m-%dT%H:%M"
# HTML5 date-only format (used when All Day is checked)
DATE_ONLY_FMT = "%Y-%m-%d"


def _tokenize_search_query(query: str) -> list[str]:
    """
    Extract alphanumeric tokens from a search query for punctuation-insensitive matching.
    
    - Splits on any non-alphanumeric character
    - Lowercases all tokens
    - Filters out single-letter tokens (too noisy)
    - For digit-only tokens, keeps only if length >= 3 (phone fragment)
    
    Example: "Mt. Hope" -> ["mt", "hope"]
             "Mt.Hope"  -> ["mt", "hope"]
             "MTHOPE"   -> ["mthope"]
    """
    # Split on non-alphanumeric characters
    raw_tokens = re.split(r'[^a-zA-Z0-9]+', query.lower())
    
    tokens = []
    for tok in raw_tokens:
        if not tok:
            continue
        # Filter out single-letter tokens
        if len(tok) == 1:
            continue
        # For digit-only tokens, require at least 3 digits
        if tok.isdigit() and len(tok) < 3:
            continue
        tokens.append(tok)
    
    return tokens


def _build_normalized_search_annotation():
    """
    Build a Django annotation that concatenates and normalizes searchable fields.
    
    Returns an expression that:
    - Concatenates all searchable text fields with a separator
    - Lowercases the result
    - Removes common punctuation and spaces for comparison
    
    This allows "Mt. Hope" to match "Mt.Hope" or "MTHOPE".
    """
    from django.db.models.functions import Coalesce, Concat, Lower, Replace
    
    # Helper to wrap field with Coalesce to handle nulls and cast to TextField
    def field_expr(field_name):
        return Coalesce(
            models.F(field_name),
            models.Value(''),
            output_field=models.TextField()
        )
    
    # Concatenate all searchable fields with a separator
    concat_expr = Concat(
        models.Value('|', output_field=models.TextField()),
        field_expr('business_name'),
        models.Value('|', output_field=models.TextField()),
        field_expr('contact_name'),
        models.Value('|', output_field=models.TextField()),
        field_expr('phone'),
        models.Value('|', output_field=models.TextField()),
        field_expr('address_line1'),
        models.Value('|', output_field=models.TextField()),
        field_expr('address_line2'),
        models.Value('|', output_field=models.TextField()),
        field_expr('city'),
        models.Value('|', output_field=models.TextField()),
        field_expr('state'),
        models.Value('|', output_field=models.TextField()),
        field_expr('trailer_color'),
        models.Value('|', output_field=models.TextField()),
        field_expr('trailer_serial'),
        models.Value('|', output_field=models.TextField()),
        field_expr('trailer_details'),
        models.Value('|', output_field=models.TextField()),
        field_expr('notes'),
        models.Value('|', output_field=models.TextField()),
        field_expr('repair_notes'),
        models.Value('|', output_field=models.TextField()),
        output_field=models.TextField(),
    )
    
    # Lowercase
    lower_expr = Lower(concat_expr, output_field=models.TextField())
    
    # Remove common punctuation and spaces for normalized comparison
    # Chain replacements: . , - ( ) ' " / \ space
    normalized = Replace(lower_expr, models.Value('.'), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value(','), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value('-'), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value('('), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value(')'), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value("'"), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value('"'), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value('/'), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value('\\'), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value(' '), models.Value(''), output_field=models.TextField())
    normalized = Replace(normalized, models.Value('+'), models.Value(''), output_field=models.TextField())
    
    return normalized



def _build_series_collapsed_rows(jobs, now, *, date_filter='all', include_match_counts=False):
    """
    Unified helper to collapse recurring series into header rows.
    
    Used for both search results (with match counts) and standard Jobs list.
    Returns interleaved row items that preserve the original sort order,
    with series headers appearing exactly where the first matching occurrence
    would have appeared (collapse-in-place).
    
    Args:
        jobs: List/queryset of Job objects (already sorted)
        now: Current datetime (for upcoming/past classification)
        date_filter: Date filter ('all', 'future', 'past', 'two_years', 'custom')
        include_match_counts: If True, compute match_count for each series (for search mode)
        
    Returns:
        dict with structure:
        {
            'upcoming': [...] or None,  # list of row dicts
            'past': [...] or None,      # list of row dicts  
            'has_recurring': bool,      # True if any series headers were created
        }
        
    Where each row dict is either:
        {'type': 'series', 'series': series_info} or
        {'type': 'job', 'job': job}
        
    And series_info contains:
        {
            'parent_id': int,
            'display_name': str,
            'phone': str,
            'calendar_name': str,
            'calendar_color': str,
            'recurrence_type': str,
            'is_forever': bool,
            'scope': 'upcoming' | 'past',
            'match_count': int (only if include_match_counts=True),
        }
    """
    from rental_scheduler.utils.recurrence import is_forever_series
    
    def get_parent_id(job):
        """Get the parent ID for a job (itself if parent, or its recurrence_parent)."""
        if job.recurrence_parent_id:
            return job.recurrence_parent_id
        elif job.recurrence_rule:
            return job.id
        return None
    
    def get_parent(job):
        """Get the parent job object."""
        if job.recurrence_parent_id:
            return job.recurrence_parent
        elif job.recurrence_rule:
            return job
        return None
    
    def determine_scope(job, date_filter):
        """
        Determine the scope for a job based on date filter and job timing.
        
        Forever parents included by future filters may have start_dt < now
        but should still appear under 'upcoming'.
        """
        # Use annotated is_past_event if available, else compute
        if hasattr(job, 'is_past_event'):
            job_is_past = bool(job.is_past_event)
        else:
            job_is_past = job.start_dt < now
        
        # For future-oriented filters, forever parents go to 'upcoming' even if start_dt is past
        if date_filter in ('future', 'two_years'):
            parent = get_parent(job)
            if parent and is_forever_series(parent):
                return 'upcoming'
        
        return 'past' if job_is_past else 'upcoming'
    
    # Convert to list if needed
    job_list = list(jobs) if hasattr(jobs, '__iter__') and not isinstance(jobs, list) else jobs
    
    # First pass: collect match counts if needed (for search mode)
    series_match_counts = {}
    if include_match_counts:
        for job in job_list:
            scope = determine_scope(job, date_filter)
            parent_id = get_parent_id(job)
            if parent_id:
                key = (parent_id, scope)
                series_match_counts[key] = series_match_counts.get(key, 0) + 1
    
    # Second pass: build rows, splitting into upcoming/past sections
    upcoming_rows = []
    past_rows = []
    seen_series = {}  # (parent_id, scope) -> True
    has_recurring = False
    
    for job in job_list:
        scope = determine_scope(job, date_filter)
        rows = past_rows if scope == 'past' else upcoming_rows
        
        parent_id = get_parent_id(job)
        parent = get_parent(job)
        
        if parent_id and parent:
            # Part of a recurring series
            series_key = (parent_id, scope)
            
            if series_key not in seen_series:
                # First occurrence - emit header
                seen_series[series_key] = True
                has_recurring = True
                
                series_info = {
                    'parent_id': parent_id,
                    'display_name': parent.display_name if hasattr(parent, 'display_name') else parent.business_name,
                    'phone': parent.get_phone() if hasattr(parent, 'get_phone') else (parent.phone or ''),
                    'calendar_name': parent.calendar.name if parent.calendar else '',
                    'calendar_color': parent.calendar.color if parent.calendar else '#6366F1',
                    'recurrence_type': (parent.recurrence_rule or {}).get('type', 'recurring'),
                    'is_forever': is_forever_series(parent) if parent.recurrence_rule else False,
                    'scope': scope,
                }
                
                if include_match_counts:
                    series_info['match_count'] = series_match_counts.get(series_key, 1)
                
                rows.append({'type': 'series', 'series': series_info})
            # else: skip (collapsed under header)
        else:
            # Non-recurring job - emit directly
            rows.append({'type': 'job', 'job': job})
    
    # For non-'all' filters, only one section will have data
    # Return None for empty sections to match expected behavior
    return {
        'upcoming': upcoming_rows if upcoming_rows else None,
        'past': past_rows if past_rows else None,
        'has_recurring': has_recurring,
    }


class HomeView(TemplateView):
    template_name = 'rental_scheduler/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'GTS Rental Scheduler'
        return context


class CalendarView(TemplateView):
    """Main calendar view for displaying jobs"""
    template_name = 'rental_scheduler/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Calendar'
        
        # Serialize calendars for JavaScript
        calendars = Calendar.objects.filter(is_active=True)
        context['calendars'] = [
            {'id': cal.id, 'name': cal.name, 'color': cal.color}
            for cal in calendars
        ]
        
        # Also add as JSON string for debugging
        context['calendars_json'] = json.dumps(context['calendars'])
        
        # Add guardrails for frontend date validation (single source of truth)
        from rental_scheduler.constants import get_guardrails_for_frontend
        context['guardrails_json'] = json.dumps(get_guardrails_for_frontend())
        
        # Add timestamp for cache busting
        import time
        context['timestamp'] = int(time.time())
        
        return context

# Calendar CRUD Views
class CalendarListView(ListView):
    """List all calendars with basic CRUD operations"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_list.html'
    context_object_name = 'calendars'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Calendars'
        return context

class CalendarCreateView(CreateView):
    """Create a new calendar"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_form.html'
    fields = ['name', 'color', 'call_reminder_color', 'is_active']
    success_url = reverse_lazy('rental_scheduler:calendar_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Calendar'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Calendar "{form.instance.name}" created successfully.')
        return super().form_valid(form)

class CalendarUpdateView(UpdateView):
    """Update an existing calendar"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_form.html'
    fields = ['name', 'color', 'call_reminder_color', 'is_active']
    success_url = reverse_lazy('rental_scheduler:calendar_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Calendar: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Calendar "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

class CalendarDeleteView(DeleteView):
    """Delete a calendar"""
    model = Calendar
    template_name = 'rental_scheduler/calendars/calendar_confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:calendar_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Calendar: {self.object.name}'
        return context
    
    def delete(self, request, *args, **kwargs):
        calendar = self.get_object()
        messages.success(request, f'Calendar "{calendar.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Job CRUD Views
class JobListView(ListView):
    """List all jobs with filtering, search, and sorting capabilities"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 25

    def get_queryset(self):
        """Filter and sort jobs based on query parameters"""
        queryset = Job.objects.select_related('calendar').filter(is_deleted=False)
        
        # Calendar filter
        calendars = self.request.GET.getlist('calendars')
        if calendars:
            queryset = queryset.filter(calendar_id__in=calendars)
        
        # Date filter
        # For future-looking filters, we also include "forever" recurring parents
        # whose start_dt may be in the past but have occurrences in the future
        date_filter = self.request.GET.get('date_filter', 'all')
        self._includes_forever_parents = False  # Track for template context
        
        # Build a filter for forever recurring parents (for OR-combining with date filters)
        # Forever parents: have recurrence_rule with end='never' or no count/until_date,
        # and no recurrence_parent (they are the parent themselves)
        forever_parent_filter = (
            models.Q(recurrence_parent__isnull=True) &
            models.Q(recurrence_rule__isnull=False) &
            (
                models.Q(recurrence_rule__end='never') |
                (
                    models.Q(recurrence_rule__count__isnull=True) &
                    models.Q(recurrence_rule__until_date__isnull=True)
                )
            )
        )
        
        if date_filter == 'custom':
            start_date = self.request.GET.get('start_date')
            end_date = self.request.GET.get('end_date')
            date_range_filter = models.Q()
            has_future_component = False
            
            if start_date:
                try:
                    start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
                    date_range_filter &= models.Q(start_dt__gte=start_date_obj)
                    if start_date_obj > timezone.now():
                        has_future_component = True
                except ValueError:
                    pass
            if end_date:
                try:
                    end_date_obj = timezone.datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.get_current_timezone())
                    date_range_filter &= models.Q(start_dt__lte=end_date_obj)
                except ValueError:
                    pass
            
            # If filtering for a future range, also include forever parents
            if has_future_component and date_range_filter:
                queryset = queryset.filter(date_range_filter | forever_parent_filter)
                self._includes_forever_parents = True
            elif date_range_filter:
                queryset = queryset.filter(date_range_filter)
                
        elif date_filter == 'future':
            now = timezone.now()
            # Include forever parents since they have future occurrences
            queryset = queryset.filter(
                models.Q(start_dt__gte=now) | forever_parent_filter
            )
            self._includes_forever_parents = True
        elif date_filter == 'past':
            now = timezone.now()
            queryset = queryset.filter(start_dt__lt=now)
        elif date_filter == 'two_years':
            now = timezone.now()
            two_years_from_now = now + timedelta(days=730)  # 2 years = 730 days
            # Include forever parents since they have occurrences in this range
            queryset = queryset.filter(
                (models.Q(start_dt__gte=now) & models.Q(start_dt__lte=two_years_from_now)) |
                forever_parent_filter
            )
            self._includes_forever_parents = True
        
        # Unified search across multiple fields with punctuation-insensitive matching
        # and smart fallback (strict AND first, then broaden to OR if no results)
        search = self.request.GET.get('search', '').strip()
        self._search_widened = False  # Track if we had to broaden the search
        
        if search:
            # Tokenize search query (punctuation-insensitive)
            tokens = _tokenize_search_query(search)
            
            if tokens:
                # Annotate with normalized search blob for punctuation-insensitive comparison
                queryset = queryset.annotate(
                    _search_blob=_build_normalized_search_annotation()
                )
                
                # Build strict AND filter (all tokens must be present)
                strict_filter = models.Q()
                for token in tokens:
                    strict_filter &= models.Q(_search_blob__icontains=token)
                
                # Try strict AND filter first
                strict_queryset = queryset.filter(strict_filter)
                
                # Check if strict filter returns any results
                if strict_queryset.exists():
                    queryset = strict_queryset
                elif len(tokens) > 1:
                    # Fall back to OR filter (any token matches)
                    broad_filter = models.Q()
                    for token in tokens:
                        broad_filter |= models.Q(_search_blob__icontains=token)
                    
                    queryset = queryset.filter(broad_filter)
                    self._search_widened = True
                else:
                    # Single token with no matches - keep the strict (empty) result
                    queryset = strict_queryset
        
        # Sorting
        allowed_sort_fields = {
            'start_dt': 'start_dt',
            'end_dt': 'end_dt',
            'business_name': 'business_name',
            'contact_name': 'contact_name',
            'status': 'status',
            'calendar__name': 'calendar__name',
            'repeat_type': 'repeat_type',
        }

        sort_by = (self.request.GET.get('sort') or '').strip()
        sort_direction = (self.request.GET.get('direction') or '').strip().lower()

        # If the user explicitly requested a sort, honor it.
        if sort_by and sort_by.lstrip('-') in allowed_sort_fields:
            sort_field = allowed_sort_fields[sort_by.lstrip('-')]

            effective_desc = sort_direction == 'desc' or sort_by.startswith('-')
            if effective_desc:
                sort_field = f'-{sort_field}'
                self._effective_direction = 'desc'
            else:
                self._effective_direction = 'asc'

            self._effective_sort = sort_by.lstrip('-')
            queryset = queryset.order_by(sort_field)
            return queryset

        # Default sorting when the user hasn't selected a column sort.
        # Keep the experience consistent between the jobs page and the calendar search panel (which pulls from /jobs/).
        if date_filter in {'future', 'two_years', 'custom'}:
            queryset = queryset.order_by('start_dt')
            self._effective_sort = 'start_dt'
            self._effective_direction = 'asc'
        elif date_filter == 'past':
            queryset = queryset.order_by('-start_dt')
            self._effective_sort = 'start_dt'
            self._effective_direction = 'desc'
        else:
            # "All Events": Upcoming first (soonest → latest), then Past (most recent → oldest)
            now = timezone.now()
            queryset = queryset.annotate(
                is_past_event=models.Case(
                    models.When(start_dt__lt=now, then=models.Value(1)),
                    default=models.Value(0),
                    output_field=models.IntegerField(),
                ),
                future_sort_key=models.Case(
                    models.When(start_dt__gte=now, then=models.F('start_dt')),
                    default=models.Value(None, output_field=models.DateTimeField()),
                    output_field=models.DateTimeField(),
                ),
                past_sort_key=models.Case(
                    models.When(start_dt__lt=now, then=models.F('start_dt')),
                    default=models.Value(None, output_field=models.DateTimeField()),
                    output_field=models.DateTimeField(),
                ),
            ).order_by('is_past_event', 'future_sort_key', '-past_sort_key')

            self._effective_sort = 'smart'
            self._effective_direction = ''

        return queryset
    
    def get_context_data(self, **kwargs):
        from django.utils import timezone
        from .models import Calendar
        
        context = super().get_context_data(**kwargs)
        context['title'] = 'Jobs'
        
        # Fix pagination context: make 'jobs' refer to the Page object (not just the list)
        # so templates can call .has_next, .has_other_pages, .start_index, etc.
        # Django ListView puts the page in 'page_obj' by default, but our templates expect 'jobs'.
        if 'page_obj' in context and context['page_obj'] is not None:
            context['jobs'] = context['page_obj']
        # If pagination is not active, 'jobs' will still be the queryset/list (fallback)
        
        # Add sorting context
        context['current_sort'] = getattr(self, '_effective_sort', self.request.GET.get('sort', 'start_dt'))
        context['current_direction'] = getattr(self, '_effective_direction', self.request.GET.get('direction', 'desc'))
        
        # Add search filter context for maintaining state
        context['search_query'] = self.request.GET.get('search', '')
        
        # Add calendar filter context
        context['calendars'] = Calendar.objects.all().order_by('name')
        
        # Get selected calendars
        selected_calendars = self.request.GET.getlist('calendars')
        context['selected_calendars'] = [int(cal_id) for cal_id in selected_calendars if cal_id.isdigit()]
        
        # Add date filter context
        context['date_filter'] = self.request.GET.get('date_filter', 'all')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        # Add search widened flag (True if fallback to OR matching was used)
        context['search_widened'] = getattr(self, '_search_widened', False)
        
        # Add flag indicating if forever recurring parents were included
        # (used to show appropriate badge/info in templates)
        context['includes_forever_parents'] = getattr(self, '_includes_forever_parents', False)
        
        # Collapse recurring series into header rows (unified for both search and standard mode)
        search_query = context['search_query']
        jobs = context.get('jobs')
        now = timezone.now()
        date_filter = context.get('date_filter', 'all')
        
        if jobs:
            job_list = list(jobs.object_list) if hasattr(jobs, 'object_list') else list(jobs)
            
            # Use unified helper for both modes
            # Search mode includes match counts, standard mode doesn't
            collapsed = _build_series_collapsed_rows(
                job_list,
                now,
                date_filter=date_filter,
                include_match_counts=bool(search_query),
            )
            
            # Unified context for templates
            context['job_sections'] = {
                'upcoming': collapsed['upcoming'],
                'past': collapsed['past'],
            }
            context['has_recurring'] = collapsed['has_recurring']
            context['is_series_collapsed'] = True  # Always use collapsed rendering
            
            # Legacy context keys for backwards compatibility (remove after templates are updated)
            context['is_grouped_search'] = bool(search_query)
            context['grouped_search'] = {
                'upcoming_rows': collapsed['upcoming'],
                'past_rows': collapsed['past'],
            }
            context['standard_sections'] = {
                'upcoming': collapsed['upcoming'],
                'past': collapsed['past'],
            }
        else:
            context['job_sections'] = {'upcoming': None, 'past': None}
            context['has_recurring'] = False
            context['is_series_collapsed'] = False
            context['is_grouped_search'] = False
            context['grouped_search'] = {'upcoming_rows': None, 'past_rows': None}
            context['standard_sections'] = {'upcoming': None, 'past': None}
        
        # For load-more links: determine if last job on current page is a past event
        # (needed for boundary-safe section header insertion)
        jobs = context.get('jobs')
        if jobs and hasattr(jobs, 'object_list') and len(jobs.object_list) > 0:
            if context['date_filter'] == 'all' and context['current_sort'] == 'smart':
                # Convert to list to support negative indexing (QuerySet doesn't support it)
                job_list = list(jobs.object_list)
                last_job = job_list[-1]
                if hasattr(last_job, 'is_past_event'):
                    context['last_job_is_past_event'] = bool(last_job.is_past_event)
                else:
                    # Fallback: check start_dt against now
                    context['last_job_is_past_event'] = last_job.start_dt < timezone.now()
            else:
                context['last_job_is_past_event'] = None
        else:
            context['last_job_is_past_event'] = None
        
        # Add pagination presenter context for footer display
        # Use append-only mode for consistent UX: user loads more to see more items
        self._add_pagination_presenter_context(context, is_append_mode=True)
        
        return context
    
    def _add_pagination_presenter_context(self, context, *, is_append_mode):
        """
        Add pagination display context for footer templates.
        
        Args:
            context: Template context dict
            is_append_mode: If True, use cumulative display (show 1 to N);
                          if False, use page-range display (show X to Y)
        """
        from django.utils import timezone as tz
        
        jobs = context.get('jobs')
        if not jobs or not hasattr(jobs, 'paginator'):
            return
        
        # Pagination display values
        # NOTE: Django Page's start_index, end_index, has_next, next_page_number are methods
        context['is_append_mode'] = is_append_mode
        # show_start: always 1 for append mode (cumulative), else current page start
        context['show_start'] = 1 if is_append_mode else jobs.start_index()
        context['show_end'] = jobs.end_index()
        context['show_total'] = jobs.paginator.count
        
        # Build canonical next-page querystring to avoid duplication in templates
        if jobs.has_next():
            params = self.request.GET.copy()
            params['page'] = jobs.next_page_number()
            # For chunk responses, track if last job is a past event (for boundary detection)
            if context.get('date_filter') == 'all' and context.get('current_sort') == 'smart':
                if hasattr(jobs, 'object_list') and len(jobs.object_list) > 0:
                    job_list = list(jobs.object_list)
                    last_job = job_list[-1]
                    if hasattr(last_job, 'is_past_event'):
                        params['prev_is_past_event'] = '1' if last_job.is_past_event else '0'
                    else:
                        params['prev_is_past_event'] = '1' if last_job.start_dt < tz.now() else '0'
            context['next_page_querystring'] = params.urlencode()
        else:
            context['next_page_querystring'] = ''


class JobListTablePartialView(JobListView):
    """
    Returns only the job list table fragment (no surrounding page layout).
    Used by the calendar search panel to avoid HTML scraping.
    
    For HTMX requests (HX-Request header), returns a chunk template that appends
    rows to the existing table body, plus out-of-band updates for pagination controls.
    """
    template_name = 'rental_scheduler/partials/job_list_table.html'

    def paginate_queryset(self, queryset, page_size):
        """
        Override pagination to handle out-of-range pages gracefully for HTMX requests.
        Returns empty page instead of raising Http404.
        """
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        from django.core.paginator import Page as DjangoPage
        
        paginator = Paginator(queryset, page_size)
        page_number = self.request.GET.get('page', 1)
        
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        
        # Handle empty queryset case for HTMX
        if is_htmx and paginator.count == 0:
            # Create an empty page manually
            empty_page = DjangoPage([], 1, paginator)
            return (paginator, empty_page, [], False)
        
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            page = paginator.page(1)
        except EmptyPage:
            if is_htmx:
                # For HTMX chunk requests, return last valid page with empty list
                # This allows the chunk template to render OOB updates safely
                if paginator.num_pages > 0:
                    page = paginator.page(paginator.num_pages)
                    # Override object_list to empty to avoid showing stale data
                    page.object_list = []
                else:
                    # Fallback: create empty page
                    page = DjangoPage([], 1, paginator)
            else:
                # For non-HTMX requests, maintain default behavior (raise 404)
                raise
        
        return (paginator, page, page.object_list, page.has_other_pages())

    def get_template_names(self):
        """Return chunk template for HTMX requests, full table template otherwise."""
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if is_htmx:
            return ['rental_scheduler/partials/job_list_table_chunk.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        from django.utils import timezone as tz
        
        context = super().get_context_data(**kwargs)
        # Remove 'calendars' from context - the table partial doesn't need the full calendar list
        context.pop('calendars', None)
        
        # For HTMX chunk responses, add boundary detection context
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        
        # NOTE: Parent already sets is_append_mode=True; no need to override here.
        
        if is_htmx:
            # Check if we need to insert a section header at the boundary
            # This happens when crossing from "upcoming" to "past" in smart sort mode
            prev_is_past_event = self.request.GET.get('prev_is_past_event')
            if prev_is_past_event is not None:
                context['prev_is_past_event'] = int(prev_is_past_event)
            
            # Determine if first row of this chunk is past event
            jobs = context.get('jobs')
            if jobs and hasattr(jobs, 'object_list') and len(jobs.object_list) > 0:
                if context.get('date_filter') == 'all' and context.get('current_sort') == 'smart':
                    # Convert to list to support indexing (QuerySet may not support it efficiently)
                    job_list = list(jobs.object_list)
                    first_job = job_list[0]
                    if hasattr(first_job, 'is_past_event'):
                        context['first_row_is_past'] = bool(first_job.is_past_event)
                    else:
                        # Fallback: check start_dt against now
                        context['first_row_is_past'] = first_job.start_dt < tz.now()
        
        return context


class JobDeleteView(DeleteView):
    """Delete a job"""
    model = Job
    template_name = 'rental_scheduler/jobs/job_confirm_delete.html'
    success_url = reverse_lazy('rental_scheduler:job_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Job: {self.object.get_display_name()}'
        return context
    
    def delete(self, request, *args, **kwargs):
        job = self.get_object()
        messages.success(request, f'Job for {job.get_display_name()} deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Calendar API Views
def lighten_color(hex_color, factor):
    """
    Lighten a hex color by a given factor (0-1).
    Factor of 0.3 means 30% lighter.
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Lighten by mixing with white
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"

def get_job_calendar_data(request):
    """API endpoint to get job data for calendar display"""
    import time as perf_time
    import hashlib
    from django.conf import settings
    from django.core.cache import cache
    from django.db import connection, reset_queries
    from rental_scheduler.constants import MAX_MULTI_DAY_EXPANSION_DAYS
    from rental_scheduler.models import CALENDAR_EVENTS_VERSION_KEY
    
    # Performance instrumentation (only in DEBUG mode)
    _perf_start = perf_time.perf_counter()
    _perf_db_start = None
    _perf_db_end = None
    _perf_serialize_start = None
    _perf_reminders_start = None
    _perf_reminders_end = None
    _perf_virtual_start = None
    _perf_virtual_end = None
    _event_count = 0
    _cache_hit = False
    _query_count_jobs = 0
    _query_count_reminders = 0
    _query_count_total = 0
    
    # Reset query log for accurate counting (DEBUG only)
    if settings.DEBUG:
        reset_queries()
    
    try:
        # Get date range from request
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        # Parse request window dates for clamping multi-day expansions
        request_start_date = None
        request_end_date = None
        if start_date:
            try:
                # Handle ISO format with timezone: "2025-01-01T00:00:00-05:00"
                if 'T' in start_date:
                    request_start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
                else:
                    request_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse start_date '{start_date}': {e}")
        if end_date:
            try:
                if 'T' in end_date:
                    request_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
                else:
                    request_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not parse end_date '{end_date}': {e}")
        
        # Get filter parameters
        status_filter = request.GET.get('status')
        calendar_filter = request.GET.get('calendar')
        search_filter = request.GET.get('search')
        
        # =====================================================================
        # Cache lookup - build key from normalized params + version
        # =====================================================================
        cache_ttl = getattr(settings, 'CALENDAR_EVENTS_CACHE_TTL', 30)
        cache_version = cache.get(CALENDAR_EVENTS_VERSION_KEY, 0)
        
        # Normalize dates for cache key (use date-only format to ignore timezone info in request)
        cache_start = request_start_date.isoformat() if request_start_date else ''
        cache_end = request_end_date.isoformat() if request_end_date else ''
        
        # Build deterministic cache key
        cache_key_raw = f"cal_events:v{cache_version}:{cache_start}:{cache_end}:{calendar_filter or ''}:{status_filter or ''}:{search_filter or ''}"
        cache_key = f"cal_events:{hashlib.md5(cache_key_raw.encode()).hexdigest()}"
        
        # Check cache (skip if fresh=1 is passed - used after mutations)
        if not request.GET.get('fresh'):
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                _cache_hit = True
                _perf_total = perf_time.perf_counter() - _perf_start
                
                # Use compact JSON (no extra whitespace)
                response = JsonResponse(cached_data, json_dumps_params={'separators': (',', ':')})
                
                if settings.DEBUG:
                    total_time_ms = _perf_total * 1000
                    response['Server-Timing'] = f'cache;desc="Cache Hit", total;dur={total_time_ms:.1f}'
                    response['X-Cache'] = 'HIT'
                    logger.info(f"[PERF] job_calendar_data: CACHE HIT, total={total_time_ms:.1f}ms")
                
                return response
        
        # =====================================================================
        # POSTGRES FAST PATH: Use calendar_feed() function for single-query performance
        # =====================================================================
        if connection.vendor == 'postgresql' and request_start_date and request_end_date:
            _perf_db_start = perf_time.perf_counter()
            
            try:
                # Parse calendar IDs for SQL array parameter
                pg_calendar_ids = None
                if calendar_filter:
                    if ',' in calendar_filter:
                        pg_calendar_ids = [int(cid.strip()) for cid in calendar_filter.split(',') if cid.strip().isdigit()]
                    else:
                        try:
                            pg_calendar_ids = [int(calendar_filter)]
                        except ValueError:
                            pass
                
                # Get timezone from Django settings
                from django.conf import settings as django_settings
                pg_timezone = getattr(django_settings, 'TIME_ZONE', 'America/New_York')
                
                # Call the calendar_feed function - returns complete JSONB payload
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT calendar_feed(
                            %s::date,           -- p_req_start
                            %s::date,           -- p_req_end
                            %s::int[],          -- p_calendar_ids (NULL = all)
                            %s,                 -- p_status (NULL = all)
                            %s,                 -- p_search (NULL = no filter)
                            %s,                 -- p_tz
                            %s                  -- p_max_expand_days
                        )
                        """,
                        [
                            request_start_date.isoformat(),
                            request_end_date.isoformat(),
                            pg_calendar_ids,
                            status_filter or None,
                            search_filter or None,
                            pg_timezone,
                            MAX_MULTI_DAY_EXPANSION_DAYS,
                        ]
                    )
                    result = cursor.fetchone()
                
                _perf_db_end = perf_time.perf_counter()
                
                # Parse the JSONB result
                import json as json_module
                events = json_module.loads(result[0]) if result and result[0] else []
                
                # Capture query count (should be 1 for the main call)
                if settings.DEBUG:
                    _query_count_jobs = 1
                    _query_count_total = 1
                
                # =========================================================
                # VIRTUAL OCCURRENCES: Still handled in Python for now
                # (Forever-recurring series need Python's recurrence logic)
                # =========================================================
                _perf_virtual_start = perf_time.perf_counter()
                
                try:
                    from rental_scheduler.utils.recurrence import is_forever_series, generate_occurrences_in_window
                    
                    # Build filter datetime for cheap parent exclusion
                    # (series starting after the window can't contribute)
                    filter_end_for_parent = timezone.make_aware(
                        datetime.combine(request_end_date + timedelta(days=1), datetime.min.time())
                    )
                    
                    # Find "forever" recurring parents
                    forever_parents_qs = Job.objects.select_related('calendar').filter(
                        is_deleted=False,
                        recurrence_parent__isnull=True,
                        recurrence_rule__isnull=False,
                        start_dt__lt=filter_end_for_parent,  # Parent must start before window ends
                    ).exclude(status='canceled')
                    
                    if pg_calendar_ids:
                        forever_parents_qs = forever_parents_qs.filter(calendar_id__in=pg_calendar_ids)
                    if status_filter:
                        forever_parents_qs = forever_parents_qs.filter(status=status_filter)
                    if search_filter:
                        forever_parents_qs = forever_parents_qs.filter(
                            models.Q(business_name__icontains=search_filter) |
                            models.Q(contact_name__icontains=search_filter) |
                            models.Q(phone__icontains=search_filter) |
                            models.Q(trailer_color__icontains=search_filter)
                        )
                    
                    for parent in forever_parents_qs:
                        if not is_forever_series(parent):
                            continue
                        
                        try:
                            materialized_starts = set(
                                Job.objects.filter(recurrence_parent=parent).values_list('recurrence_original_start', flat=True)
                            )
                            
                            occurrences = generate_occurrences_in_window(
                                parent, request_start_date, request_end_date, safety_cap=100
                            )
                        except Exception as parent_err:
                            logger.error(
                                f"Error generating virtual occurrences for parent job {parent.id} "
                                f"(window: {request_start_date} to {request_end_date}): {parent_err}"
                            )
                            continue
                        
                        for occ in occurrences:
                            if occ.get('is_parent') or occ['start_dt'] in materialized_starts:
                                continue
                            
                            occ_start = occ['start_dt']
                            occ_end = occ['end_dt']
                            phone_formatted = format_phone(parent.get_phone()) if parent.get_phone() else ""
                            
                            business_name = parent.business_name or ""
                            contact_name = parent.contact_name or ""
                            if business_name and contact_name:
                                title = f"{business_name} ({contact_name})"
                            elif business_name:
                                title = business_name
                            elif contact_name:
                                title = contact_name
                            else:
                                title = "No Name Provided"
                            if phone_formatted:
                                title += f" - {phone_formatted}"
                            
                            calendar_color = parent.calendar.color or '#3B82F6'
                            occ_start_local = timezone.localtime(occ_start)
                            occ_end_local = timezone.localtime(occ_end)
                            
                            if parent.all_day:
                                start_str = f"{occ_start_local.date().isoformat()}T12:00:00"
                                end_str = f"{(occ_end_local.date() + timedelta(days=1)).isoformat()}T12:00:00"
                            else:
                                start_str = occ_start_local.strftime('%Y-%m-%dT%H:%M:%S')
                                end_str = occ_end_local.strftime('%Y-%m-%dT%H:%M:%S')
                            
                            virtual_event = {
                                'id': f"virtual-job-{parent.id}-{occ_start.isoformat()}",
                                'title': title,
                                'start': start_str,
                                'end': end_str,
                                'allDay': parent.all_day,
                                'backgroundColor': calendar_color,
                                'borderColor': calendar_color,
                                'extendedProps': {
                                    'type': 'virtual_job',
                                    'recurrence_parent_id': parent.id,
                                    'recurrence_original_start': occ_start.isoformat(),
                                    'status': 'uncompleted',
                                    'calendar_id': parent.calendar.id,
                                    'calendar_name': parent.calendar.name,
                                    'display_name': parent.display_name,
                                    'phone': parent.get_phone(),
                                    'trailer_color': parent.trailer_color,
                                    'is_recurring_parent': False,
                                    'is_recurring_instance': True,
                                    'is_virtual': True,
                                }
                            }
                            events.append(virtual_event)
                            
                            # Virtual call reminder
                            if parent.has_call_reminder and parent.call_reminder_weeks_prior:
                                try:
                                    reminder_dt = get_call_reminder_sunday(occ_start, parent.call_reminder_weeks_prior)
                                    reminder_date = reminder_dt.date()
                                    if request_start_date <= reminder_date <= request_end_date:
                                        reminder_color = parent.calendar.call_reminder_color or '#F59E0B'
                                        events.append({
                                            'id': f"virtual-call-reminder-{parent.id}-{occ_start.isoformat()}",
                                            'title': f"📞 {title}",
                                            'start': f"{reminder_date.isoformat()}T12:00:00",
                                            'end': f"{(reminder_date + timedelta(days=1)).isoformat()}T12:00:00",
                                            'backgroundColor': reminder_color,
                                            'borderColor': reminder_color,
                                            'allDay': True,
                                            'extendedProps': {
                                                'type': 'virtual_call_reminder',
                                                'recurrence_parent_id': parent.id,
                                                'recurrence_original_start': occ_start.isoformat(),
                                                'status': 'uncompleted',
                                                'calendar_id': parent.calendar.id,
                                                'calendar_name': parent.calendar.name,
                                                'display_name': parent.display_name,
                                                'phone': parent.get_phone(),
                                                'weeks_prior': parent.call_reminder_weeks_prior,
                                                'job_date': occ_start_local.date().isoformat(),
                                                'is_virtual': True,
                                            }
                                        })
                                except Exception:
                                    pass
                except Exception as virtual_err:
                    logger.warning(f"Error generating virtual occurrences (Postgres path): {virtual_err}")
                
                _perf_virtual_end = perf_time.perf_counter()
                
                # Build response
                _event_count = len(events)
                _perf_total = perf_time.perf_counter() - _perf_start
                
                response_data = {'status': 'success', 'events': events}
                
                try:
                    cache.set(cache_key, response_data, timeout=cache_ttl)
                except Exception as cache_err:
                    logger.warning(f"Failed to cache calendar data: {cache_err}")
                
                response = JsonResponse(response_data, json_dumps_params={'separators': (',', ':')})
                
                if settings.DEBUG:
                    db_time_ms = (_perf_db_end - _perf_db_start) * 1000
                    virtual_time_ms = (_perf_virtual_end - _perf_virtual_start) * 1000
                    total_time_ms = _perf_total * 1000
                    response['Server-Timing'] = (
                        f'db;dur={db_time_ms:.1f};desc="Postgres calendar_feed", '
                        f'virtual;dur={virtual_time_ms:.1f};desc="Virtual Occurrences", '
                        f'total;dur={total_time_ms:.1f};desc="Total"'
                    )
                    response['X-Cache'] = 'MISS'
                    response['X-DB-Backend'] = 'postgresql'
                    logger.info(
                        f"[PERF] job_calendar_data (POSTGRES): events={_event_count}, "
                        f"db={db_time_ms:.1f}ms, virtual={virtual_time_ms:.1f}ms, total={total_time_ms:.1f}ms"
                    )
                
                return response
                
            except Exception as pg_err:
                # Log and fall through to ORM path
                logger.warning(f"Postgres calendar_feed failed, falling back to ORM: {pg_err}")
        
        # =====================================================================
        # SQLITE/ORM FALLBACK PATH
        # =====================================================================
        
        # Build queryset - optimized to select only necessary fields for calendar display
        # Use Subquery annotations instead of prefetch_related for call_reminders
        # This reduces query count from 2+ to 1 for the jobs fetch
        from django.db.models import OuterRef, Subquery, Exists
        from django.db.models.functions import Substr, Length
        from .models import CallReminder
        
        # Subquery to get the notes from the first linked call reminder
        call_reminder_notes_subquery = CallReminder.objects.filter(
            job_id=OuterRef('pk')
        ).order_by('id').values('notes')[:1]
        
        jobs = Job.objects.select_related('calendar').filter(is_deleted=False).annotate(
            # Annotate with call reminder notes (first 50 chars for preview)
            _call_reminder_notes=Subquery(call_reminder_notes_subquery),
            # Annotate with has_notes flag
            _call_reminder_has_notes=Exists(
                CallReminder.objects.filter(job_id=OuterRef('pk')).exclude(notes='').exclude(notes__isnull=True)
            ),
        ).only(
            'id', 'business_name', 'contact_name', 'phone', 'status',
            'start_dt', 'end_dt', 'all_day', 'trailer_color',
            'has_call_reminder', 'call_reminder_weeks_prior', 'call_reminder_completed',
            'recurrence_rule', 'recurrence_parent_id',
            'calendar__id', 'calendar__name', 'calendar__color', 'calendar__call_reminder_color'
        )
        
        # Apply date range filter using timezone-aware datetime bounds
        if request_start_date and request_end_date:
            # Build aware datetime bounds in project timezone
            # start of first day for end_dt comparison
            filter_start_dt = timezone.make_aware(
                datetime.combine(request_start_date, datetime.min.time())
            )
            # end of last day for start_dt comparison (use start of next day as exclusive bound)
            filter_end_dt = timezone.make_aware(
                datetime.combine(request_end_date + timedelta(days=1), datetime.min.time())
            )
            jobs = jobs.filter(
                start_dt__lt=filter_end_dt,
                end_dt__gte=filter_start_dt
            )
        
        # Apply status filter
        if status_filter:
            jobs = jobs.filter(status=status_filter)
        
        # Apply calendar filter (supports multiple calendar IDs as comma-separated string)
        if calendar_filter:
            # Check if it's a comma-separated list of IDs
            if ',' in calendar_filter:
                calendar_ids = [int(cid.strip()) for cid in calendar_filter.split(',') if cid.strip().isdigit()]
                if calendar_ids:
                    jobs = jobs.filter(calendar_id__in=calendar_ids)
            else:
                # Single calendar ID
                jobs = jobs.filter(calendar_id=calendar_filter)
        
        # Apply search filter
        if search_filter:
            jobs = jobs.filter(
                models.Q(business_name__icontains=search_filter) |
                models.Q(contact_name__icontains=search_filter) |
                models.Q(phone__icontains=search_filter) |
                models.Q(trailer_color__icontains=search_filter) |
                models.Q(trailer_serial__icontains=search_filter) |
                models.Q(trailer_details__icontains=search_filter) |
                models.Q(notes__icontains=search_filter) |
                models.Q(repair_notes__icontains=search_filter)
            )
        
        # Convert to calendar events
        events = []
        
        # Performance: measure DB query time (queryset is lazy, force evaluation here)
        _perf_db_start = perf_time.perf_counter()
        jobs_list = list(jobs)  # Force DB query execution
        _perf_db_end = perf_time.perf_counter()
        
        # Capture query count after jobs fetch (DEBUG only)
        if settings.DEBUG:
            _query_count_jobs = len(connection.queries)
        
        _perf_serialize_start = perf_time.perf_counter()
        
        for job in jobs_list:
            # Format phone number using shared formatter
            phone_formatted = format_phone(job.get_phone()) if job.get_phone() else ""
            
            # Build the event title in format: Business Name (Contact Name) - Phone Number
            business_name = job.business_name or ""
            contact_name = job.contact_name or ""
            
            if business_name and contact_name:
                title = f"{business_name} ({contact_name})"
            elif business_name:
                title = business_name
            elif contact_name:
                title = contact_name
            else:
                title = "No Name Provided"
            
            if phone_formatted:
                title += f" - {phone_formatted}"
            
            # Get calendar color and apply lighter shade for completed jobs
            calendar_color = job.calendar.color if job.calendar.color else '#3B82F6'
            if job.status == 'completed':
                # Create a lighter shade for completed events
                calendar_color = lighten_color(calendar_color, 0.3)
            
            # Calculate the date span of this job
            job_start_local = timezone.localtime(job.start_dt)
            job_end_local = timezone.localtime(job.end_dt)
            
            # Determine if this is a multi-day job
            job_start_date = job_start_local.date()
            job_end_date = job_end_local.date()
            is_multi_day = (job_end_date > job_start_date)
            
            # Compute recurring flags once (avoids repeated property access)
            job_is_recurring_parent = job.is_recurring_parent
            job_is_recurring_instance = job.is_recurring_instance
            
            if is_multi_day:
                # Break multi-day jobs into separate events for each day
                # CLAMP to request window to prevent runaway responses from bad data
                total_days = (job_end_date - job_start_date).days
                
                # Determine the visible portion of this job within the request window
                if request_start_date and request_end_date:
                    visible_start = max(job_start_date, request_start_date)
                    visible_end = min(job_end_date, request_end_date)
                else:
                    # No window specified, but still apply safety cap
                    visible_start = job_start_date
                    visible_end = job_end_date
                
                # Safety cap: never expand more than MAX_MULTI_DAY_EXPANSION_DAYS
                visible_span = (visible_end - visible_start).days
                if visible_span > MAX_MULTI_DAY_EXPANSION_DAYS:
                    logger.warning(
                        f"Job {job.id} visible span ({visible_span} days) exceeds max; "
                        f"capping to {MAX_MULTI_DAY_EXPANSION_DAYS} days"
                    )
                    visible_end = visible_start + timedelta(days=MAX_MULTI_DAY_EXPANSION_DAYS)
                
                # Skip if job is entirely outside the visible window
                if visible_start > visible_end:
                    continue
                
                current_date = visible_start
                day_number = (visible_start - job_start_date).days  # Track actual day number in the job
                
                while current_date <= visible_end:
                    # For all-day events, use date strings
                    # For timed events, use the actual times on first/last day, full day for middle days
                    if job.all_day:
                        # All-day event: use noon to avoid timezone shifting issues
                        day_start = current_date.strftime('%Y-%m-%dT12:00:00')
                        day_end = (current_date + timedelta(days=1)).strftime('%Y-%m-%dT12:00:00')  # Exclusive end
                        is_all_day = True
                    else:
                        # Timed event: first day starts at job time, last day ends at job time, middle days are full days
                        if current_date == job_start_date and current_date == job_end_date:
                            # Single day (shouldn't happen in multi-day branch, but handle it)
                            day_start = job_start_local.strftime('%Y-%m-%dT%H:%M:%S')
                            day_end = job_end_local.strftime('%Y-%m-%dT%H:%M:%S')
                            is_all_day = False
                        elif current_date == job_start_date:
                            # First day: start at job start time, end at midnight
                            day_start = job_start_local.strftime('%Y-%m-%dT%H:%M:%S')
                            day_end = (current_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
                            is_all_day = False
                        elif current_date == job_end_date:
                            # Last day: start at midnight, end at job end time
                            day_start = current_date.strftime('%Y-%m-%dT00:00:00')
                            day_end = job_end_local.strftime('%Y-%m-%dT%H:%M:%S')
                            is_all_day = False
                        else:
                            # Middle day: full day from midnight to midnight
                            day_start = current_date.strftime('%Y-%m-%dT00:00:00')
                            day_end = (current_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
                            is_all_day = False
                    
                    # Create event for this day - LEAN payload (details fetched on click)
                    day_event = {
                        'id': f"job-{job.id}-day-{day_number}",
                        'title': title,
                        'start': day_start,
                        'end': day_end,
                        'allDay': is_all_day,
                        'backgroundColor': calendar_color,
                        'borderColor': calendar_color,
                        'extendedProps': {
                            'type': 'job',
                            'job_id': job.id,
                            'status': job.status,
                            'calendar_id': job.calendar.id,
                            'calendar_name': job.calendar.name,
                            # Minimal info for tooltip/display
                            'display_name': job.display_name,
                            'phone': job.get_phone(),
                            'trailer_color': job.trailer_color,
                            # Recurring flags only (not full rule object)
                            'is_recurring_parent': job_is_recurring_parent,
                            'is_recurring_instance': job_is_recurring_instance,
                            # Multi-day tracking
                            'is_multi_day': True,
                            'multi_day_number': day_number,
                            'multi_day_total': total_days,
                            # Store full job date range for display
                            'job_start_date': job_start_date.isoformat(),
                            'job_end_date': job_end_date.isoformat(),
                        }
                    }
                    
                    events.append(day_event)
                    current_date += timedelta(days=1)
                    day_number += 1
            else:
                # Single-day job: use the original approach - LEAN payload (details fetched on click)
                event = event_to_calendar_json(
                    job,
                    title=title,
                    backgroundColor=calendar_color,
                    borderColor=calendar_color,
                    extendedProps={
                        'type': 'job',
                        'job_id': job.id,
                        'status': job.status,
                        'calendar_id': job.calendar.id,
                        'calendar_name': job.calendar.name,
                        # Minimal info for tooltip/display
                        'display_name': job.display_name,
                        'phone': job.get_phone(),
                        'trailer_color': job.trailer_color,
                        # Recurring flags only (not full rule object)
                        'is_recurring_parent': job_is_recurring_parent,
                        'is_recurring_instance': job_is_recurring_instance,
                        # Multi-day tracking
                        'is_multi_day': False,
                    }
                )
                
                # Override the id to use the "job-{id}" format
                event['id'] = f"job-{job.id}"
                
                events.append(event)
            
            # Create call reminder event if enabled and not completed
            if job.has_call_reminder and job.call_reminder_weeks_prior and not job.call_reminder_completed:
                try:
                    reminder_dt = get_call_reminder_sunday(job.start_dt, job.call_reminder_weeks_prior)
                    reminder_end_dt = reminder_dt + timedelta(days=1)  # All-day event (exclusive end)
                    
                    # Get the call reminder color from the calendar
                    reminder_color = job.calendar.call_reminder_color or '#F59E0B'
                    
                    # Format the reminder title
                    reminder_title = f"📞 {title}"
                    
                    # Get the CallReminder notes preview from annotated data (avoids N+1 query)
                    # Full notes are fetched on demand via detail API
                    notes_preview = ''
                    has_notes = getattr(job, '_call_reminder_has_notes', False)
                    if has_notes:
                        full_notes = getattr(job, '_call_reminder_notes', '') or ''
                        if full_notes:
                            # Truncate for preview (same 50-char limit as title)
                            notes_preview = full_notes[:50] + '...' if len(full_notes) > 50 else full_notes
                    
                    reminder_event = {
                        'id': f"reminder-{job.id}",
                        'title': reminder_title,
                        'start': f"{reminder_dt.date().isoformat()}T12:00:00",
                        'end': f"{reminder_end_dt.date().isoformat()}T12:00:00",  # Exclusive end
                        'backgroundColor': reminder_color,
                        'borderColor': reminder_color,
                        'allDay': True,
                        'extendedProps': {
                            'type': 'call_reminder',
                            'job_id': job.id,
                            'status': job.status,
                            'calendar_id': job.calendar.id,
                            'calendar_name': job.calendar.name,
                            'business_name': job.business_name,
                            'contact_name': job.contact_name,
                            'phone': job.get_phone(),
                            'weeks_prior': job.call_reminder_weeks_prior,
                            'job_date': timezone.localtime(job.start_dt).date().isoformat(),
                            'call_reminder_completed': job.call_reminder_completed,
                            'notes_preview': notes_preview,  # Trimmed for feed; full via detail API
                            'has_notes': has_notes,
                        }
                    }
                    
                    events.append(reminder_event)
                except Exception as reminder_error:
                    logger.error(f"Error creating call reminder for job {job.id}: {str(reminder_error)}")
        
        # Fetch standalone CallReminder records (not linked to jobs)
        # Only query if we have valid date bounds (reuse already-parsed dates from top of function)
        _perf_reminders_start = perf_time.perf_counter()
        if request_start_date and request_end_date:
            try:
                from .models import CallReminder
                
                # Parse calendar_ids for filter (reuse logic)
                reminder_calendar_ids = []
                if calendar_filter:
                    if ',' in calendar_filter:
                        reminder_calendar_ids = [int(cid.strip()) for cid in calendar_filter.split(',') if cid.strip().isdigit()]
                    else:
                        try:
                            reminder_calendar_ids = [int(calendar_filter)]
                        except ValueError:
                            pass
                
                # Build optimized query with .only() for minimal payload
                reminder_base_qs = CallReminder.objects.filter(
                    reminder_date__range=[request_start_date, request_end_date],
                    job__isnull=True,  # Only standalone reminders
                ).select_related('calendar').only(
                    'id', 'reminder_date', 'notes', 'completed',
                    'calendar__id', 'calendar__name', 'calendar__call_reminder_color', 'calendar__is_active'
                )
                
                if reminder_calendar_ids:
                    call_reminders = reminder_base_qs.filter(calendar_id__in=reminder_calendar_ids)
                else:
                    # No filter, get all active calendars
                    call_reminders = reminder_base_qs.filter(calendar__is_active=True)
                
                # Add standalone call reminders to events (read-only, no DB writes)
                for reminder in call_reminders:
                    try:
                        # Normalize reminder_date to date object in-memory only (no DB writes)
                        reminder_date = reminder.reminder_date
                        
                        # Handle datetime objects (defensive - shouldn't happen with DateField)
                        if isinstance(reminder_date, datetime):
                            reminder_date = reminder_date.date()
                        # Handle string objects (defensive - shouldn't happen with DateField)
                        elif isinstance(reminder_date, str):
                            reminder_date = datetime.strptime(reminder_date[:10], '%Y-%m-%d').date()
                        
                        reminder_color = reminder.calendar.call_reminder_color or '#F59E0B'
                        
                        # Apply lighter shade for completed reminders
                        if reminder.completed:
                            reminder_color = lighten_color(reminder_color, 0.3)
                        
                        reminder_end_dt = reminder_date + timedelta(days=1)
                        
                        # Build title with notes if available
                        reminder_title = "📞 Call Reminder"
                        if reminder.notes:
                            # Truncate notes if too long for display
                            notes_preview = reminder.notes[:50] + '...' if len(reminder.notes) > 50 else reminder.notes
                            reminder_title = f"📞 {notes_preview}"
                        
                        # Add completion indicator to title for completed reminders
                        if reminder.completed:
                            reminder_title = f"✓ {reminder_title}"
                        
                        # Use notes_preview in feed, full notes fetched on demand
                        has_notes = bool(reminder.notes)
                        standalone_notes_preview = notes_preview if reminder.notes else ''  # Reuse notes_preview from title
                        
                        reminder_event = {
                            'id': f"call-reminder-{reminder.id}",
                            'title': reminder_title,
                            'start': f"{reminder_date.isoformat()}T12:00:00",
                            'end': f"{reminder_end_dt.isoformat()}T12:00:00",  # Exclusive end for all-day event
                            'backgroundColor': reminder_color,
                            'borderColor': reminder_color,
                            'allDay': True,
                            'extendedProps': {
                                'type': 'standalone_call_reminder',
                                'reminder_id': reminder.id,
                                'calendar_id': reminder.calendar.id,
                                'calendar_name': reminder.calendar.name,
                                'notes_preview': standalone_notes_preview,  # Trimmed for feed
                                'has_notes': has_notes,
                                'completed': reminder.completed,
                                'reminder_date': reminder_date.isoformat(),
                            }
                        }
                        
                        events.append(reminder_event)
                    except Exception as single_reminder_error:
                        logger.error(f"Error processing call reminder {reminder.id}: {str(single_reminder_error)}")
                        # Skip this reminder and continue with others
            except Exception as reminder_fetch_error:
                logger.error(f"Error fetching standalone call reminders: {str(reminder_fetch_error)}")
                # Continue without standalone reminders if there's an error
        
        _perf_reminders_end = perf_time.perf_counter()
        
        # Capture query count after reminders fetch (DEBUG only)
        if settings.DEBUG:
            _query_count_total = len(connection.queries)
            _query_count_reminders = _query_count_total - _query_count_jobs
        
        # =====================================================================
        # VIRTUAL OCCURRENCES: Generate on-the-fly for "forever" recurring series
        # =====================================================================
        _perf_virtual_start = perf_time.perf_counter()
        
        if request_start_date and request_end_date:
            try:
                from rental_scheduler.utils.recurrence import is_forever_series, generate_occurrences_in_window
                
                # Build calendar filter for recurring parents
                virtual_calendar_ids = None
                if calendar_filter:
                    if ',' in calendar_filter:
                        virtual_calendar_ids = [int(cid.strip()) for cid in calendar_filter.split(',') if cid.strip().isdigit()]
                    else:
                        try:
                            virtual_calendar_ids = [int(calendar_filter)]
                        except ValueError:
                            pass
                
                # Build filter datetime for cheap parent exclusion
                # (series starting after the window can't contribute)
                filter_end_for_parent = timezone.make_aware(
                    datetime.combine(request_end_date + timedelta(days=1), datetime.min.time())
                )
                
                # Find "forever" recurring parents that could have occurrences in the window
                # A forever series has recurrence_rule with end='never' or no count/until_date
                forever_parents_qs = Job.objects.select_related('calendar').filter(
                    is_deleted=False,
                    recurrence_parent__isnull=True,  # Only parents
                    recurrence_rule__isnull=False,   # Has a recurrence rule
                    start_dt__lt=filter_end_for_parent,  # Parent must start before window ends
                ).exclude(
                    status='canceled'
                )
                
                if virtual_calendar_ids:
                    forever_parents_qs = forever_parents_qs.filter(calendar_id__in=virtual_calendar_ids)
                
                # Apply status filter if provided
                if status_filter:
                    forever_parents_qs = forever_parents_qs.filter(status=status_filter)
                
                # Apply search filter if provided
                if search_filter:
                    forever_parents_qs = forever_parents_qs.filter(
                        models.Q(business_name__icontains=search_filter) |
                        models.Q(contact_name__icontains=search_filter) |
                        models.Q(phone__icontains=search_filter) |
                        models.Q(trailer_color__icontains=search_filter)
                    )
                
                for parent in forever_parents_qs:
                    # Skip if not a forever series
                    if not is_forever_series(parent):
                        continue
                    
                    try:
                        # Get already-materialized instance starts for this parent (including soft-deleted)
                        materialized_starts = set(
                            Job.objects.filter(
                                recurrence_parent=parent
                            ).values_list('recurrence_original_start', flat=True)
                        )
                        
                        # Generate virtual occurrences in the window
                        occurrences = generate_occurrences_in_window(
                            parent,
                            request_start_date,
                            request_end_date,
                            safety_cap=100  # Limit per parent per request
                        )
                    except Exception as parent_err:
                        logger.error(
                            f"Error generating virtual occurrences for parent job {parent.id} "
                            f"(window: {request_start_date} to {request_end_date}): {parent_err}"
                        )
                        continue
                    
                    for occ in occurrences:
                        # Skip parent occurrence (already in real jobs query) and materialized ones
                        if occ.get('is_parent'):
                            continue
                        if occ['start_dt'] in materialized_starts:
                            continue
                        
                        # Build virtual job event
                        occ_start = occ['start_dt']
                        occ_end = occ['end_dt']
                        
                        # Format phone number
                        phone_formatted = format_phone(parent.get_phone()) if parent.get_phone() else ""
                        
                        # Build title
                        business_name = parent.business_name or ""
                        contact_name = parent.contact_name or ""
                        if business_name and contact_name:
                            title = f"{business_name} ({contact_name})"
                        elif business_name:
                            title = business_name
                        elif contact_name:
                            title = contact_name
                        else:
                            title = "No Name Provided"
                        if phone_formatted:
                            title += f" - {phone_formatted}"
                        
                        # Get calendar color
                        calendar_color = parent.calendar.color if parent.calendar.color else '#3B82F6'
                        
                        # Format dates
                        occ_start_local = timezone.localtime(occ_start)
                        occ_end_local = timezone.localtime(occ_end)
                        
                        if parent.all_day:
                            start_str = f"{occ_start_local.date().isoformat()}T12:00:00"
                            end_str = f"{(occ_end_local.date() + timedelta(days=1)).isoformat()}T12:00:00"
                        else:
                            start_str = occ_start_local.strftime('%Y-%m-%dT%H:%M:%S')
                            end_str = occ_end_local.strftime('%Y-%m-%dT%H:%M:%S')
                        
                        virtual_event = {
                            'id': f"virtual-job-{parent.id}-{occ_start.isoformat()}",
                            'title': title,
                            'start': start_str,
                            'end': end_str,
                            'allDay': parent.all_day,
                            'backgroundColor': calendar_color,
                            'borderColor': calendar_color,
                            'extendedProps': {
                                'type': 'virtual_job',
                                'recurrence_parent_id': parent.id,
                                'recurrence_original_start': occ_start.isoformat(),
                                'status': 'uncompleted',  # Virtual occurrences are always uncompleted
                                'calendar_id': parent.calendar.id,
                                'calendar_name': parent.calendar.name,
                                'display_name': parent.display_name,
                                'phone': parent.get_phone(),
                                'trailer_color': parent.trailer_color,
                                'is_recurring_parent': False,
                                'is_recurring_instance': True,  # Will be when materialized
                                'is_virtual': True,
                            }
                        }
                        events.append(virtual_event)
                        
                        # Also emit virtual call reminder if parent has call reminder enabled
                        if parent.has_call_reminder and parent.call_reminder_weeks_prior:
                            try:
                                reminder_dt = get_call_reminder_sunday(occ_start, parent.call_reminder_weeks_prior)
                                reminder_date = reminder_dt.date()
                                
                                # Only include if reminder date is in the window
                                if request_start_date <= reminder_date <= request_end_date:
                                    reminder_color = parent.calendar.call_reminder_color or '#F59E0B'
                                    reminder_title = f"📞 {title}"
                                    reminder_end_dt = reminder_date + timedelta(days=1)
                                    
                                    virtual_reminder_event = {
                                        'id': f"virtual-call-reminder-{parent.id}-{occ_start.isoformat()}",
                                        'title': reminder_title,
                                        'start': f"{reminder_date.isoformat()}T12:00:00",
                                        'end': f"{reminder_end_dt.isoformat()}T12:00:00",
                                        'backgroundColor': reminder_color,
                                        'borderColor': reminder_color,
                                        'allDay': True,
                                        'extendedProps': {
                                            'type': 'virtual_call_reminder',
                                            'recurrence_parent_id': parent.id,
                                            'recurrence_original_start': occ_start.isoformat(),
                                            'status': 'uncompleted',
                                            'calendar_id': parent.calendar.id,
                                            'calendar_name': parent.calendar.name,
                                            'display_name': parent.display_name,
                                            'phone': parent.get_phone(),
                                            'weeks_prior': parent.call_reminder_weeks_prior,
                                            'job_date': occ_start_local.date().isoformat(),
                                            'is_virtual': True,
                                        }
                                    }
                                    events.append(virtual_reminder_event)
                            except Exception as vr_err:
                                logger.warning(f"Error creating virtual call reminder: {vr_err}")
                
            except Exception as virtual_err:
                logger.error(f"Error generating virtual occurrences: {virtual_err}")
                # Continue without virtual events if there's an error
        
        _perf_virtual_end = perf_time.perf_counter()
        
        # Build response with performance metrics
        _event_count = len(events)
        _perf_serialize_end = perf_time.perf_counter()
        _perf_total = perf_time.perf_counter() - _perf_start
        
        response_data = {
            'status': 'success',
            'events': events
        }
        
        # Store in cache for future requests
        try:
            cache.set(cache_key, response_data, timeout=cache_ttl)
        except Exception as cache_err:
            logger.warning(f"Failed to cache calendar data: {cache_err}")
        
        # Use compact JSON (no extra whitespace) for smaller payload
        response = JsonResponse(response_data, json_dumps_params={'separators': (',', ':')})
        
        # Add Server-Timing header for DevTools visibility (DEBUG only)
        if settings.DEBUG:
            db_time_ms = (_perf_db_end - _perf_db_start) * 1000 if _perf_db_start and _perf_db_end else 0
            reminders_time_ms = (_perf_reminders_end - _perf_reminders_start) * 1000 if _perf_reminders_start and _perf_reminders_end else 0
            virtual_time_ms = (_perf_virtual_end - _perf_virtual_start) * 1000 if _perf_virtual_start and _perf_virtual_end else 0
            serialize_time_ms = (_perf_serialize_end - _perf_serialize_start) * 1000 if _perf_serialize_start else 0
            total_time_ms = _perf_total * 1000
            
            response['Server-Timing'] = (
                f'db;dur={db_time_ms:.1f};desc="Jobs DB", '
                f'reminders;dur={reminders_time_ms:.1f};desc="Reminders DB", '
                f'virtual;dur={virtual_time_ms:.1f};desc="Virtual Occurrences", '
                f'serialize;dur={serialize_time_ms:.1f};desc="Serialization", '
                f'total;dur={total_time_ms:.1f};desc="Total"'
            )
            response['X-Cache'] = 'MISS'
            
            # Log performance metrics with query counts
            logger.info(
                f"[PERF] job_calendar_data: CACHE MISS, events={_event_count}, "
                f"queries={_query_count_total} (jobs={_query_count_jobs}, reminders={_query_count_reminders}), "
                f"db={db_time_ms:.1f}ms, reminders={reminders_time_ms:.1f}ms, serialize={serialize_time_ms:.1f}ms, total={total_time_ms:.1f}ms"
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting calendar data: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500, json_dumps_params={'separators': (',', ':')})


@require_http_methods(["POST"])
@csrf_protect
def update_job_status(request, job_id):
    """API endpoint to update job status with CSRF protection"""
    try:
        job = get_object_or_404(Job, id=job_id)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in dict(Job.STATUS_CHOICES):
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        old_status = job.status
        job.status = new_status
        job.save()
        
        return JsonResponse({
            'success': True,
            'old_status': old_status,
            'new_status': new_status,
            'is_canceled': False,  # No canceled status in simplified system
        })
        
    except Exception as e:
        logger.error(f"Error updating job status: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def mark_call_reminder_complete(request, job_id):
    """API endpoint to mark a call reminder as complete"""
    try:
        job = get_object_or_404(Job, id=job_id)
        job.call_reminder_completed = True
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder marked as complete'
        })
        
    except Exception as e:
        logger.error(f"Error marking call reminder complete: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def call_reminder_create_partial(request):
    """Return call reminder creation form partial for panel"""
    from .forms import CallReminderForm
    from datetime import datetime
    
    # Get date from query params and pre-fill form
    date_str = request.GET.get('date')
    calendar_id = request.GET.get('calendar')
    
    initial = {}
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            initial['reminder_date'] = date_obj
        except ValueError:
            pass
    
    if calendar_id:
        try:
            initial['calendar'] = int(calendar_id)
        except (ValueError, TypeError):
            pass
    
    # Fallback: if no calendar was set, select the first active calendar as default
    if 'calendar' not in initial:
        default_calendar = Calendar.objects.filter(is_active=True).first()
        if default_calendar:
            initial['calendar'] = default_calendar.id
    
    form = CallReminderForm(initial=initial)
    
    return render(request, 'rental_scheduler/call_reminders/_call_reminder_form_partial.html', {
        'form': form,
        'title': 'New Call Reminder'
    })


@require_http_methods(["POST"])
@csrf_protect
def call_reminder_create_submit(request):
    """Handle call reminder creation form submission"""
    from .forms import CallReminderForm
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("="*80)
    logger.info(f"Call reminder create request received")
    logger.info(f"POST data: {dict(request.POST)}")
    logger.info("="*80)
    
    form = CallReminderForm(request.POST)
    
    if form.is_valid():
        try:
            reminder = form.save()
            logger.info(f"Call reminder created successfully: ID={reminder.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Call reminder created successfully',
                'reminder_id': reminder.id
            })
        except Exception as e:
            logger.error(f"Error saving call reminder: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    else:
        logger.error(f"Form validation failed!")
        logger.error(f"Form errors: {form.errors}")
        
        return JsonResponse({
            'success': False,
            'errors': dict(form.errors)
        }, status=400)


@require_http_methods(["POST"])
@csrf_protect
def call_reminder_update(request, pk):
    """API endpoint to update call reminder notes and completion status"""
    import json
    from .models import CallReminder
    
    try:
        reminder = get_object_or_404(CallReminder, id=pk)
        
        # Parse JSON body
        data = json.loads(request.body)
        
        # Update notes if provided
        if 'notes' in data:
            reminder.notes = data['notes']
        
        # Update completed status if provided
        if 'completed' in data:
            completed = data['completed']
            if isinstance(completed, str):
                completed = completed.lower() in ('true', '1', 'yes', 'on')
            reminder.completed = bool(completed)
        
        reminder.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating call reminder: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def call_reminder_delete(request, pk):
    """API endpoint to delete a call reminder"""
    from .models import CallReminder
    
    try:
        reminder = get_object_or_404(CallReminder, id=pk)
        reminder.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting call reminder: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def job_call_reminder_update(request, job_id):
    """API endpoint to get or create and update CallReminder for a job"""
    import json
    from .models import CallReminder, Job
    from .utils.events import get_call_reminder_sunday
    
    try:
        job = get_object_or_404(Job, id=job_id)
        
        # Parse JSON body
        data = json.loads(request.body)
        
        # Calculate the reminder date based on job's settings
        if job.has_call_reminder and job.call_reminder_weeks_prior:
            reminder_date = get_call_reminder_sunday(job.start_dt, job.call_reminder_weeks_prior).date()
        else:
            return JsonResponse({'error': 'Job does not have call reminder enabled'}, status=400)
        
        # Get or create CallReminder for this job
        reminder, created = CallReminder.objects.get_or_create(
            job=job,
            calendar=job.calendar,
            defaults={'reminder_date': reminder_date, 'notes': ''}
        )
        
        # Update the reminder_date in case job date changed
        reminder.reminder_date = reminder_date
        
        # Update notes if provided
        if 'notes' in data:
            reminder.notes = data['notes']
        
        # Update completed status if provided
        if 'completed' in data:
            completed = data['completed']
            if isinstance(completed, str):
                completed = completed.lower() in ('true', '1', 'yes', 'on')
            reminder.completed = bool(completed)
            # Also update the job's call_reminder_completed flag
            job.call_reminder_completed = reminder.completed
            job.save(update_fields=['call_reminder_completed'])
        
        reminder.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Call reminder updated successfully',
            'reminder_id': reminder.id
        })
        
    except Exception as e:
        logger.error(f"Error updating job call reminder: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def delete_job_api(request, job_id):
    """API endpoint to delete a job with CSRF protection"""
    try:
        job = get_object_or_404(Job, id=job_id)
        job_name = job.get_display_name()
        
        # Soft delete by setting is_deleted flag
        job.is_deleted = True
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Job for {job_name} deleted successfully.',
            'job_id': job_id
        })
        
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# Job Modal Views
def job_create_partial(request):
    """Return job creation form partial for panel"""
    from rental_scheduler.utils.recurrence import get_recurrence_meta
    
    call_reminder_notes = ''
    recurrence_meta = None
    
    work_order_v2 = None

    # Check if editing existing job
    if 'edit' in request.GET:
        try:
            job_id = int(request.GET['edit'])
            job = get_object_or_404(Job, pk=job_id)
            form = JobForm(instance=job)
            work_order_v2 = WorkOrderV2.objects.filter(job=job).first()
            
            # Compute recurrence metadata for display
            recurrence_meta = get_recurrence_meta(job)
            
            # Load call reminder notes if job has a call reminder
            if job.has_call_reminder:
                from .models import CallReminder
                call_reminder = CallReminder.objects.filter(job=job).first()
                if call_reminder:
                    call_reminder_notes = call_reminder.notes or ''
        except (ValueError, TypeError):
            form = JobForm()
    else:
        # New job creation
        initial = {'all_day': True}
        if 'date' in request.GET:
            try:
                from datetime import datetime
                date_str = request.GET['date']
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Use date-only format since all_day is True by default
                initial['start_dt'] = date_obj.strftime(DATE_ONLY_FMT)
                initial['end_dt'] = date_obj.strftime(DATE_ONLY_FMT)
            except ValueError:
                pass  # Invalid date format, ignore
        else:
            # No date provided - default to today
            from datetime import date as _date
            today = _date.today()
            # Use date-only format since all_day is True by default
            initial['start_dt'] = today.strftime(DATE_ONLY_FMT)
            initial['end_dt'] = today.strftime(DATE_ONLY_FMT)
        
        # Pre-select calendar based on current filter
        if 'calendar' in request.GET:
            try:
                calendar_id = int(request.GET['calendar'])
                calendar = Calendar.objects.filter(pk=calendar_id, is_active=True).first()
                if calendar:
                    initial['calendar'] = calendar
            except (ValueError, TypeError):
                pass  # Invalid calendar ID, ignore
        
        # Fallback: if no calendar was set, select the first active calendar as default
        if 'calendar' not in initial:
            default_calendar = Calendar.objects.filter(is_active=True).first()
            if default_calendar:
                initial['calendar'] = default_calendar
        
        form = JobForm(initial=initial)
    
    return render(request, 'rental_scheduler/jobs/_job_form_partial.html', {
        'form': form,
        'call_reminder_notes': call_reminder_notes,
        'recurrence_meta': recurrence_meta,
        'work_order_v2': work_order_v2,
    })


def job_detail_partial(request, pk):
    """Return job details partial for panel"""
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'rental_scheduler/jobs/_job_detail_partial.html', {'job': job})


@require_http_methods(["POST"])
def job_create_submit(request):
    """Handle job creation/update form submission"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("="*80)
    logger.info(f"job_create_submit called with POST data: {dict(request.POST)}")
    logger.info(f"all_day value: {request.POST.get('all_day')}")
    logger.info(f"start_dt value: {request.POST.get('start_dt')}")
    logger.info(f"end_dt value: {request.POST.get('end_dt')}")
    logger.info("="*80)
    
    # Check if this is an update (job ID in form data)
    job_id = request.POST.get('job_id')
    if job_id:
        try:
            job = get_object_or_404(Job, pk=job_id)
            form = JobForm(request.POST, instance=job)
            logger.info(f"Updating existing job {job_id}")
        except (ValueError, TypeError):
            form = JobForm(request.POST)
            logger.info("Creating new job (invalid job_id)")
    else:
        form = JobForm(request.POST)
        logger.info("Creating new job")
    
    logger.info(f"Form is_valid: {form.is_valid()}")
    if not form.is_valid():
        logger.error(f"Form validation FAILED!")
        logger.error(f"Form errors: {form.errors}")
        logger.error(f"Form errors as dict: {dict(form.errors)}")
        for field, errors in form.errors.items():
            logger.error(f"  Field '{field}': {errors}")
    
    if form.is_valid():
        job = form.save(commit=False)
        
        # Explicitly handle checkbox fields (unchecked checkboxes don't send data)
        has_call_reminder = request.POST.get('has_call_reminder') == 'on'
        call_reminder_weeks = request.POST.get('call_reminder_weeks_prior')
        call_reminder_completed = request.POST.get('call_reminder_completed') == 'on'
        
        logger.info(f"Call reminder checkbox: {has_call_reminder}, weeks: {call_reminder_weeks}, completed: {call_reminder_completed}")
        
        job.has_call_reminder = has_call_reminder
        job.call_reminder_completed = call_reminder_completed
        if job.has_call_reminder and call_reminder_weeks:
            try:
                job.call_reminder_weeks_prior = int(call_reminder_weeks)
            except (ValueError, TypeError):
                job.call_reminder_weeks_prior = None
        else:
            job.call_reminder_weeks_prior = None
        
        job.save()
        
        # Handle call reminder notes - save to CallReminder object
        call_reminder_notes = request.POST.get('call_reminder_notes', '').strip()
        if job.has_call_reminder and job.call_reminder_weeks_prior:
            from .models import CallReminder
            from .utils.events import get_call_reminder_sunday
            
            # Calculate reminder date
            reminder_date = get_call_reminder_sunday(job.start_dt, job.call_reminder_weeks_prior).date()
            
            # Get or create CallReminder for this job
            call_reminder, created = CallReminder.objects.get_or_create(
                job=job,
                calendar=job.calendar,
                defaults={'reminder_date': reminder_date, 'notes': call_reminder_notes}
            )
            
            # Update if it already exists
            if not created:
                call_reminder.reminder_date = reminder_date
                call_reminder.notes = call_reminder_notes
                call_reminder.completed = job.call_reminder_completed
                call_reminder.save()
        
        # Handle recurring event creation
        recurrence_enabled = request.POST.get('recurrence_enabled') == 'on'
        if recurrence_enabled and not job_id:  # Only on creation, not updates
            # Don't allow instances to become recurring parents
            if job.recurrence_parent:
                messages.error(request, 'Cannot make a recurring instance into a new recurring series. Edit the parent series instead.')
                return redirect('rental_scheduler:job_list')
            
            recurrence_type = request.POST.get('recurrence_type', 'monthly')
            recurrence_interval_raw = request.POST.get('recurrence_interval', '1')
            try:
                recurrence_interval = int(recurrence_interval_raw)
            except (TypeError, ValueError):
                messages.error(request, 'Recurrence interval must be a whole number.')
                return redirect('rental_scheduler:job_list')

            if recurrence_interval < 1:
                messages.error(request, 'Recurrence interval must be at least 1.')
                return redirect('rental_scheduler:job_list')

            # Parse recurrence end mode (never, after_count, on_date)
            recurrence_end_mode = request.POST.get('recurrence_end', 'never')
            count = None
            until_date = None
            is_forever = False
            
            if recurrence_end_mode == 'never':
                # "Forever" series - no count or until_date
                is_forever = True
            elif recurrence_end_mode == 'after_count':
                recurrence_count_raw = request.POST.get('recurrence_count')
                if recurrence_count_raw:
                    try:
                        count = int(recurrence_count_raw)
                    except (TypeError, ValueError):
                        messages.error(request, 'Recurrence count must be a whole number.')
                        return redirect('rental_scheduler:job_list')

                    if count < 1:
                        messages.error(request, 'Recurrence count must be at least 1.')
                        return redirect('rental_scheduler:job_list')

                    if count > 500:
                        messages.error(request, 'Recurrence count cannot exceed 500 occurrences.')
                        return redirect('rental_scheduler:job_list')
            elif recurrence_end_mode == 'on_date':
                recurrence_until_raw = request.POST.get('recurrence_until')
                if recurrence_until_raw:
                    try:
                        until_date = datetime.strptime(recurrence_until_raw, DATE_ONLY_FMT).date()
                    except ValueError:
                        messages.error(request, 'Recurrence end date must be a valid date (YYYY-MM-DD).')
                        return redirect('rental_scheduler:job_list')
            
            # Create recurrence rule with end mode flag
            job.create_recurrence_rule(
                recurrence_type=recurrence_type,
                interval=recurrence_interval,
                count=count,
                until_date=until_date
            )
            
            # Store 'end' flag in recurrence_rule for forever series
            if is_forever:
                rule = job.recurrence_rule or {}
                rule['end'] = 'never'
                job.recurrence_rule = rule
                job.save(update_fields=['recurrence_rule'])
                logger.info(f"Created forever recurring job {job.id} with {recurrence_type} recurrence")
            else:
                # Generate recurring instances for non-forever series
                job.generate_recurring_instances()
                logger.info(f"Created recurring job {job.id} with {recurrence_type} recurrence ({count or 'until ' + str(until_date)} occurrences)")
        
        # Handle recurring event updates (finite -> forever conversion)
        elif recurrence_enabled and job_id and job.is_recurring_parent:
            # Only allow editing recurring parents (not instances)
            if job.recurrence_parent:
                messages.error(request, 'Cannot edit recurrence for an instance. Edit the parent series instead.')
                return redirect('rental_scheduler:job_list')
            
            # Parse recurrence settings from form
            recurrence_end_mode = request.POST.get('recurrence_end', 'never')
            
            # Update recurrence rule based on end mode
            if recurrence_end_mode == 'never':
                # Converting to forever series
                rule = job.recurrence_rule or {}
                rule['end'] = 'never'
                rule['count'] = None
                rule['until_date'] = None
                job.recurrence_rule = rule
                job.save(update_fields=['recurrence_rule'])
                logger.info(f"Updated job {job.id} to forever recurring series")
            elif recurrence_end_mode == 'after_count':
                # Converting to finite count series
                recurrence_count_raw = request.POST.get('recurrence_count')
                if recurrence_count_raw:
                    try:
                        count = int(recurrence_count_raw)
                        if count < 1:
                            messages.error(request, 'Recurrence count must be at least 1.')
                            return redirect('rental_scheduler:job_list')
                        if count > 500:
                            messages.error(request, 'Recurrence count cannot exceed 500 occurrences.')
                            return redirect('rental_scheduler:job_list')
                        
                        rule = job.recurrence_rule or {}
                        rule['count'] = count
                        rule['until_date'] = None
                        if 'end' in rule:
                            del rule['end']
                        job.recurrence_rule = rule
                        job.save(update_fields=['recurrence_rule'])
                        logger.info(f"Updated job {job.id} to finite count recurring series (count={count})")
                    except (TypeError, ValueError):
                        messages.error(request, 'Recurrence count must be a whole number.')
                        return redirect('rental_scheduler:job_list')
            elif recurrence_end_mode == 'on_date':
                # Converting to finite date series
                recurrence_until_raw = request.POST.get('recurrence_until')
                if recurrence_until_raw:
                    try:
                        until_date = datetime.strptime(recurrence_until_raw, DATE_ONLY_FMT).date()
                        rule = job.recurrence_rule or {}
                        rule['count'] = None
                        rule['until_date'] = until_date.isoformat()
                        if 'end' in rule:
                            del rule['end']
                        job.recurrence_rule = rule
                        job.save(update_fields=['recurrence_rule'])
                        logger.info(f"Updated job {job.id} to finite date recurring series (until={until_date})")
                    except ValueError:
                        messages.error(request, 'Recurrence end date must be a valid date (YYYY-MM-DD).')
                        return redirect('rental_scheduler:job_list')
        
        logger.info(f"Job saved successfully: {job.id}")
        # Return a simple success response that triggers the close action
        # Include job ID in the trigger for the minimize button to use
        import json as json_module
        trigger_data = json_module.dumps({'jobSaved': {'jobId': job.id}})
        return HttpResponse(
            f'<input type="hidden" name="job_id" value="{job.id}" hx-swap-oob="true"><div hx-swap-oob="true" id="job-success">Job saved successfully!</div>', 
            headers={'HX-Trigger': trigger_data}
        )
    else:
        logger.error(f"Form validation errors: {form.errors}")
        return render(request, 'rental_scheduler/jobs/_job_form_partial.html', {'form': form}, status=400)

# API Views for Job Updates
@require_http_methods(["POST"])
@csrf_protect
def job_create_api(request):
    """API endpoint to create a new job"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        print(f"DEBUG: Received data: {data}")  # Debug logging
        
        # Create new job
        job = Job()
        
        # Set job fields
        job.business_name = data.get('business_name', '')
        job.contact_name = data.get('contact_name', '')
        job.phone = data.get('phone', '')
        job.trailer_color = data.get('trailer_color', '')
        job.trailer_serial = data.get('trailer_serial', '')
        job.trailer_details = data.get('trailer_details', '')
        job.notes = data.get('notes', '')
        job.repair_notes = data.get('repair_notes', '')
        job.status = data.get('status', 'uncompleted')
        
        # Handle repeat settings
        job.repeat_type = data.get('repeat_type', 'none') or 'none'
        if job.repeat_type == 'monthly':
            job.repeat_n_months = int(data.get('repeat_n_months', data.get('repeat_months', 1)))
        else:
            job.repeat_n_months = None
        
        # Determine if this is an all-day event
        all_day = data.get('allDay', data.get('all_day', False))
        if isinstance(all_day, str):
            all_day = all_day.lower() in ('true', '1', 'yes', 'on')
        job.all_day = bool(all_day)
        
        # Handle dates with normalization for all-day events
        start_value = data.get('start', data.get('start_dt'))
        end_value = data.get('end', data.get('end_dt'))
        
        if start_value:
            try:
                # Use normalization helper for proper timezone handling
                start_dt_utc, end_dt_utc, _, _, _ = normalize_event_datetimes(
                    start_value,
                    end_value,
                    job.all_day
                )
                job.start_dt = start_dt_utc
                job.end_dt = end_dt_utc
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Set default calendar to first active calendar
        first_calendar = Calendar.objects.filter(is_active=True).first()
        if first_calendar:
            job.calendar = first_calendar
        
        # Save the job
        print(f"DEBUG: About to save job with start_dt={job.start_dt}, end_dt={job.end_dt}")  # Debug logging
        job.save()
        print(f"DEBUG: Job saved successfully with ID: {job.id}")  # Debug logging
        
        # Return created job data with proper formatting for FullCalendar
        if job.all_day:
            start_str = timezone.localtime(job.start_dt).date().isoformat()
            end_str = timezone.localtime(job.end_dt).date().isoformat()
        else:
            # Use strftime to avoid timezone offset in ISO string
            start_str = timezone.localtime(job.start_dt).strftime('%Y-%m-%dT%H:%M:%S')
            end_str = timezone.localtime(job.end_dt).strftime('%Y-%m-%dT%H:%M:%S')
        
        return JsonResponse({
            'id': job.id,
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start': start_str,
            'end': end_str,
            'allDay': job.all_day,
            'status': job.status,
            'notes': job.notes,
            'repair_notes': job.repair_notes,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"DEBUG: Error creating job: {e}")  # Debug logging
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_protect
def job_update_api(request, pk):
    """API endpoint for updating job data with CSRF protection"""
    
    try:
        job = get_object_or_404(Job, pk=pk)
        
        # Parse JSON data
        data = json.loads(request.body)
        
        # Update job fields
        job.business_name = data.get('business_name', job.business_name)
        job.contact_name = data.get('contact_name', job.contact_name)
        job.phone = data.get('phone', job.phone)
        job.trailer_color = data.get('trailer_color', job.trailer_color)
        job.trailer_serial = data.get('trailer_serial', job.trailer_serial)
        job.trailer_details = data.get('trailer_details', job.trailer_details)
        job.notes = data.get('notes', job.notes)
        job.repair_notes = data.get('repair_notes', job.repair_notes)
        job.status = data.get('status', job.status)
        
        # Handle repeat settings
        if 'repeat_type' in data:
            job.repeat_type = data.get('repeat_type', 'none') or 'none'
            if job.repeat_type == 'monthly':
                job.repeat_n_months = int(data.get('repeat_n_months', data.get('repeat_months', 1)))
            else:
                job.repeat_n_months = None
        
        # Determine if this is an all-day event
        if 'allDay' in data or 'all_day' in data:
            all_day = data.get('allDay', data.get('all_day', job.all_day))
            if isinstance(all_day, str):
                all_day = all_day.lower() in ('true', '1', 'yes', 'on')
            job.all_day = bool(all_day)
        
        # Handle dates with normalization for all-day events
        start_value = data.get('start', data.get('start_dt'))
        end_value = data.get('end', data.get('end_dt'))
        
        if start_value or end_value:
            # Use current values as fallback if one is missing
            if not start_value:
                start_value = job.start_dt
            if not end_value:
                end_value = job.end_dt
            
            try:
                # Use normalization helper for proper timezone handling
                start_dt_utc, end_dt_utc, _, _, _ = normalize_event_datetimes(
                    start_value,
                    end_value,
                    job.all_day
                )
                job.start_dt = start_dt_utc
                job.end_dt = end_dt_utc
            except (ValueError, TypeError) as e:
                return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        
        # Save the job
        job.save()
        
        # Return updated job data with proper formatting for FullCalendar
        if job.all_day:
            start_str = timezone.localtime(job.start_dt).date().isoformat()
            end_str = timezone.localtime(job.end_dt).date().isoformat()
        else:
            # Use strftime to avoid timezone offset in ISO string
            start_str = timezone.localtime(job.start_dt).strftime('%Y-%m-%dT%H:%M:%S')
            end_str = timezone.localtime(job.end_dt).strftime('%Y-%m-%dT%H:%M:%S')
        
        return JsonResponse({
            'id': job.id,
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start': start_str,
            'end': end_str,
            'allDay': job.all_day,
            'status': job.status,
            'notes': job.notes,
            'repair_notes': job.repair_notes,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def job_detail_api(request, pk):
    """API endpoint to get job details"""
    try:
        job = get_object_or_404(Job, pk=pk)
        
        # Return job data
        return JsonResponse({
            'id': job.id,
            'calendar_name': job.calendar.name if job.calendar_id else '',
            'business_name': job.business_name,
            'contact_name': job.contact_name,
            'phone': job.phone,
            'trailer_color': job.trailer_color,
            'trailer_serial': job.trailer_serial,
            'trailer_details': job.trailer_details,
            'start_dt': job.start_dt.isoformat() if job.start_dt else None,
            'end_dt': job.end_dt.isoformat() if job.end_dt else None,
            'all_day': job.all_day,
            'status': job.status,
            'notes': job.notes,
            'repair_notes': job.repair_notes,
            'display_name': job.display_name,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def extract_phone_from_text(text):
    """
    Extract phone number from text using regex patterns.
    Handles formats like: 740-501-9004, 231-6407, (330) 265-4243, etc.
    """
    if not text:
        return None
    
    # Common phone patterns
    patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 740-501-9004
        r'\b\d{3}-\d{4}\b',        # 231-6407
        r'\(\d{3}\)\s*\d{3}-\d{4}', # (330) 265-4243
        r'\b\d{3}\s+\d{3}-\d{4}\b', # 330 265-4243
        r'\b\d{10}\b',             # 7405019004
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None


def parse_ics_datetime(dt_value, is_all_day=False):
    """
    Convert iCalendar datetime to timezone-aware datetime.
    Handles both DATE and DATETIME formats.
    """
    if dt_value is None:
        return None
    
    # If it's already a datetime object
    if isinstance(dt_value, datetime):
        # Make it timezone-aware if it isn't
        if timezone.is_naive(dt_value):
            return timezone.make_aware(dt_value)
        return dt_value
    
    # If it's a date object (all-day event)
    if isinstance(dt_value, date):
        # Convert to datetime at midnight
        dt = datetime.combine(dt_value, datetime.min.time())
        return timezone.make_aware(dt)
    
    return None


def convert_rrule_to_json(rrule_str):
    """
    Convert iCalendar RRULE string to our JSON format.
    Example: "FREQ=YEARLY;UNTIL=20280128" -> {"type": "yearly", "interval": 1, "until_date": "2028-01-28"}
    """
    if not rrule_str:
        return None
    
    try:
        # Parse RRULE components
        parts = {}
        for part in rrule_str.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                parts[key] = value
        
        # Extract frequency
        freq = parts.get('FREQ', '').lower()
        if freq not in ['yearly', 'monthly', 'weekly', 'daily']:
            return None
        
        # Build JSON rule
        rule = {
            'type': freq,
            'interval': int(parts.get('INTERVAL', 1))
        }
        
        # Add count if present
        if 'COUNT' in parts:
            rule['count'] = int(parts['COUNT'])
        
        # Add until date if present
        if 'UNTIL' in parts:
            until_str = parts['UNTIL']
            # Parse UNTIL date (format: YYYYMMDD or YYYYMMDDTHHMMSSZ)
            if 'T' in until_str:
                until_str = until_str.split('T')[0]
            # Format as YYYY-MM-DD
            if len(until_str) >= 8:
                rule['until_date'] = f"{until_str[:4]}-{until_str[4:6]}-{until_str[6:8]}"
        
        return rule
    
    except Exception as e:
        logger.error(f"Error parsing RRULE: {rrule_str}, Error: {str(e)}")
        return None


@csrf_protect
def calendar_import(request):
    """
    View for importing calendar events from .ics files.
    Displays upload form and processes imported events.
    """
    results = None
    
    logger.info(f"[DEBUG] calendar_import called - Method: {request.method}")
    
    if request.method == 'POST':
        logger.info(f"[DEBUG] POST data keys: {list(request.POST.keys())}")
        logger.info(f"[DEBUG] FILES data keys: {list(request.FILES.keys())}")
        logger.info(f"[DEBUG] Calendar value: {request.POST.get('calendar', 'NOT FOUND')}")
        logger.info(f"[DEBUG] File in FILES: {'ics_file' in request.FILES}")
        
        form = CalendarImportForm(request.POST, request.FILES)
        
        logger.info(f"[DEBUG] Form is_valid: {form.is_valid()}")
        if not form.is_valid():
            logger.error(f"[DEBUG] Form errors: {form.errors}")
            logger.error(f"[DEBUG] Form errors dict: {dict(form.errors)}")
        
        if form.is_valid():
            try:
                from icalendar import Calendar as ICalendar
                import uuid
                
                # Get the uploaded file and selected calendar
                ics_file = request.FILES['ics_file']
                target_calendar = form.cleaned_data['calendar']
                use_ai_parsing = form.cleaned_data.get('use_ai_parsing', True)
                
                # Generate unique batch ID for this import
                batch_id = str(uuid.uuid4())
                
                logger.info(f"Starting calendar import - AI parsing: {use_ai_parsing}")
                
                # Read and parse the .ics file
                ics_content = ics_file.read()
                cal = ICalendar.from_ical(ics_content)
                
                # Track results
                imported_count = 0
                skipped_count = 0
                error_count = 0
                errors = []
                
                # Process each event
                for component in cal.walk():
                    if component.name == "VEVENT":
                        try:
                            # Extract fields
                            summary = str(component.get('summary', ''))
                            description = str(component.get('description', ''))
                            dtstart = component.get('dtstart')
                            dtend = component.get('dtend')
                            created = component.get('created')
                            rrule = component.get('rrule')
                            status = component.get('status')
                            uid = str(component.get('uid', ''))
                            
                            # Determine job status - map CANCELLED to completed
                            job_status = 'uncompleted'  # Default
                            if status:
                                status_str = str(status).upper()
                                if status_str == 'CANCELLED':
                                    job_status = 'completed'
                            
                            # Skip if missing required fields
                            if not dtstart or not dtend:
                                skipped_count += 1
                                errors.append(f"Event '{summary}' skipped: missing start or end date")
                                continue
                            
                            # Get datetime values
                            dtstart_val = dtstart.dt if hasattr(dtstart, 'dt') else dtstart
                            dtend_val = dtend.dt if hasattr(dtend, 'dt') else dtend
                            
                            # Check if all-day event
                            is_all_day = isinstance(dtstart_val, date) and not isinstance(dtstart_val, datetime)
                            
                            # Parse dates
                            start_dt = parse_ics_datetime(dtstart_val, is_all_day)
                            end_dt = parse_ics_datetime(dtend_val, is_all_day)
                            
                            if not start_dt or not end_dt:
                                skipped_count += 1
                                errors.append(f"Event '{summary}' skipped: invalid date format")
                                continue
                            
                            # For all-day events, adjust end time
                            if is_all_day:
                                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                            
                            # Extract phone from summary
                            phone = extract_phone_from_text(summary)
                            
                            # Remove phone from business_name if found
                            business_name = summary
                            if phone:
                                business_name = re.sub(r'\s*' + re.escape(phone) + r'\s*', ' ', business_name).strip()
                            
                            # Parse date_call_received
                            date_call_received = None
                            if created:
                                created_val = created.dt if hasattr(created, 'dt') else created
                                date_call_received = parse_ics_datetime(created_val)
                            
                            # Convert RRULE if present
                            recurrence_rule = None
                            if rrule:
                                rrule_str = str(rrule.to_ical().decode('utf-8'))
                                recurrence_rule = convert_rrule_to_json(rrule_str)
                            
                            # Parse description with AI to extract structured fields (if enabled)
                            if use_ai_parsing:
                                parsed_description = parse_description_with_ai(description)
                            else:
                                # No AI parsing - use raw description in notes
                                parsed_description = {
                                    'trailer_color': '',
                                    'trailer_serial': '',
                                    'trailer_details': '',
                                    'repair_notes': '',
                                    'quote': None,
                                    'unparsed_notes': description
                                }
                            
                            # Create Job instance
                            job = Job(
                                calendar=target_calendar,
                                status=job_status,
                                business_name=business_name[:150] if business_name else '',  # Limit to field max_length
                                phone=phone[:25] if phone else '',
                                start_dt=start_dt,
                                end_dt=end_dt,
                                all_day=is_all_day,
                                notes=parsed_description.get('unparsed_notes', description),
                                repair_notes=parsed_description.get('repair_notes', ''),
                                trailer_color=parsed_description.get('trailer_color', '')[:60],  # Limit to field max_length
                                trailer_serial=parsed_description.get('trailer_serial', '')[:120],  # Limit to field max_length
                                trailer_details=parsed_description.get('trailer_details', '')[:200],  # Limit to field max_length
                                quote=parsed_description.get('quote'),
                                date_call_received=date_call_received,
                                recurrence_rule=recurrence_rule,
                                import_batch_id=batch_id,  # Track import batch
                                created_by=request.user if request.user.is_authenticated else None,
                            )
                            
                            # Validate and save
                            job.full_clean()
                            job.save()
                            
                            imported_count += 1
                            
                        except Exception as e:
                            error_count += 1
                            event_name = summary if 'summary' in locals() else 'Unknown'
                            error_msg = f"Event '{event_name}' error: {str(e)}"
                            errors.append(error_msg)
                            logger.error(f"Import error for UID {uid}: {str(e)}")
                
                # Prepare results
                results = {
                    'success': True,
                    'imported': imported_count,
                    'skipped': skipped_count,
                    'errors_count': error_count,
                    'error_details': errors[:20],  # Show first 20 errors
                    'calendar_name': target_calendar.name
                }
                
                # Debug logging
                logger.info(f"Import complete: {imported_count} imported, {skipped_count} skipped, {error_count} errors")
                
                # Create comprehensive success message
                message_parts = []
                message_parts.append(f'✓ Import Complete: {imported_count} event(s) successfully imported to "{target_calendar.name}"')
                
                if skipped_count > 0:
                    message_parts.append(f'{skipped_count} skipped')
                if error_count > 0:
                    message_parts.append(f'{error_count} had errors')
                
                messages.success(request, ' | '.join(message_parts))
                
                # Redirect to calendar to see imported events
                return redirect('rental_scheduler:calendar')
                
            except Exception as e:
                messages.error(request, f'Failed to import calendar: {str(e)}')
                logger.error(f"Calendar import error: {str(e)}")
                # Keep the form with data so user can see what they selected
                # form already has the POST data from line 1370
        else:
            # Form validation failed - show errors to user
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CalendarImportForm()
    
    return render(request, 'rental_scheduler/jobs/job_import.html', {
        'form': form,
        'title': 'Import Calendar Events'
    })


def import_history(request):
    """
    View showing recent calendar imports with ability to revert them.
    """
    from django.db.models import Count, Min, Max
    
    # Get all import batches with aggregated info
    imports = (Job.objects
               .filter(import_batch_id__isnull=False)
               .values('import_batch_id', 'calendar__name', 'calendar__id')
               .annotate(
                   count=Count('id'),
                   first_date=Min('start_dt'),
                   last_date=Max('start_dt'),
                   imported_at=Min('created_at')
               )
               .order_by('-imported_at'))
    
    return render(request, 'rental_scheduler/jobs/import_history.html', {
        'imports': imports,
        'title': 'Import History'
    })


@csrf_protect
@require_http_methods(["POST"])
def revert_import(request, batch_id):
    """
    Delete all jobs from a specific import batch.
    """
    try:
        # Get all jobs in this batch
        jobs = Job.objects.filter(import_batch_id=batch_id)
        count = jobs.count()
        
        if count == 0:
            messages.warning(request, 'No jobs found for this import batch.')
            return redirect('rental_scheduler:import_history')
        
        # Delete all jobs in the batch
        jobs.delete()
        
        messages.success(request, f'Successfully reverted import: {count} job(s) deleted.')
        logger.info(f"Reverted import batch {batch_id}: {count} jobs deleted")
        
    except Exception as e:
        messages.error(request, f'Failed to revert import: {str(e)}')
        logger.error(f"Error reverting import {batch_id}: {str(e)}")
    
    return redirect('rental_scheduler:import_history')


# JSON Export/Import Views
@require_http_methods(["GET"])
def export_jobs(request, calendar_id=None):
    """
    Export jobs to JSON format for importing into another instance.
    Optionally filter by calendar_id.
    """
    try:
        # Get jobs to export
        jobs_qs = Job.objects.filter(is_deleted=False).select_related('calendar')
        
        export_source = "all"
        if calendar_id:
            calendar = get_object_or_404(Calendar, pk=calendar_id)
            jobs_qs = jobs_qs.filter(calendar=calendar)
            export_source = calendar.name
        
        # Order by start_dt for consistent export
        jobs_qs = jobs_qs.order_by('start_dt')
        
        # Build export data
        jobs_data = []
        parent_id_map = {}  # Map old parent IDs to temporary IDs for import
        
        for idx, job in enumerate(jobs_qs):
            job_dict = {
                # Basic info
                'business_name': job.business_name,
                'contact_name': job.contact_name,
                'phone': job.phone,
                
                # Address
                'address_line1': job.address_line1,
                'address_line2': job.address_line2,
                'city': job.city,
                'state': job.state,
                'postal_code': job.postal_code,
                
                # Timing
                'date_call_received': job.date_call_received.isoformat() if job.date_call_received else None,
                'start_dt': job.start_dt.isoformat(),
                'end_dt': job.end_dt.isoformat(),
                'all_day': job.all_day,
                
                # Call reminder
                'has_call_reminder': job.has_call_reminder,
                'call_reminder_weeks_prior': job.call_reminder_weeks_prior,
                'call_reminder_completed': job.call_reminder_completed,
                
                # Legacy repeat
                'repeat_type': job.repeat_type,
                'repeat_n_months': job.repeat_n_months,
                
                # Recurring events
                'recurrence_rule': job.recurrence_rule,
                'recurrence_original_start': job.recurrence_original_start.isoformat() if job.recurrence_original_start else None,
                'end_recurrence_date': job.end_recurrence_date.isoformat() if job.end_recurrence_date else None,
                
                # Job details
                'notes': job.notes,
                'repair_notes': job.repair_notes,
                
                # Trailer info
                'trailer_color': job.trailer_color,
                'trailer_serial': job.trailer_serial,
                'trailer_details': job.trailer_details,
                
                # Quote
                'quote': str(job.quote) if job.quote else None,
                'trailer_color_overwrite': job.trailer_color_overwrite,
                'quote_text': job.quote_text,
                
                # Status
                'status': job.status,
            }
            
            # Handle recurring parent relationships
            if job.is_recurring_parent:
                job_dict['_is_recurring_parent'] = True
                job_dict['_temp_id'] = f"parent_{idx}"
                parent_id_map[job.id] = f"parent_{idx}"
            elif job.is_recurring_instance and job.recurrence_parent_id:
                job_dict['_is_recurring_instance'] = True
                # Will be resolved during import
                if job.recurrence_parent_id in parent_id_map:
                    job_dict['_parent_temp_id'] = parent_id_map[job.recurrence_parent_id]
            
            jobs_data.append(job_dict)
        
        # Build the export structure
        export_data = {
            'version': '1.0',
            'exported_at': timezone.now().isoformat(),
            'export_source': export_source,
            'job_count': len(jobs_data),
            'jobs': jobs_data
        }
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y-%m-%d_%H%M%S')
        if calendar_id:
            filename = f"jobs_export_{export_source}_{timestamp}.json"
        else:
            filename = f"jobs_export_all_{timestamp}.json"
        
        # Create response
        response = HttpResponse(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"Exported {len(jobs_data)} jobs from '{export_source}'")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting jobs: {str(e)}", exc_info=True)
        messages.error(request, f"Error exporting jobs: {str(e)}")
        return redirect('rental_scheduler:job_list')


@csrf_protect
def import_jobs_json(request):
    """
    Import jobs from JSON export file.
    Allows user to select target calendar for all imported jobs.
    """
    from .forms import JobImportForm
    
    if request.method == 'POST':
        form = JobImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                json_file = form.cleaned_data['json_file']
                target_calendar = form.cleaned_data['target_calendar']
                
                # Read and parse JSON
                json_file.seek(0)
                content = json_file.read()
                data = json.loads(content)
                
                # Validate version
                if data.get('version') != '1.0':
                    messages.warning(request, f"Warning: Export version {data.get('version')} may not be fully compatible.")
                
                jobs_data = data.get('jobs', [])
                if not jobs_data:
                    messages.warning(request, "No jobs found in the export file.")
                    return redirect('rental_scheduler:calendar_import')
                
                # Generate import batch ID for tracking
                import uuid
                batch_id = str(uuid.uuid4())
                
                # Import jobs within transaction
                with transaction.atomic():
                    imported_count = 0
                    parent_map = {}  # Map temp IDs to new parent Job instances
                    jobs_to_link = []  # Store (job, parent_temp_id) tuples for second pass
                    
                    # First pass: import all jobs
                    for job_data in jobs_data:
                        is_parent = job_data.pop('_is_recurring_parent', False)
                        is_instance = job_data.pop('_is_recurring_instance', False)
                        temp_id = job_data.pop('_temp_id', None)
                        parent_temp_id = job_data.pop('_parent_temp_id', None)
                        
                        # Parse datetime fields
                        if job_data.get('date_call_received'):
                            job_data['date_call_received'] = datetime.fromisoformat(job_data['date_call_received'])
                        if job_data.get('start_dt'):
                            job_data['start_dt'] = datetime.fromisoformat(job_data['start_dt'])
                        if job_data.get('end_dt'):
                            job_data['end_dt'] = datetime.fromisoformat(job_data['end_dt'])
                        if job_data.get('recurrence_original_start'):
                            job_data['recurrence_original_start'] = datetime.fromisoformat(job_data['recurrence_original_start'])
                        if job_data.get('end_recurrence_date'):
                            job_data['end_recurrence_date'] = date.fromisoformat(job_data['end_recurrence_date'])
                        
                        # Quote is now a CharField, keep as string
                        if job_data.get('quote'):
                            job_data['quote'] = str(job_data['quote'])
                        
                        # Create the job
                        job = Job(
                            calendar=target_calendar,
                            import_batch_id=batch_id,
                            **job_data
                        )
                        
                        # Bypass full_clean during import to avoid validation issues
                        # Call the parent Model.save() directly instead of Job.save()
                        models.Model.save(job, force_insert=True)
                        
                        imported_count += 1
                        
                        # Track parents for second pass
                        if is_parent and temp_id:
                            parent_map[temp_id] = job
                        elif is_instance and parent_temp_id:
                            # Store for second pass
                            jobs_to_link.append((job, parent_temp_id))
                    
                    # Second pass: link recurring instances to parents
                    for job, parent_temp_id in jobs_to_link:
                        if parent_temp_id in parent_map:
                            parent_job = parent_map[parent_temp_id]
                            job.recurrence_parent = parent_job
                            models.Model.save(job, update_fields=['recurrence_parent'])
                
                messages.success(
                    request,
                    f"Successfully imported {imported_count} job(s) into calendar '{target_calendar.name}'. "
                    f"Import batch ID: {batch_id[:8]}..."
                )
                logger.info(f"Imported {imported_count} jobs from JSON export into calendar '{target_calendar.name}' (batch: {batch_id})")
                
                return redirect('rental_scheduler:job_list')
                
            except json.JSONDecodeError as e:
                messages.error(request, f"Invalid JSON file: {str(e)}")
            except KeyError as e:
                messages.error(request, f"Missing required field in export data: {str(e)}")
            except Exception as e:
                logger.error(f"Error importing jobs from JSON: {str(e)}", exc_info=True)
                messages.error(request, f"Error importing jobs: {str(e)}")
    else:
        form = JobImportForm()
    
    context = {
        'title': 'Import Jobs from JSON',
        'form': form,
        'import_type': 'json'
    }
    
    return render(request, 'rental_scheduler/jobs/job_import_json.html', context)
