from django.db import models
from django.contrib.auth.models import User


class Foo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)

    def __str__(self):
        return f'{self.user.username} | XOF {self.amount} '


ACTIVITY_CHOICES = [
    ('DGE', 'Dir. Générale(DGE)'),
    ('DCF', 'Dir. Financière(DCF)'),
    ('DRH', 'Dir. RH(DRH)'),
    ('DEX', 'Dir. Exploitation(DEX)'),
    ('DET', 'Dir. Technique(DET)'),
    ('DCM', 'Dir. Commerciale(DCM)'),
    ('SMG', 'Moyens Generaux(SMG)'),
    ('FHY', 'fret Hydrocarbure(FHY)'),
    ('FSB', 'fret boisson(FSB)'),
    ('FHP', 'fret huile de palm(FHP)'),
    ('FTC', 'fret conteneurs(FTC)'),
    ('FCS', 'fret canne à sucre(FCS)'),
    ('FDI', 'fret divers(FDI)'),
    ('LEV', 'levage(LEV)'),
    ('LOC', 'location de surfaces(LOC)'),
    ('SDI', 'services divers(SDI)'),
    ('RAV', 'revenus à ventiler(RAV)'),
    ('PAF', 'Prestation Accessoir(PAF)'),
    ('COL', 'fret Colis lourds(COL)'),

]

AGENCY_CHOICES = [
    ('0000', 'Siège'),
    ('0001', 'Abidjan (agence principale)'),
    ('0002', 'Bouaflé'),
    ('0003', 'San-Pedro'),
    ('0007', 'Bouaké'),
    ('0008', 'Yamoussoukro'),
    ('0009', 'Ferké'),
    ('0010', 'Minautores'),

]


class FeeRequest(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)

    activity = models.CharField(choices=ACTIVITY_CHOICES, max_length=3, default='DGE')
    agency = models.CharField(choices=AGENCY_CHOICES, max_length=4, default='0001')
    date = models.DateTimeField()
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.driver} -> {self.activity}'


FEE_LABEL_CHOICES = [
    ('PSE', 'PESAGE'),
    ('PGE', 'PEAGE'),
    ('SBK', 'SEJOUR BOUAKE'),
    ('TXI', 'TAXI'),

]


# juste pour retrouver le prix en fonction du libelle
FEE_LABEL_CHOICES_PRICE = {
    'PSE': 5000,
    'PGE': 10000,
    'SBK': 25000,
    'TXI': 5000,
}


class FeeReason(models.Model):
    label = models.CharField(max_length=3, choices=FEE_LABEL_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0)
    request = models.ForeignKey(FeeRequest, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.label} x{self.quantity}  | {self.get_total_price} FCFA'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.price = FEE_LABEL_CHOICES_PRICE[self.label]
        super(FeeReason, self).save(force_insert, using, update_fields)

    @property
    def get_total_price(self):
        return self.price * self.quantity
