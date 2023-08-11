from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations= True

    def create_user(self,username,password= None, **kwargs):

        if not username:
            raise ValueError("Username is required")
        
        user = self.model(username= username, **kwargs)
        user.set_password(password)
        user.save(using= self._db)
        return user
    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff',True )
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_staff') is not True: 
            raise ValueError(("Super user must have is_staff true"))

        return self.create_user(username, password,**extra_fields)


