from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    
    def create_user(self, email, name, password=None, role="patient"):
        if not email:
            raise ValueError("Users must have an email address")
        
        email = self.normalize_email(email)

        from .models import User
        
        # Auto-incrementing hospital ID
        last_user = User.objects.order_by('-id').first()
        next_number = (last_user.id + 1) if last_user else 1
        hospital_id = f"HOSP-{next_number:05d}"

        user = self.model(
            email=email,
            name=name,
            role=role,
            hospital_id=hospital_id
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email=email, name=name, password=password, role="admin")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
