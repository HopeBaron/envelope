from typing_extensions import Self
from django.db import models
from django.utils import timezone
from django.contrib.auth import models as auth_models

class Entity(models.Model):
    create_date = models.DateTimeField(default=timezone.now)
    delete_date = models.DateTimeField(null=True)

    def _soft_delete(self):
        self.delete_date = timezone.now()
        self.save()

    class Meta:
        abstract = True


class UserManager(auth_models.BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class User(auth_models.AbstractBaseUser, Entity):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=360)
    USERNAME_FIELD = 'username'
    objects = UserManager()

    @property
    def memberships(self):
        return Membership.objects.filter(user_id=self.id)

    def join(self, chat):
        return Membership.objects.create(chat_id=chat.id, user_id=self.id)


class Chat(Entity):
    users = models.ManyToManyField(
        User, through="Membership", through_fields=("chat", "user"))

    @property
    def messages(self):
        return Message.objects.filter(chat_id=self.id)

    @property
    def memberships(self):
        return Membership.objects.filter(chat_id=self.id)


class Message (Entity):
    author = models.ForeignKey(User, models.CASCADE)
    chat = models.ForeignKey(Chat, models.CASCADE)
    content = models.TextField()


class Membership(Entity):
    user = models.ForeignKey(User, models.CASCADE)
    chat = models.ForeignKey(Chat, models.CASCADE)

    class Meta:
        unique_together = ("user", "chat")

    def add(self, user: User):
        return Membership.objects.create(chat=self.chat, user=user)

    def revoke(self, member: Self):
        member._soft_delete()

    def revoke(self):
        self._soft_delete()
