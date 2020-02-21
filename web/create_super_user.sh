#!/bin/sh
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@admin.com', 'Silex2109')" | python manage.py shell