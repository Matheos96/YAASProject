from .models import *
from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class AuctionForm(forms.ModelForm):

    class Meta:
        model = Auction
        fields = ('title', 'description', 'min_price', 'deadline')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        #self.helper.form_action = reverse("login_user")
        self.helper.form_method = "post"
        self.helper.layout = Layout("title",
                                    "description",
                                    "min_price",
                                    "deadline",
                                    Submit("post", "Post", css_class="btn btn-success"))



