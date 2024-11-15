from django.db import models


class VotosCandidatos(models.Model):
    nome = models.CharField(max_length=255)
    votos = models.IntegerField(default=0)
    sessao = models.CharField(max_length=4)
    zona = models.CharField(max_length=3)

    def __str__(self):
        return f'{self.nome}'
