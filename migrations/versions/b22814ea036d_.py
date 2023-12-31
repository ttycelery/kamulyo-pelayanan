"""empty message

Revision ID: b22814ea036d
Revises: 5bbd804fdbcc
Create Date: 2023-09-30 20:55:04.177091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b22814ea036d'
down_revision = '5bbd804fdbcc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('balasan_tiket', schema=None) as batch_op:
        batch_op.drop_constraint('balasan_tiket_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'tiket', ['tiket_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('tiket_attachment', schema=None) as batch_op:
        batch_op.drop_constraint('tiket_attachment_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'tiket', ['tiket_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tiket_attachment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('tiket_attachment_ibfk_1', 'tiket', ['tiket_id'], ['id'])

    with op.batch_alter_table('balasan_tiket', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('balasan_tiket_ibfk_1', 'tiket', ['tiket_id'], ['id'])

    # ### end Alembic commands ###
