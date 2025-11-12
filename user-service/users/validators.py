import re
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, errors, message="Validation failed"):
        self.errors = errors
        self.message = message
        super().__init__(self.message)


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_uuid(uuid_string, field_name="id"):
        """
        Validate UUID format
        Raises ValidationError if invalid
        """
        if not uuid_string:
            raise ValidationError(
                errors={field_name: "This field is required"},
                message=f"Invalid {field_name}"
            )
        
        try:
            uuid.UUID(str(uuid_string))
            return True
        except (ValueError, AttributeError, TypeError):
            raise ValidationError(
                errors={field_name: f"Invalid UUID format: {uuid_string}"},
                message=f"Invalid {field_name}"
            )
    
    @staticmethod
    def validate_email(email):
        """
        Validate email format
        Raises ValidationError if invalid
        """
        if not email:
            raise ValidationError(
                errors={'email': "This field is required"},
                message="Invalid email"
            )
        
        if not isinstance(email, str):
            raise ValidationError(
                errors={'email': "Must be a string"},
                message="Invalid email"
            )
        
        email = email.strip()
        
        if not email:
            raise ValidationError(
                errors={'email': "This field cannot be empty"},
                message="Invalid email"
            )
        
        # Check length
        if len(email) > 254:  # RFC 5321
            raise ValidationError(
                errors={'email': "Email address is too long (max 254 characters)"},
                message="Invalid email"
            )
        
        # Use Django's email validator
        try:
            django_validate_email(email)
        except ValidationError as e:
            raise ValidationError(
                errors={'email': "Invalid email format"},
                message="Invalid email"
            )
        
        # Additional checks
        if email.count('@') != 1:
            raise ValidationError(
                errors={'email': "Email must contain exactly one @ symbol"},
                message="Invalid email"
            )
        
        local, domain = email.rsplit('@', 1)
        
        if not local or not domain:
            raise ValidationError(
                errors={'email': "Invalid email format"},
                message="Invalid email"
            )
        
        if domain.count('.') < 1:
            raise ValidationError(
                errors={'email': "Invalid domain in email address"},
                message="Invalid email"
            )
        
        return email.lower()
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        Requirements:
        - At least 8 characters
        - Contains uppercase and lowercase
        - Contains at least one number
        - Contains at least one special character
        """
        if not password:
            raise ValidationError(
                errors={'password': "This field is required"},
                message="Invalid password"
            )
        
        if not isinstance(password, str):
            raise ValidationError(
                errors={'password': "Must be a string"},
                message="Invalid password"
            )
        
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if len(password) > 128:
            errors.append("Password is too long (max 128 characters)")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        if errors:
            raise ValidationError(
                errors={'password': errors},
                message="Password does not meet requirements"
            )
        
        return True
    
    @staticmethod
    def validate_name(name, field_name="name", min_length=1, max_length=255, required=True):
        """
        Validate name field
        """
        if not name:
            if required:
                raise ValidationError(
                    errors={field_name: "This field is required"},
                    message=f"Invalid {field_name}"
                )
            return ""
        
        if not isinstance(name, str):
            raise ValidationError(
                errors={field_name: "Must be a string"},
                message=f"Invalid {field_name}"
            )
        
        name = name.strip()
        
        if required and not name:
            raise ValidationError(
                errors={field_name: "This field cannot be empty"},
                message=f"Invalid {field_name}"
            )
        
        if len(name) < min_length:
            raise ValidationError(
                errors={field_name: f"Must be at least {min_length} characters long"},
                message=f"Invalid {field_name}"
            )
        
        if len(name) > max_length:
            raise ValidationError(
                errors={field_name: f"Must not exceed {max_length} characters"},
                message=f"Invalid {field_name}"
            )
        
        # Check for invalid characters (optional)
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            raise ValidationError(
                errors={field_name: "Contains invalid characters (only letters, spaces, hyphens, and apostrophes allowed)"},
                message=f"Invalid {field_name}"
            )
        
        return name
    
    @staticmethod
    def validate_push_token(push_token, required=False):
        """
        Validate FCM push token
        """
        if not push_token:
            if required:
                raise ValidationError(
                    errors={'push_token': "This field is required"},
                    message="Invalid push token"
                )
            return None
        
        if not isinstance(push_token, str):
            raise ValidationError(
                errors={'push_token': "Must be a string"},
                message="Invalid push token"
            )
        
        push_token = push_token.strip()
        
        if required and not push_token:
            raise ValidationError(
                errors={'push_token': "This field cannot be empty"},
                message="Invalid push token"
            )
        
        if len(push_token) > 512:
            raise ValidationError(
                errors={'push_token': "Token is too long (max 512 characters)"},
                message="Invalid push token"
            )
        
        # Basic FCM token format validation (alphanumeric, hyphens, underscores, colons)
        if not re.match(r'^[a-zA-Z0-9_:-]+$', push_token):
            raise ValidationError(
                errors={'push_token': "Invalid token format (only alphanumeric characters, hyphens, underscores, and colons allowed)"},
                message="Invalid push token"
            )
        
        return push_token
    
    @staticmethod
    def validate_preferences(email_pref=None, push_pref=None):
        """
        Validate preferences values
        """
        errors = {}
        
        if email_pref is not None and not isinstance(email_pref, bool):
            errors['email'] = f"Must be a boolean value, got {type(email_pref).__name__}"
        
        if push_pref is not None and not isinstance(push_pref, bool):
            errors['push'] = f"Must be a boolean value, got {type(push_pref).__name__}"
        
        if errors:
            raise ValidationError(
                errors=errors,
                message="Invalid preferences"
            )
        
        if email_pref is None and push_pref is None:
            raise ValidationError(
                errors={'preferences': "At least one preference (email or push) must be provided"},
                message="Invalid preferences"
            )
        
        return True