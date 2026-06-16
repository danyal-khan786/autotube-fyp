# created manually!
from django import forms
from .models import VideoAnalysis

class VideoInputForm(forms.ModelForm):
    """
    Used exclusively for the CREATE operation. 
    The user only provides the URL; the AI handles the rest.
    """
    class Meta:
        model = VideoAnalysis
        fields = ['youtube_url']
        widgets = {
            'youtube_url': forms.URLInput(attrs={
                'placeholder': 'https://www.youtube.com/watch?v=...',
                'class': 'form-control form-control-lg shadow-sm',
                'autocomplete': 'off'
            })
        }
        labels = {
            'youtube_url': '' # Hides the default label for a cleaner UI
        }


class VideoAnalysisCRUDForm(forms.ModelForm):
    """
    Used for UPDATE and READ operations.
    Allows the user to manually edit the AI-generated text if they want to tweak it.
    """
    class Meta:
        model = VideoAnalysis
        fields = [
            'video_title', 
            'summary', 
            'tone_analysis', 
            'target_audience'
        ]
        widgets = {
            'video_title': forms.TextInput(attrs={'class': 'form-control fw-bold'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tone_analysis': forms.TextInput(attrs={'class': 'form-control'}),
            'target_audience': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Custom flag to instantly turn this into a "Read-Only" form
        read_only = kwargs.pop('read_only', False)
        super().__init__(*args, **kwargs)
        
        if read_only:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = True
                field.widget.attrs['readonly'] = True