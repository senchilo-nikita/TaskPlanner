from django import forms


class FriendInviteForm(forms.Form):
    email = forms.EmailField(label="Email друга")

