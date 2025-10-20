from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        """Soft delete all objects in the queryset"""
        return self.update(is_deleted=True)

    def hard_delete(self):
        """Permanently delete all objects in the queryset"""
        return super().delete()

    def alive(self):
        """Return only non-deleted objects"""
        return self.filter(is_deleted=False)

    def dead(self):
        """Return only deleted objects"""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        """기본적으로 삭제되지 않은 객체만 반환"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        """삭제된 객체를 포함한 모든 객체 반환"""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """삭제된 객체만 반환"""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # 기본 매니저 (삭제된 것 포함)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def delete(self, using=None, keep_parents=False):
        """Override delete method to perform soft delete by default"""
        self.soft_delete()

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object"""
        super().delete(using=using, keep_parents=keep_parents)
