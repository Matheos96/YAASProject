from .models import *
from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from bootstrap_datepicker_plus import DateTimePickerInput


class AuctionForm(forms.ModelForm):

    class Meta:
        model = Auction
        fields = ('title', 'description', 'min_price', 'deadline')
        widgets = {
            'deadline': DateTimePickerInput(format='%d.%m.%Y %H:%M:%S')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['deadline'].label = 'Deadline<br /> (Format: dd.mm.YYYY HH:MM:SS)'
        self.fields['min_price'].label = 'Minimum price'

        self.helper = FormHelper
        self.helper.form_action = reverse("new_auction")
        self.helper.form_method = "post"
        self.helper.layout = Layout("title",
                                    "description",
                                    "min_price",
                                    "deadline",
                                    Submit("post", "Post", css_class="btn btn-primary"))


class EditAuctionForm(AuctionForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = reverse("edit_auction", kwargs={'auction_id': self.instance.id})
        self.helper.layout = Layout("description",
                                    Submit("post", "Save", css_class="btn btn-success"))


class ConfirmForm(forms.Form):
    title = forms.CharField(widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.HiddenInput())
    min_price = forms.CharField(widget=forms.HiddenInput())
    deadline = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_action = reverse("confirm_form")
        self.helper.form_method = "post"
        self.helper.layout = Layout("title",
                                    "description",
                                    "min_price",
                                    "deadline",
                                    Submit("yes", "Confirm", css_class="btn btn-success"),
                                    Submit("no", "Discard", css_class="btn btn-warning"))


class MakeBidForm(forms.Form):
    bid = forms.DecimalField(required=True, max_digits=9, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(MakeBidForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper
        self.helper.form_method = "post"
        self.helper.layout = Layout("bid",
                                    Submit("make_bid", "Make Bid", css_class="btn btn-primary"))
