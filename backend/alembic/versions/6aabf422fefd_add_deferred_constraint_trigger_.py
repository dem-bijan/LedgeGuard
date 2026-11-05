"""add deferred constraint trigger enforcing ledger balance

Revision ID: 6aabf422fefd
Revises: 5b86d3edfe5f
Create Date: 2026-11-05 21:31:17.231892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6aabf422fefd'
down_revision: Union[str, Sequence[str], None] = '5b86d3edfe5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_transaction_balance()
        RETURNS TRIGGER AS $$
        DECLARE
            affected_transaction_id UUID;
            total NUMERIC;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                affected_transaction_id := OLD.transaction_id;
            ELSE
                affected_transaction_id := NEW.transaction_id;
            END IF;

            SELECT COALESCE(SUM(amount), 0) INTO total
            FROM ledger_entries
            WHERE transaction_id = affected_transaction_id;

            IF total != 0 THEN
                RAISE EXCEPTION
                    'Transaction % is not balanced: entries sum to %, expected 0',
                    affected_transaction_id, total;
            END IF;

            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER enforce_transaction_balance
        AFTER INSERT OR UPDATE OR DELETE ON ledger_entries
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION check_transaction_balance();
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS enforce_transaction_balance ON ledger_entries;")
    op.execute("DROP FUNCTION IF EXISTS check_transaction_balance();")
