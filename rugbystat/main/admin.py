from django.urls import reverse
from django.utils.html import mark_safe


class CrossLinkMixin:

    def _get_admin_links(self, qs):
        """Return link (or "-") to display in list view column.

        :param instance: any Django model instance
        :return: str to represent link in admin list view.
        """
        if qs:
            display_text = ''
            label = None
            model_name = None
            for instance in qs:
                if not label:
                    label = instance._meta.app_label
                if not model_name:
                    model_name = instance._meta.model_name
                
                url = reverse('admin:{0}_{1}_change'.format(label, model_name),
                              args=(instance.pk,))
                display_text += f'<li><a href={url}>{instance}</a></li>'
            return mark_safe(f'<ul>{display_text}</ul>')  # nosec

        return '-'
