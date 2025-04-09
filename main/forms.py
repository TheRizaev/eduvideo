from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, ExpertiseArea
import re
from datetime import date
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    # Override the username field to be a regular CharField with no validation
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w @+-]+$',  # разрешает пробелы
                message=(
                    "Enter a valid username. This value may contain only letters, "
                    "numbers, spaces and @/./+/-/_ characters."
                )
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'autocomplete': 'off'  # Prevent browser validation
        }),
        help_text="Можно использовать любые символы и пробелы между ними."
    )
    
    email = forms.EmailField(required=True)
    identification = forms.CharField(
        required=True,
        help_text="Your identification starts with @ followed by lowercase letters and/or numbers. Choose wisely as it cannot be changed later.",
        max_length=30
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'text', 
            'class': 'custom-date-picker',
            'placeholder': 'ДД.ММ.ГГГГ'
        }),
        help_text="Your date of birth",
        input_formats=['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y']
    )
    
    class Meta:
        model = User
        fields = ['username', 'identification', 'email', 'date_of_birth', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use')
        return email
    
    def clean_username(self):
        # Get username with minimum validation - just ensuring it's not empty
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Username is required')
            
        # Only check if there's no consecutive spaces (single spaces between characters are allowed)
        if re.search(r'\s\s+', username):
            raise forms.ValidationError('Multiple consecutive spaces are not allowed')
        
        # Trim leading and trailing spaces
        username = username.strip()
            
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
            
        # Only other validation is maximum length which is handled by the field itself
        return username
        
    def clean_identification(self):
        identification = self.cleaned_data.get('identification')
        
        # Check if identification starts with @
        if not identification.startswith('@'):
            raise forms.ValidationError('Identification must start with @')
            
        # Remove @ for validation but keep it in the actual identification
        identification_without_at = identification[1:]
        
        # Check if the rest contains only lowercase letters and numbers
        if not re.match(r'^[a-z0-9]+$', identification_without_at):
            raise forms.ValidationError('Identification can only contain lowercase letters and numbers after @')
        
        return identification
        
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        today = date.today()
        
        # Check if user is at least 13 years old
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 13:
            raise forms.ValidationError('You must be at least 13 years old to register')
            
        # Check if date is not in the future
        if dob > today:
            raise forms.ValidationError('Date of birth cannot be in the future')
            
        return dob

class UserDetailsForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your first name'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your last name'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError('First name is required')
        return first_name
        
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError('Last name is required')
        return last_name

class EmailVerificationForm(forms.Form):
    verification_code = forms.CharField(
        required=True,
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit code', 'class': 'verification-input'}),
        help_text="Enter the 6-digit code sent to your email"
    )
    
    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code')
        if not code.isdigit():
            raise forms.ValidationError('Verification code must contain only numbers')
        return code

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']
        
class AuthorApplicationForm(forms.ModelForm):
    expertise_areas = forms.ModelMultipleChoiceField(
        queryset=ExpertiseArea.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = UserProfile
        fields = ['credentials', 'expertise_areas']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['credentials'].widget.attrs.update({
            'placeholder': 'Tell us about your education, experience, certificates and why you want to become an author'
        })
