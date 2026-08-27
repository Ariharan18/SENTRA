"""Create the initial migration baseline.

The domain tables are intentionally deferred to Phase 2 and later.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0001_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Establish the initial migration point."""


def downgrade() -> None:
    """Revert the initial migration point."""
