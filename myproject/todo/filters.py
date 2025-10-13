import django_filters
from .models import Task
from django.utils import timezone

class TaskFilter(django_filters.FilterSet):
    status=django_filters.ChoiceFilter(choices=Task.CHOICE_STATUS)
    expired_date=django_filters.ChoiceFilter(choices=[("Yes","Expired tasks"),("No","Not expired tasks")],method="filter_expired",label="Expired deadline")
    deadline_time=django_filters.DateFromToRangeFilter(field_name="deadline",label="Deadline",widget=django_filters.widgets.RangeWidget(
        attrs={"type":"date"}
    ),
    )

    class Meta:
        model=Task
        fields=['status']
    
    def filter_expired(self,queryset,name,value):
        if value == "Yes":
            return queryset.filter(deadline__lt=timezone.now())
        elif value=="No":
            return queryset.filter(deadline__gte=timezone.now())
        return queryset