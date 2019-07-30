"""
Course API URLs
"""
from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import include, url

from .views import EnterpriseLearnerEnrollmentView

urlpatterns = [
    url(r'^learner_enrollments/(?P<user_email>.+)$', EnterpriseLearnerEnrollmentView.as_view(), name="enterprise-enrollment-list"),
]



