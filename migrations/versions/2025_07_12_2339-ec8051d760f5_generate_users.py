"""generate users

Revision ID: ec8051d760f5
Revises: f332b138f4bb
Create Date: 2025-07-12 23:39:04.212662

"""
from typing import Union, Sequence
import sqlalchemy as sa
from alembic import op
from sqlalchemy import bindparam, union
from sqlalchemy.sql import text
from settings import settings # revision identifiers, used by Alembic.


# revision identifiers, used by Alembic.
revision: str = 'ec8051d760f5'
down_revision: Union[str, None] = 'f332b138f4bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(text("""
                WITH new_users AS (
                    INSERT INTO users (full_name, email, password_hash, role)
                    VALUES
                        ('test_user', 'test@mail.com', :hash1, 'USER'),
                        ('admin_user', 'admin@mail.com', :hash2, 'ADMIN')
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id, email
                )
                INSERT INTO accounts (user_id, balance)
                SELECT
                    nu.id,
                    0.00
                FROM new_users nu
                WHERE nu.email = 'test@mail.com'
            """).bindparams(bindparam("hash1", value=settings.test_user_password),
                            bindparam("hash2", value=settings.admin_user_password), ))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(text("""
               WITH user_ids AS(
                    SELECT id FROM users
                    WHERE email IN ('test@mail.com', 'admin@mail.com')
               ),
               delete_transactions AS (
                    DELETE FROM transactions
                    WHERE user_id IN (SELECT id FROM user_ids)
                ),
               delete_refreshtokens AS (
                    DELETE FROM refreshtokens
                    WHERE user_id IN (SELECT id FROM user_ids)
               ),
               delete_revokedtokens AS (
                    DELETE FROM revokedtokens
                    WHERE user_id IN (SELECT id FROM user_ids)
               ),
               delete_accounts AS (
                    DELETE FROM accounts 
                    WHERE user_id IN (SELECT id FROM user_ids)
               ),
               deleted_users AS (
                    DELETE FROM users
                    WHERE id IN (SELECT id FROM user_ids)
                    RETURNING id
               )
               SELECT 1;
            """))

