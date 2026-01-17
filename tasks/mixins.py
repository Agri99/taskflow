from django.contrib.auth.mixins import LoginRequiredMixin

class OwnerRequiredMixin(LoginRequiredMixin):
    owner_field = 'owner'

    def get_queryset(self):
        qs = super().get_queryset()
        filter_kwargs = {self.owner_field: self.request.user}
        return qs.filter(**filter_kwargs)