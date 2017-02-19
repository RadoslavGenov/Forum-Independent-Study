from django import forms
from .models import Comment, Post
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Re-enter Password', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match')
        return cd['password2']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)
    
class SearchForm(forms.Form):
    query = forms.CharField()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'author', 'body', 'publish', 'status', 'tags', 'slug')