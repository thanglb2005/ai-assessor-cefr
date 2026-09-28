import pytest

from aicefr.auth.service import ResourceNotFound, authorize_owner
from aicefr.contracts import Actor, ActorRole


def test_owner_check_does_not_reveal_foreign_or_missing_record():
    actor = Actor(actor_id="fixture-owner", role=ActorRole.STUDENT)
    authorize_owner(actor, "fixture-owner")
    with pytest.raises(ResourceNotFound) as missing:
        authorize_owner(actor, None)
    with pytest.raises(ResourceNotFound) as foreign:
        authorize_owner(actor, "fixture-other")
    assert str(missing.value) == str(foreign.value)
