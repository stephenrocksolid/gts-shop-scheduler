import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db
def test_work_order_company_profile_is_singleton():
    from rental_scheduler.models import WorkOrderCompanyProfile

    profile1 = WorkOrderCompanyProfile.get_solo()
    profile2 = WorkOrderCompanyProfile.get_solo()

    assert profile1.pk == 1
    assert profile2.pk == 1
    assert WorkOrderCompanyProfile.objects.count() == 1


@pytest.mark.django_db
def test_work_order_employee_name_is_unique():
    from rental_scheduler.models import WorkOrderEmployee

    emp1 = WorkOrderEmployee(name="Alice")
    emp1.full_clean()
    emp1.save()

    emp2 = WorkOrderEmployee(name="Alice")
    with pytest.raises(ValidationError):
        emp2.full_clean()


@pytest.mark.django_db
def test_work_order_number_sequence_allocates_sequential_numbers():
    from rental_scheduler.models import WorkOrderNumberSequence

    seq = WorkOrderNumberSequence.get_solo(start_number=100)
    assert seq.start_number == 100
    assert seq.next_number == 100

    n1 = WorkOrderNumberSequence.allocate_work_order_number()
    n2 = WorkOrderNumberSequence.allocate_work_order_number()

    assert (n1, n2) == (100, 101)

    seq.refresh_from_db()
    assert seq.next_number == 102
