# Since this package contains a "django" module, this is required on Python 2.
from __future__ import absolute_import

from django.conf import settings
from django.template.context import Context, RequestContext
from django.template.engine import _dirs_undefined, Engine


from .base import BaseEngine


class DjangoTemplates(BaseEngine):

    app_dirname = 'templates'

    def __init__(self, params):
        params = params.copy()
        options = params.pop('OPTIONS').copy()
        options.setdefault('debug', settings.TEMPLATE_DEBUG)
        options.setdefault('file_charset', settings.FILE_CHARSET)
        super(DjangoTemplates, self).__init__(params)
        self.engine = Engine(self.dirs, self.app_dirs, **options)

    def __repr__(self):
        return '<%(cls)s engine=%(engine)r>' % {
            'cls': self.__class__.__name__, 'engine': self.engine
        }

    def from_string(self, template_code):
        return Template(self.engine.from_string(template_code))

    def get_template(self, template_name, dirs=_dirs_undefined):
        return Template(self.engine.get_template(template_name, dirs))


class Template(object):

    def __init__(self, template):
        self.template = template

    def __repr__(self):
        return ('<Django%(cls)s loaders=%(engine)r, name=%(name)s, '
                'origin=%(origin)r>' % {
                    'cls': self.__class__.__name__,
                    'engine': self.template.engine.loaders,
                    'name': self.template.name,
                    'origin': self.origin,
                })

    @property
    def origin(self):
        # TODO: define the Origin API. For now simply forwarding to the
        #       underlying Template preserves backwards-compatibility.
        return self.template.origin

    def render(self, context=None, request=None):
        # TODO: require context to be a dict -- through a deprecation path?
        if not isinstance(context, Context):
            if request is None:
                context = Context(context)
            else:
                # The following pattern is required to ensure values from
                # context override those from template context processors.
                original_context = context
                context = RequestContext(request)
                if original_context:
                    context.push(original_context)

        return self.template.render(context)
