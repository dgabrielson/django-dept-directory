# django-dept-directory

Provides display information for directories.

Defines:
- `ContactInfoType`
- `Address`
- `PhoneNumber`
- `EmailAddress`
- `PersonType`
- `Person`
- `Location`


**TODO**: consider making the localflavor field specific.    
http://docs.djangoproject.com/en/dev/ref/contrib/localflavor/#canada-ca
```
from django.contrib.localflavor.ca.forms import CAPhoneNumberField

DIRECTORY_LOCALFLAVOR_PHONE = 'django.contrib.localflavor.ca.forms.CAPhoneNumberField'
DIRECTORY_LOCALFLAVOR_REGION = 'django.contrib.localflavor.ca.forms.CAProvinceSelect'
DIRECTORY_LOCALFLAVOR_POSTALCODE = 'django.contrib.localflavor.ca.forms.CAPostalCodeField'
```

## For Canada (ca)

`class ca.forms.CAPhoneNumberField`

    A form field that validates input as a Canadian phone number, with the format XXX-XXX-XXXX.

`class ca.forms.CAPostalCodeField`

    A form field that validates input as a Canadian postal code, with the format XXX XXX.

`class ca.forms.CAProvinceField`

    A form field that validates input as a Canadian province name or abbreviation.

`class ca.forms.CASocialInsuranceNumberField`

    A form field that validates input as a Canadian Social Insurance Number (SIN). A valid number must have the format XXX-XXX-XXX and pass a Luhn mod-10 checksum.

`class ca.forms.CAProvinceSelect`

    A Select widget that uses a list of Canadian provinces and territories as its choices.
