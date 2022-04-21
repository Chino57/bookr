from django import forms
from django.core.exceptions import ValidationError
from .models import Publisher, Review

RADIO_CHOICES = (("Value One", "Value One Display"),
                 ("Value Two", "Text For Value Two"),
                 ("Value Three", "Value Three's Display Text"))

BOOK_CHOICES = (("Non-Fiction",
                 (("1", "Deep Learning with Keras"),
                  ("2", "Web Development with Django"))),
                ("Fiction",
                 (("3", "Brave New World"),
                  ("4", "The Great Gatsby"))))

class ExampleForm(forms.Form):
    text_input = forms.CharField(max_length=3)
    password_input = forms.CharField(widget=forms.PasswordInput,min_length=8)
    checkbox_on = forms.BooleanField()
    radio_input = forms.ChoiceField(choices=RADIO_CHOICES, widget=forms.RadioSelect)
    favorite_book = forms.ChoiceField(choices=BOOK_CHOICES)
    books_you_own = forms.MultipleChoiceField(required=False,choices=BOOK_CHOICES)
    text_area = forms.CharField(widget=forms.Textarea)
    integer_input = forms.IntegerField(min_value=1, max_value=10)
    float_input = forms.FloatField()
    decimal_input = forms.DecimalField(max_digits=5,decimal_places=3)
    email_input = forms.EmailField()
    date_input = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    hidden_input = forms.CharField(widget=forms.HiddenInput, initial="Hidden Value")


class SearchForm(forms.Form):
    search = forms.CharField(required=False, min_length=3)
    search_in = forms.ChoiceField(required=False, choices=(("title", "Title"),
                                                           ("contributor", "Contributor")))


class NewsletterSignupForm(forms.Form):
    signup = forms.BooleanField(label="Sign up to newsletter?", required=False)
    email = forms.EmailField(help_text="Enter your email address to subscribe", required=False)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['signup'] and not cleaned_data.get("email"):
            self.add_error("email", "Your email address is required if signing up for the newsletter.")


class OrderForm(forms.Form):
    def validate_email_domain(value):
        if value.split("@")[-1].lower() != "example.com":
            raise ValidationError("The email address must be on the domain example.com.")

    def clean_email(self):
        return self.cleaned_data["email"].lower()

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["send_confirmation"] and not cleaned_data.get("email"):
            self.add_error("email", "Please enter an email address to receive the confirmation message.")
        elif cleaned_data.get("email") and not cleaned_data["send_confirmation"]:
            self.add_error("send_confirmation", "Please check this if you want to receive a confirmation email")
        item_total = cleaned_data.get("magazine_count", 0) + cleaned_data.get("book_count", 0)
        if item_total > 100:
            self.add_error(None, "The total number of items must be 100 or less.")

    magazine_count = forms.IntegerField(min_value=0, max_value=80, widget=forms.NumberInput(attrs={"placeholder" : "Number of Magazines"}))
    book_count = forms.IntegerField(min_value=0, max_value=50, widget=forms.NumberInput(attrs={"placeholder": "Number of Books"}))
    send_confirmation = forms.BooleanField(required=False)
    email = forms.EmailField(required=False, validators=[validate_email_domain], widget=forms.EmailInput(attrs={"placeholder": "Your company email address"}))


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ("date_edited", "book")

    rating = forms.IntegerField(min_value=0, max_value=5)