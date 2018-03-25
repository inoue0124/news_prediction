from django import forms

class UrlForm(forms.Form):
    url = forms.URLField(max_length=250, required=False, label='URLを入力')
