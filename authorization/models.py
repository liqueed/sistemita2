from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

    @property
    def full_name(self):
        if self.last_name and self.first_name:
            return f'{self.last_name} {self.first_name}'
        elif self.first_name:
            return self.first_name
        else:
            return self.username
