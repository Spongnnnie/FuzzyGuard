from django import forms

class UserInfoForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    date_of_birth = forms.DateField(label='Date of Birth', widget=forms.SelectDateWidget(years=range(1900, 2024)))
    maiden_name = forms.CharField(label='Maiden Name', max_length=100)
    nickname = forms.CharField(label='Nickname', max_length=100)
    gender = forms.ChoiceField(label='Gender', choices=[('Male', 'Male'), ('Female', 'Female')])
    religion = forms.ChoiceField(label='Religion', choices=[('Christian', 'Christian'), ('Islam', 'Islam'),('Hindu','Hindu'),('Buddhist','Buddhist')])
    profession = forms.CharField(label='Profession', max_length=100)
    complexion = forms.CharField(label='Complexion', max_length=100)
