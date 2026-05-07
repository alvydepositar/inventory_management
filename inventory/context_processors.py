from .access import get_access_context, scope_branches_queryset


def stock_branches(request):
    access = get_access_context(request)
    role = access.role
    return {
        'sidebar_branches': scope_branches_queryset(request),
        'current_role': role,
        'is_admin_role': role == 'admin',
        'is_branch_manager_role': role == 'branch_manager',
        'is_user_role': role == 'user',
        'assigned_branch_id': access.assigned_branch_id,
        'can_manage_users': role == 'admin',
        'can_manage_branch_records': role == 'admin',
        'can_manage_reference_records': role in {'admin', 'branch_manager'},
        'can_delete_reference_records': role == 'admin',
        'can_view_all_branches_reports': role == 'admin',
        'can_record_stock_actions': role in {'admin', 'branch_manager', 'user'},
        'can_correct_stock_actions': role in {'admin', 'branch_manager'},
    }
