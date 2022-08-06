from django import forms
from tinymce.widgets import TinyMCE
from .models import Post, Comment


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 20}
        )
    )
    class Meta:
        model = Post
        fields = '__all__'


class CommentForm(forms.ModelForm):
    name= forms.CharField()
    email= forms.EmailField()
    body = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 2}))
    class Meta:
        model = Comment
        fields = ("name", "email", "body")
