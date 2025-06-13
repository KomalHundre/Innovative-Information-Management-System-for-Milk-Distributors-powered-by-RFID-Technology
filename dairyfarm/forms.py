from django import forms
from .models import Farmer, MilkCollection
from django.contrib.auth.models import User

class FarmerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    bank_account_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    ifsc_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = Farmer
        fields = ['phone_number', 'bank_account_number', 'ifsc_code', 'address']
    
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['phone_number'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        farmer = super().save(commit=False)
        farmer.user = user
        farmer.rfid_number = f"RFID{user.id:06d}"  # Generate a dummy RFID number
        if commit:
            farmer.save()
        return farmer

class MilkCollectionForm(forms.ModelForm):
    class Meta:
        model = MilkCollection
        fields = ['farmer', 'quantity', 'fat_content', 'session']
        widgets = {
            'farmer': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fat_content': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
        }