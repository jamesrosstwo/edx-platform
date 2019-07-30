"""
Course API Views
"""

from __future__ import absolute_import

import search
from six import iteritems

from bulk_email.api import is_bulk_email_feature_enabled, is_user_opted_out_for_course
from edx_when.api import get_dates_for_course
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from edx_rest_framework_extensions.paginators import NamespacedPageNumberPagination
from opaque_keys.edx.locator import CourseLocator
from lms.djangoapps.certificates.api import get_certificate_for_user
from lms.djangoapps.program_enrollments.api.api import (
    get_due_dates,
    get_course_run_url,
    get_emails_enabled,
    get_course_run_status
)
from lms.djangoapps.program_enrollments.api.v1.constants import (
    CourseEnrollmentResponseStatuses,
    CourseRunProgressStatuses,
    MAX_ENROLLMENT_RECORDS,
    ProgramEnrollmentResponseStatuses,
)
from lms.djangoapps.program_enrollments.api.v1.serializers import CourseRunOverviewListSerializer
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.enrollments.api import get_enrollments
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from student.helpers import get_resume_urls_for_enrollments
from xmodule.modulestore.django import modulestore


from enterprise.models import EnterpriseCourseEnrollment, EnterpriseCustomerUser

from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin, LazySequence, view_auth_classes

# from . import USE_RATE_LIMIT_2_FOR_COURSE_LIST_API, USE_RATE_LIMIT_10_FOR_COURSE_LIST_API
# from .api import course_detail, list_courses
# from .forms import CourseDetailGetForm, CourseListGetForm
# from .serializers import CourseDetailSerializer, CourseSerializer


User = get_user_model()


class EnterpriseLearnerEnrollmentView(DeveloperErrorViewMixin, ListAPIView):
    """
    **Use Cases**

        _____________

    **Example Requests**

        GET /api/_____________

    **Response Values**

        _____________

    **Parameters:**

        _____________

    **Returns**

        _____________

    """
    def get(self, request, user_email):
        user = get_object_or_404(User, email=user_email)
        enterprise_customer_user = get_object_or_404(EnterpriseCustomerUser, user_id=user.id)

        enrollments = get_enrollments(user.username)
        # get enterprise enrollments for user --> we dont want all enrollments now
        
        ent_enrollments = EnterpriseCourseEnrollment.objects.filter(
            enterprise_customer_user=enterprise_customer_user
        ).values_list('course_id', flat=True)

        enrollments = [
            enrollment
            for enrollment in enrollments
            if enrollment['course_details']['course_id'] in ent_enrollments
        ]
        #print(enrollments)

        # we need enrollment objects for get_resume_urls_for_enrollments. otherwise we could skip that sstep
        enrollment_dict = {enrollment['course_details']['course_id']: enrollment for enrollment in enrollments}

        overviews = CourseOverview.get_from_ids_if_exists(enrollment_dict.keys())
        print(overviews)
        # resume_course_run_urls = get_resume_urls_for_enrollments(user, enrollment_dict.values())

        response = {
            'course_runs': [],
        }

        for enrollment in enrollments:
            # key in overview dictionary is a CourseLocator object, originating from a CourseKeyField
            course_locator = CourseLocator.from_string(enrollment['course_details']['course_id'])
            overview = overviews[course_locator]

            certificate_download_url = None
            is_certificate_passing = None
            certificate_creation_date = None
            certificate_info = get_certificate_for_user(user.username, enrollment['course_details']['course_id'])

            if certificate_info:
                certificate_download_url = certificate_info['download_url']
                is_certificate_passing = certificate_info['is_passing']
                certificate_creation_date = certificate_info['created']

            course_run_dict = {
                'course_run_id': enrollment['course_details']['course_id'],
                'display_name': overview.display_name_with_default,
                'course_run_status': get_course_run_status(overview, is_certificate_passing, certificate_creation_date),
                'course_run_url': get_course_run_url(request, enrollment['course_details']['course_id']),
                'start_date': overview.start,
                'end_date': overview.end,
                'due_dates': get_due_dates(request, enrollment['course_details']['course_id'], user),
            }

            if certificate_download_url:
                course_run_dict['certificate_download_url'] = certificate_download_url

            emails_enabled = get_emails_enabled(user, enrollment['course_details']['course_id'])
            if emails_enabled is not None:
                course_run_dict['emails_enabled'] = emails_enabled

            # if the url is '', then the url is None so we can omit it from the response
            #resume_course_run_url = resume_course_run_urls[enrollment['course_details']['course_id']]
            #if resume_course_run_url:
            #    course_run_dict['resume_course_run_url'] = resume_course_run_url
            print(course_run_dict)
            print('\n\n\n\n\n\n\n\n')
            response['course_runs'].append(course_run_dict)

        serializer = CourseRunOverviewListSerializer(response)
        return Response(serializer.data)

    