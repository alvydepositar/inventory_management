from .models import Branches


def stock_branches(request):
    return {
        'sidebar_branches': Branches.objects.order_by('name'),
    }
