from random import randint

from django.db import transaction
from django.utils import timezone

from .models import (
    Products,
    StockConversion,
    StockConversionInput,
    StockLevel,
    StockMovement,
)


def _generate_stock_movement_id() -> str:
    for _ in range(20):
        ts = timezone.now().strftime('%Y%m%d%H%M%S')
        suffix = f"{randint(0, 999):03d}"
        value = f"SM-{ts}{suffix}"
        if not StockMovement.objects.filter(transaction_id=value).exists():
            return value
    raise ValueError('Unable to generate a unique transaction reference.')


def _normalize_conversion_inputs(inputs):
    normalized = []
    seen_product_ids = set()

    for row in inputs or []:
        input_product = row.get('input_product') if isinstance(row, dict) else None
        quantity_used = row.get('quantity_used') if isinstance(row, dict) else None

        if isinstance(input_product, Products):
            product = input_product
        else:
            try:
                product_id = int(input_product)
            except (TypeError, ValueError):
                product_id = None
            product = Products.objects.filter(pk=product_id).first() if product_id else None

        if not product:
            raise ValueError('Each input row must include a valid input product.')

        try:
            qty = int(quantity_used)
        except (TypeError, ValueError):
            qty = 0
        if qty <= 0:
            raise ValueError('Each input quantity must be greater than zero.')

        if product.id in seen_product_ids:
            raise ValueError('Input products must not be duplicated.')

        seen_product_ids.add(product.id)
        normalized.append((product, qty))

    if not normalized:
        raise ValueError('At least one input product is required.')

    return normalized


def _build_conversion_movement_remarks(conversion, direction, output_product, remarks):
    ref = f"Conversion #{conversion.id}"
    if direction == 'OUT':
        base = f"{ref}: Used for mixing into {output_product.product_name}."
    else:
        base = f"{ref}: Produced from mixing."
    return f"{base} {remarks}".strip() if remarks else base


def create_stock_conversion(branch, inputs, output_product, output_quantity, user, remarks=''):
    if not branch:
        raise ValueError('Branch is required.')
    if not output_product:
        raise ValueError('Output product is required.')

    try:
        output_qty = int(output_quantity)
    except (TypeError, ValueError):
        output_qty = 0
    if output_qty <= 0:
        raise ValueError('Output quantity must be greater than zero.')

    normalized_inputs = _normalize_conversion_inputs(inputs)

    with transaction.atomic():
        product_ids = {product.id for product, _ in normalized_inputs}
        product_ids.add(output_product.id)

        locked_levels = {
            level.product_id: level
            for level in StockLevel.objects.select_for_update().filter(
                branch=branch,
                product_id__in=product_ids,
            )
        }

        output_level = locked_levels.get(output_product.id)
        if output_level is None:
            output_level, _ = StockLevel.objects.select_for_update().get_or_create(
                branch=branch,
                product=output_product,
                defaults={'quantity': 0},
            )
            locked_levels[output_product.id] = output_level

        for product, qty in normalized_inputs:
            level = locked_levels.get(product.id)
            available = level.quantity if level else 0
            if available < qty:
                raise ValueError(
                    f'Insufficient stock for {product.product_name}. '
                    f'Available: {available}, required: {qty}.'
                )

        conversion = StockConversion.objects.create(
            branch=branch,
            output_product=output_product,
            output_quantity=output_qty,
            remarks=remarks or '',
            created_by=user,
            handled_by=user,
        )

        input_rows = []
        movement_rows = []

        for product, qty in normalized_inputs:
            level = locked_levels[product.id]
            balance_before = level.quantity
            balance_after = balance_before - qty
            level.quantity = balance_after
            level.save(update_fields=['quantity', 'last_updated'])

            input_rows.append(
                StockConversionInput(
                    conversion=conversion,
                    input_product=product,
                    quantity_used=qty,
                )
            )
            movement_rows.append(
                StockMovement(
                    transaction_id=_generate_stock_movement_id(),
                    transaction_type='MIX_OUT',
                    branch=branch,
                    product=product,
                    quantity=qty,
                    remarks=_build_conversion_movement_remarks(
                        conversion,
                        'OUT',
                        output_product,
                        remarks,
                    ),
                    handled_by=user,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    conversion=conversion,
                )
            )

        output_balance_before = output_level.quantity
        output_balance_after = output_balance_before + output_qty
        output_level.quantity = output_balance_after
        output_level.save(update_fields=['quantity', 'last_updated'])

        movement_rows.append(
            StockMovement(
                transaction_id=_generate_stock_movement_id(),
                transaction_type='MIX_IN',
                branch=branch,
                product=output_product,
                quantity=output_qty,
                remarks=_build_conversion_movement_remarks(
                    conversion,
                    'IN',
                    output_product,
                    remarks,
                ),
                handled_by=user,
                balance_before=output_balance_before,
                balance_after=output_balance_after,
                conversion=conversion,
            )
        )

        StockConversionInput.objects.bulk_create(input_rows)
        StockMovement.objects.bulk_create(movement_rows)

    return conversion
