#!/bin/bash


TIMESTAMP=$(DATE '+%y-%m-%d %H:%M:%S')


DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer
fro django.db.models import Max


one_year_ago = timezone.now() - timedelta(days=365)
customers = Customer.objects.annotate(last_order=Max('order_created_at')).filter(last_order_lt=one_year_ago)
count = customers.count()
customers.delete()
print(count)
")


echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt


