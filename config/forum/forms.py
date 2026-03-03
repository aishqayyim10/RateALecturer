from xml.etree.ElementTree import Comment
from .models import Review, Comment, Lecturer, Profile
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['overall_rating', 'difficulty', 'would_take_again', 'is_anonymous', 'comment']
        widgets = {
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'difficulty': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'would_take_again': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'cursor: pointer;'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'cursor: pointer;'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What was your experience like?'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', 'is_anonymous']
        labels = {
            'body': '' # This hides the label so it looks cleaner
        }
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add to the discussion...', 'style': 'width: 100%;'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'cursor: pointer;'}),
        }

class LecturerForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ['name', 'faculty', 'subject']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Dr. John Doe'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Data Structures'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'year', 'semester', 'bio']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'I am studying...'}),
        }

class CustomRegisterForm(UserCreationForm):
    # Make the email field explicitly required
    email = forms.EmailField(required=True, help_text="Required for password resets.")

    class Meta:
        model = User
        # Tell Django to include the email field right after the username
        fields = ['username', 'email']
        