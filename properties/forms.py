from crispy_forms.bootstrap import AppendedText, InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
from django.forms import ModelForm
from django import forms

from models import Property, Owner, Developer, DeveloperProjects, Project, \
    ProjectPermission, Bank, Permissions


class PermissionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PermissionForm, self).__init__(*args, **kwargs)

        permissions = Permissions.objects.all()
        for permission in permissions:
            self.fields[permission.name] = forms.CharField()

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'permission-form'

    def save(self, *args, **kwargs):
        project = kwargs.pop('project')
        for field in self.fields:
            permission = Permissions.objects.filter(name=field).first()
            p = ProjectPermission(
                project=project,
                permission=permission,
                value=self.cleaned_data[field]
            )
            p.save()
        return project


class ProjectForm(ModelForm):
    add_bank = forms.BooleanField(required=False, label='Add a bank')
    new_bank = forms.CharField(required=False, label='Bank Name')

    class Meta:
        model = Project
        fields = [
            'name',
            'launch_date',
            'possession_date',
            'bank',
            'add_bank',
            'new_bank'
        ]

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'project-form'
        self.fields['bank'].required = False
        self.helper.layout = Layout(
            'name',
            'launch_date',
            'possession_date',
            'bank',
            'add_bank',
            'new_bank',
            # ButtonHolder(
            #     Submit('Submit', 'submit', css_class='btn-block')
            # )
        )

    def save(self, commit=True):
        if 'add_bank' in self.cleaned_data.keys():
            if self.cleaned_data['add_bank'] is True:
                bank = Bank(name=self.cleaned_data['new_bank'])

                project = super(ProjectForm, self).save()
                bank.save()
                project.bank.add(bank)
                return project
        return super(ProjectForm, self).save()


