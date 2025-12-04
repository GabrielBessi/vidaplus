"""Seed usuario admin

Revision ID: 143261191270
Revises: debd81f1df52
Create Date: 2025-12-03 21:21:44.691502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '143261191270'
down_revision = 'debd81f1df52'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        INSERT INTO usuarios (id, nome, email, senha, perfil)
        VALUES (1, 'Administrador', 'adm1@gmail.com', 'scrypt:32768:8:1$40UvnIIG593r6Fbp$e1b1f3283bdee21e9e9e26dbd37792b1fda5785c274ac85c0a082dcec952ac8bcafbb935245826313d1f48ae2c8317480d6f39ef039d63ef5b0e1bcd6916ec55', 'administrador')
    """)
    op.execute("""
        INSERT INTO administradores (id, cpf, data_nascimento, endereco, telefone)
        VALUES (1, '12345678910', '1999-01-01', 'Rua Brasil, 6', '11 99999999')
    """)

def downgrade():
    pass
