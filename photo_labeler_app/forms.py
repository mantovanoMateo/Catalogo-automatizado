from django import forms

class UploadExcelForm(forms.Form):
    file = forms.FileField()

class UploadImagesForm(forms.Form):
    images = forms.FileField()
