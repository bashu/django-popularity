# -*- coding: utf-8 -*-

from django.conf import settings

from .tasks import update_hitcount, HitCountJob


class PopularityMixin(object):

    def get(self, request, *args, **kwargs):
        response = super(PopularityMixin, self).get(request, *args, **kwargs)
        if getattr(settings, 'USE_HITCOUNT', False):
            from hitcount.utils import get_ip

            opts, u = self.object._meta, request.user

            if not request.session.session_key:
                request.session.save()

            update_hitcount.delay(
                session_key=request.session.session_key,
                ip_address=get_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                username=u.username if u.is_authenticated() else None,
                app_label=opts.app_label,
                model=opts.module_name,
                object_id=self.object.id,
                )

        return response

    @classmethod
    def get_hitcount_for(cls, obj):
        if getattr(settings, 'USE_HITCOUNT', False):
            opts, pk = obj._meta, obj.pk
            return HitCountJob().get(opts.app_label, opts.module_name, pk)
        return None
