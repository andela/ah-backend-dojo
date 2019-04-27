import json
from rest_framework import renderers


class ProfileRenderer(renderers.JSONRenderer):

    charset = "utf-8"
    object_label = 'profile'

    def render(self, data, media_type=None, renderer_context=None):
        # Function for displaying user profile
        # and errors 
        errors = data.get("errors")

        if errors:
            return super().render(data)
        return json.dumps({"profile": data})