class PropertyBasicDetailsForm(ModelForm):
    developer_name = forms.CharField()

    class Meta:
        model = Property
        fields = [
            'address_line_one',
            'address_line_two',
            'city',
            'state',
            'pin_code']

    def __init__(self, *args, **kwargs):
        super(PropertyBasicDetailsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_tag =False
        self.helper.form_id = 'project-basic-details-form'
        self.fields['address_line_two'].required = False
        self.helper.layout = Layout(
            # 'name',
            'developer_name',
            'address_line_one',
            'address_line_two',
            'city',
            'state',
            'pin_code',
            # 'owner_name',
            ButtonHolder(
                Submit('Submit', 'submit', css_class='btn-block')
            )
        )

    def save(self, commit=True):
        developer_name = self.cleaned_data['developer_name']
        dev, created = Developer.objects.get_or_create(name=developer_name)
        print dev
        self.instance.developer = dev
        return super(PropertyBasicDetailsForm, self).save()


MONTHS = (
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December')
)


class DeveloperProjectForm(ModelForm):
    developer = forms.CharField()

    class Meta:
        model = DeveloperProjects
        fields = [
            'project_name',
            'launch_date_month',
            'launch_date_year',
            'possession_date_month',
            'possession_date_year',
        ]
        widgets = {
            'launch_date_month': forms.Select(choices=MONTHS),
            'possession_date_month': forms.Select(choices=MONTHS),
        }

    def __init__(self, *args, **kwargs):
        super(DeveloperProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'developer-project-form'
        self.helper.layout = Layout(
            'project_name',
            'launch_date_month',
            'launch_date_year',
            'possession_date_month',
            'possession_date_year',
            'developer',
            ButtonHolder(
                Submit('Submit', 'submit', css_class='btn-block')
            )
        )

    def save(self, commit=True):
        developer = self.cleaned_data['developer']
        developer, created = Developer.objects.get_or_create(name=developer)
        self.instance.developer = developer

        return super(DeveloperProjectForm, self).save()


OWNER_CHOICES = ((True, 'Re-Sale'), (False, 'Direct Builder'))


class OwnerForm(ModelForm):
    co_owner_name = forms.CharField()
    co_owner_occupation = forms.CharField()

    class Meta:
        model = Owner
        fields = [
            'name',
            'occupation',
            'pan_number',
            'date_of_purchase',
            'loan_from',
            'cost_of_purchase',
            'is_resale',
            'name_of_seller',
            'contact_number_seller',
            'email_seller',
        ]

        widgets = {
            'is_resale': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super(OwnerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'owner-form'
        self.fields['name_of_seller'].required = False
        self.fields['contact_number_seller'].required = False
        self.fields['email_seller'].required = False
        self.helper.layout = Layout(
            'name',
            'occupation',
            'co_owner_name',
            'co_owner_occupation',
            'pan_number',
            'date_of_purchase',
            'loan_from',
            'cost_of_purchase',
            InlineRadios('is_resale'),
            'name_of_seller',
            'contact_number_seller',
            'email_seller',
            ButtonHolder(
                Submit('owner-details', 'submit', css_class='btn-block',
                       css_id='submit-owner-details')
            )
        )

    def save(self, commit=True):
        co_owner_name = self.cleaned_data['co_owner_name']
        co_owner_occupation = self.cleaned_data['co_owner_occupation']

        co_owner, created = Owner.objects.get_or_create(
            name=co_owner_name,
            occupation=co_owner_occupation
        )

        self.instance.co_owner = co_owner

        return super(OwnerForm, self).save()


BEDROOM_CHOICE = []
for i in range(1, 11):
    BEDROOM_CHOICE.append(tuple((i, i)))

BEDROOM_CHOICE = tuple(BEDROOM_CHOICE)
BATHROOM_CHOICE = BEDROOM_CHOICE


PROPERTY_TYPE_CHOICE =(
    ('Apartment', 'Apartment'),
    ('Town Home','Town Home'),
    ('Single Family House','Single Family House'),
    ('Land','Land'),
)

SPECIFICATION_CHOICE = (
    ('Basic','Basic'),
    ('Premium','Premium'),
    ('Luxury', 'Luxury'),
)

class PropertyForm(ModelForm):
    developer = forms.CharField(label='Builder Name')

    class Meta:
        model = Property
        fields = [
            'property_type',
            'specifications',
            'built_up_area',
            'total_area',
            'number_of_bedrooms',
            'number_of_bathrooms',
            'number_of_parking_spaces',
            'address_line_one',
            'address_line_two',
            'city',
            'state',
            'pin_code',
        ]
        widgets = {
            'number_of_bedrooms': forms.Select(
                choices=BEDROOM_CHOICE, ),
            'number_of_bathrooms': forms.Select(
                choices=BATHROOM_CHOICE),
            'number_of_parking_spaces': forms.Select(
                choices=((1, 1,), (2, 2), ('3+', '3+')), ),
            'developer': forms.TextInput(),
            'property_type': forms.Select(choices=PROPERTY_TYPE_CHOICE),
            'specifications':forms.Select(choices=SPECIFICATION_CHOICE)
        }

    def __init__(self, *args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_tag=False
        self.helper.disable_csrf = True
        self.helper.form_id = 'property-details'
        self.fields['address_line_two'].required = False
        self.helper.layout = Layout(
            'property_type',
            'developer',
            'address_line_one',
            'address_line_two',
            'city',
            'state',
            'pin_code',
            'number_of_bedrooms',
            'number_of_bathrooms',
            'number_of_parking_spaces',
            'specifications',
            AppendedText('built_up_area', 'sq ft'),
            AppendedText('total_area', 'sq ft'),
            ButtonHolder(
                Submit('property-details', 'submit', css_class='btn-block',
                       css_id='submit-property-details')
            )
        )

    def save(self, commit=True):
        developer = self.cleaned_data['developer']
        developer, created = Developer.objects.get_or_create(name=developer)
        self.instance.developer = developer

        return super(PropertyForm, self).save()


class OtherDetailsForm(ModelForm):
    class Meta:
        model = Property
        fields = ['connectivity',
                  'neighborhood_quality',
                  'comments']

    def __init__(self, *args, **kwargs):
        super(OtherDetailsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields['connectivity'].required = False
        self.fields['neighborhood_quality'].required = False
        self.fields['comments'].required = False

        self.helper.layout = Layout(
            'connectivity',
            'neighborhood_quality',
            'comments',
            ButtonHolder(
                Submit('other-details', 'submit', css_class='btn-block',
                       css_id='submit-other-details')
            )
        )
