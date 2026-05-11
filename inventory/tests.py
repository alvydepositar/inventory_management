from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    Branches,
    Brands,
    Categories,
    Products,
    StockConversion,
    StockConversionInput,
    StockLevel,
    StockMovement,
    Suppliers,
    Users,
)


class StockConversionTests(TestCase):
    def setUp(self):
        self.category = Categories.objects.create(name='Paint')
        self.brand = Brands.objects.create(name='ColorSmile')
        self.supplier = Suppliers.objects.create(
            name='Main Supplier',
            contact_person='Sample Contact',
        )
        self.white = Products.objects.create(
            product_id='P-WHITE',
            product_name='White',
            category=self.category,
            brand=self.brand,
            unit_price='100.00',
            supplier=self.supplier,
        )
        self.black = Products.objects.create(
            product_id='P-BLACK',
            product_name='Black',
            category=self.category,
            brand=self.brand,
            unit_price='100.00',
            supplier=self.supplier,
        )
        self.gray = Products.objects.create(
            product_id='P-GRAY',
            product_name='Gray',
            category=self.category,
            brand=self.brand,
            unit_price='100.00',
            supplier=self.supplier,
        )

        self.branch_a = Branches.objects.create(name='Branch A')
        self.branch_b = Branches.objects.create(name='Branch B')

        StockLevel.objects.create(branch=self.branch_a, product=self.white, quantity=100)
        StockLevel.objects.create(branch=self.branch_a, product=self.black, quantity=40)
        StockLevel.objects.create(branch=self.branch_a, product=self.gray, quantity=10)

        StockLevel.objects.create(branch=self.branch_b, product=self.white, quantity=70)
        StockLevel.objects.create(branch=self.branch_b, product=self.black, quantity=50)
        StockLevel.objects.create(branch=self.branch_b, product=self.gray, quantity=5)

        user_model = get_user_model()
        self.branch_user_auth = user_model.objects.create_user(
            username='branch_user',
            email='branch_user@example.com',
            password='password123',
        )
        self.branch_user = Users.objects.create(
            username='branch_user',
            email='branch_user@example.com',
            password='password123',
            user_role='user',
            assigned_branch=self.branch_a,
        )

        self.admin_auth = user_model.objects.create_user(
            username='admin_user',
            email='admin_user@example.com',
            password='password123',
            is_staff=True,
            is_superuser=True,
        )
        self.admin_user = Users.objects.create(
            username='admin_user',
            email='admin_user@example.com',
            password='password123',
            user_role='admin',
        )

        self.url = reverse('add_stock_conversion')

    def _conversion_payload(self, branch_id=None, output_qty=20, white_qty=10, black_qty=5):
        return {
            'branch': str(branch_id or self.branch_a.id),
            'output_product': str(self.gray.id),
            'output_quantity': str(output_qty),
            'remarks': 'Mix test',
            'input_product': [str(self.white.id), str(self.black.id)],
            'quantity_used': [str(white_qty), str(black_qty)],
        }

    def test_successful_conversion_deducts_inputs_and_adds_output(self):
        self.client.force_login(self.branch_user_auth)
        response = self.client.post(self.url, data=self._conversion_payload())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        white_level = StockLevel.objects.get(branch=self.branch_a, product=self.white)
        black_level = StockLevel.objects.get(branch=self.branch_a, product=self.black)
        gray_level = StockLevel.objects.get(branch=self.branch_a, product=self.gray)
        self.assertEqual(white_level.quantity, 90)
        self.assertEqual(black_level.quantity, 35)
        self.assertEqual(gray_level.quantity, 30)

        self.assertEqual(StockConversion.objects.count(), 1)
        conversion = StockConversion.objects.first()
        self.assertEqual(conversion.output_quantity, 20)
        self.assertEqual(StockConversionInput.objects.filter(conversion=conversion).count(), 2)

        self.assertEqual(StockMovement.objects.filter(transaction_type='MIX_OUT').count(), 2)
        self.assertEqual(StockMovement.objects.filter(transaction_type='MIX_IN').count(), 1)

        white_out = StockMovement.objects.get(transaction_type='MIX_OUT', product=self.white)
        black_out = StockMovement.objects.get(transaction_type='MIX_OUT', product=self.black)
        gray_in = StockMovement.objects.get(transaction_type='MIX_IN', product=self.gray)
        self.assertEqual((white_out.balance_before, white_out.balance_after), (100, 90))
        self.assertEqual((black_out.balance_before, black_out.balance_after), (40, 35))
        self.assertEqual((gray_in.balance_before, gray_in.balance_after), (10, 30))

    def test_conversion_fails_if_input_stock_is_insufficient(self):
        self.client.force_login(self.branch_user_auth)
        response = self.client.post(
            self.url,
            data=self._conversion_payload(white_qty=1000),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('Insufficient stock', response.json()['message'])
        self.assertEqual(StockConversion.objects.count(), 0)
        self.assertEqual(StockMovement.objects.filter(transaction_type__in=['MIX_OUT', 'MIX_IN']).count(), 0)

        self.assertEqual(StockLevel.objects.get(branch=self.branch_a, product=self.white).quantity, 100)
        self.assertEqual(StockLevel.objects.get(branch=self.branch_a, product=self.black).quantity, 40)
        self.assertEqual(StockLevel.objects.get(branch=self.branch_a, product=self.gray).quantity, 10)

    def test_conversion_fails_if_input_quantity_is_zero_or_negative(self):
        self.client.force_login(self.branch_user_auth)
        response = self.client.post(
            self.url,
            data=self._conversion_payload(white_qty=0),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('greater than zero', response.json()['message'])
        self.assertEqual(StockConversion.objects.count(), 0)
        self.assertEqual(StockMovement.objects.filter(transaction_type__in=['MIX_OUT', 'MIX_IN']).count(), 0)

    def test_conversion_rolls_back_when_one_input_is_invalid(self):
        self.client.force_login(self.branch_user_auth)
        response = self.client.post(
            self.url,
            data=self._conversion_payload(white_qty=10, black_qty=999),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(StockConversion.objects.count(), 0)
        self.assertEqual(StockMovement.objects.filter(transaction_type__in=['MIX_OUT', 'MIX_IN']).count(), 0)
        self.assertEqual(StockLevel.objects.get(branch=self.branch_a, product=self.white).quantity, 100)
        self.assertEqual(StockLevel.objects.get(branch=self.branch_a, product=self.black).quantity, 40)
        self.assertEqual(StockLevel.objects.get(branch=self.branch_a, product=self.gray).quantity, 10)

    def test_branch_restriction_is_enforced(self):
        self.client.force_login(self.branch_user_auth)
        response = self.client.post(
            self.url,
            data=self._conversion_payload(branch_id=self.branch_b.id),
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])

    def test_admin_can_mix_for_any_branch(self):
        self.client.force_login(self.admin_auth)
        response = self.client.post(
            self.url,
            data=self._conversion_payload(branch_id=self.branch_b.id, output_qty=8, white_qty=4, black_qty=2),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(StockLevel.objects.get(branch=self.branch_b, product=self.white).quantity, 66)
        self.assertEqual(StockLevel.objects.get(branch=self.branch_b, product=self.black).quantity, 48)
        self.assertEqual(StockLevel.objects.get(branch=self.branch_b, product=self.gray).quantity, 13)

    def test_conversion_can_create_new_output_product(self):
        self.client.force_login(self.admin_auth)
        response = self.client.post(
            self.url,
            data={
                'branch': str(self.branch_a.id),
                'create_output_product': '1',
                'new_output_product_id': 'P-GRAY-NEW',
                'new_output_product_name': 'Gray New',
                'new_output_unit_price': '120.50',
                'new_output_low_stock_limit': '5',
                'remarks': 'Create new output product during conversion',
                'output_quantity': '6',
                'input_product': [str(self.white.id), str(self.black.id)],
                'quantity_used': ['2', '1'],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        new_output = Products.objects.get(product_id='P-GRAY-NEW')
        self.assertEqual(new_output.product_name, 'Gray New')
        self.assertEqual(float(new_output.unit_price), 120.50)
        self.assertEqual(new_output.low_stock_limit, 5)

        new_output_level = StockLevel.objects.get(branch=self.branch_a, product=new_output)
        self.assertEqual(new_output_level.quantity, 6)
