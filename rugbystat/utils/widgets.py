from dal import autocomplete


class ModelSelect2Bootstrap(autocomplete.ModelSelect2):
    class Media:
        css = {
            'all': (
                # The one from dal_select2.widgets.Select2WidgetMixin
                'autocomplete_light/vendor/select2/dist/css/select2.css',
                # Bootstrap theme itself
                '//cdnjs.cloudflare.com/ajax/libs/select2-bootstrap-theme/0.1.0-beta.10/select2-bootstrap.min.css'
            )
        }

        js = (
            'autocomplete_light/jquery.init.js',
            'autocomplete_light/autocomplete.init.js',
            'autocomplete_light/vendor/select2/dist/js/select2.full.js',
            'autocomplete_light/select2.js',
        )

    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs.setdefault('data-theme', 'bootstrap')
        return attrs
