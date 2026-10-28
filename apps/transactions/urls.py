
from django.urls import path

from .views import (
    account_balances,
    initialize_accounts,
    transfer_points,
)

urlpatterns = [
    path(
        "initialize/",
        initialize_accounts,
        name="initialize-accounts",
    ),
    path(
        "balances/",
        account_balances,
        name="account-balances",
    ),
    path(
        "transfer/",
        transfer_points,
        name="transfer-points",
    ),
]
