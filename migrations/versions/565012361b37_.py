"""empty message

Revision ID: 565012361b37
Revises: d06c64b9a04b
Create Date: 2023-05-21 09:56:54.203300

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '565012361b37'
down_revision = 'd06c64b9a04b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attendance', sa.Column('editId', sa.String(length=20), nullable=True, comment='上次修改者ID/在生成考勤记录的定时函数中将此ID赋予一个默认值'))
    op.add_column('attendance', sa.Column('editTime', sa.DateTime(), nullable=True, comment='上次保存数据库的时间'))
    op.alter_column('staff_information', 'staffCheckState',
               existing_type=mysql.INTEGER(),
               comment='今日尚未出勤：0  出勤：{今日出勤（工作中）：10  今日出勤（临时外出）16 , 今日出差：11 ,  今日休假： 12  , 加班出勤（工作中）： 13 ,  今日出勤（已完成工作） 14  加班出勤（已完成工作）15 } ;   缺勤：{今日缺勤：20 , 今日迟到（工作中）：21 ;  今日出勤|早退：22; 今日迟到（未出勤）23  今日迟到|早退 24  今日迟到（临时外出）25  今日迟到（已完成工作）26   今日加班缺勤：30  ;  今日加班迟到（工作中）：31  ; 今日加班迟到（未出勤）32 ;  }',
               existing_comment='今日尚未出勤：0  出勤：{今日出勤（工作中）：10 , 今日出差：11 ,  今日休假： 12  , 加班出勤（工作中）： 13 ,  今日出勤（已完成工作） 14  加班出勤（已完成工作）15 } ;   缺勤：{今日缺勤：20 , 今日迟到（工作中）：21 ;  今日早退：22; 今日迟到（未出勤）27  今日迟到|早退 28   今日迟到（已完成工作）29   今日加班缺勤：23  ;  今日加班迟到（工作中）： 24 ; 今日加班迟到（未出勤）30 ;  }',
               existing_nullable=True,
               existing_server_default=sa.text("'0'"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('staff_information', 'staffCheckState',
               existing_type=mysql.INTEGER(),
               comment='今日尚未出勤：0  出勤：{今日出勤（工作中）：10 , 今日出差：11 ,  今日休假： 12  , 加班出勤（工作中）： 13 ,  今日出勤（已完成工作） 14  加班出勤（已完成工作）15 } ;   缺勤：{今日缺勤：20 , 今日迟到（工作中）：21 ;  今日早退：22; 今日迟到（未出勤）27  今日迟到|早退 28   今日迟到（已完成工作）29   今日加班缺勤：23  ;  今日加班迟到（工作中）： 24 ; 今日加班迟到（未出勤）30 ;  }',
               existing_comment='今日尚未出勤：0  出勤：{今日出勤（工作中）：10  今日出勤（临时外出）16 , 今日出差：11 ,  今日休假： 12  , 加班出勤（工作中）： 13 ,  今日出勤（已完成工作） 14  加班出勤（已完成工作）15 } ;   缺勤：{今日缺勤：20 , 今日迟到（工作中）：21 ;  今日出勤|早退：22; 今日迟到（未出勤）23  今日迟到|早退 24  今日迟到（临时外出）25  今日迟到（已完成工作）26   今日加班缺勤：30  ;  今日加班迟到（工作中）：31  ; 今日加班迟到（未出勤）32 ;  }',
               existing_nullable=True,
               existing_server_default=sa.text("'0'"))
    op.drop_column('attendance', 'editTime')
    op.drop_column('attendance', 'editId')
    # ### end Alembic commands ###
