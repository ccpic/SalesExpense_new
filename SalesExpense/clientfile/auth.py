from pandas.core.arrays import integer
from sqlalchemy import create_engine
import pyodbc
import pandas as pd
from anytree import Node, NodeMixin, RenderTree, search
from anytree.exporter import DotExporter
import json

SALES_POS = ["高级地区经理", "销售总监", "大区经理", "地区经理", "大区副总监", "高级大区经理", "区域销售总监", "区域销售副总监"]
UPLOAD_AUTH_POS = ["地区经理", "高级地区经理"]


class Staff(NodeMixin):  # Add Node feature
    def __init__(
        self,
        id: integer,  # eid
        name: str,  # 姓名
        position: str,  # 岗位名称
        oa_account: str,  # OA账号名
        parent: object = None,
        children: object = None,
    ):
        super(Staff, self).__init__()
        self.id = id
        self.name = name
        self.position = position
        self.oa_account = oa_account
        self.parent = parent
        if children:
            self.children = children

    def find_staff(self, attr: str, value):
        return search.find_by_attr(self, name=attr, value=value)

    def get_descendants_list(self, attr: str = "id", pos: list = SALES_POS):
        if self.descendants is None:
            return getattr(self, attr)
        else:
            descendants = [
                getattr(staff, attr)
                for staff in self.descendants
                if (staff.position in pos)
            ]
            descendants.append(getattr(self, attr))
            return descendants


# def get_df_hr() -> pd.DataFrame: # pandas方便，测试用
#     with open('../env.json', 'r') as env:
#         ENV_CONST = json.loads(env)

#     VIEW_TABLE = ENV_CONST["view_table"]

#     conn = pyodbc.connect(
#         driver="{SQL Server}",
#         server=ENV_CONST["server"],
#         database=ENV_CONST["database"],
#         uid=ENV_CONST["uid"],
#         pwd=ENV_CONST["pwd"],
#         unicode_results=True,
#         charset="utf8",
#     )
#     cursor = conn.cursor()

#     sql = "SELECT * FROM %s WHERE [二级部门] in (N'南中国', N'北中国')" % VIEW_TABLE
#     print(sql)
#     cursor.execute(sql)

#     columns = [column[0] for column in cursor.description]
#     df = pd.DataFrame(columns=columns)

#     fetch_lines_per_block = 2000
#     i = 0
#     while True:
#         rows = cursor.fetchmany(fetch_lines_per_block)
#         if len(rows) == 0:
#             break
#         else:
#             rd = [dict(zip(columns, r)) for r in rows]
#             df = df.append(rd, ignore_index=True)
#             del rows
#             del rd
#         i += 1

#     cursor.close()
#     conn.close()

#     return df


def build_staff_tree(ENV_CONST: dict) -> Node:  # 生成组织架构
    all_staffs = get_dict_hr(ENV_CONST)

    ROOT_ID = ENV_CONST["root_id"]
    ROOT_NAME = ENV_CONST["root_name"]
    ROOT_POS = ENV_CONST["root_pos"]
    ROOT_OA = ENV_CONST["root_oa"]

    dict_staffs = {
        n["eid"]: Staff(n["eid"], n["姓名"], n["岗位名称"], n["OA账号"]) for n in all_staffs
    }
    root = dict_staffs[ROOT_ID] = Staff(ROOT_ID, ROOT_NAME, ROOT_POS, ROOT_OA)
    for staff in all_staffs:
        try:
            if (parent_id := staff["直属上级ID"]) is not None:
                dict_staffs[parent_id].children += (dict_staffs[staff["eid"]],)
        except:
            pass

    return root


def get_dict_hr(ENV_CONST: dict) -> dict:

    VIEW_TABLE = ENV_CONST["view_table"]

    conn = pyodbc.connect(
        driver="{SQL Server}",
        server=ENV_CONST["server"],
        database=ENV_CONST["database"],
        uid=ENV_CONST["uid"],
        pwd=ENV_CONST["pwd"],
        unicode_results=True,
        charset="utf8",
    )
    cursor = conn.cursor()

    sql = "SELECT * FROM %s WHERE [二级部门] in (N'南中国', N'北中国')" % VIEW_TABLE
    print(sql)
    cursor.execute(sql)

    columns = [column[0] for column in cursor.description]

    result = []
    for row in cursor.fetchall():
        result.append(dict(zip(columns, row)))

    cursor.close()
    conn.close()

    return result


def get_user_auth(oa_account: str, eid: int) -> tuple:  # 返回一个权限架构下所有姓名的tuple
    with open("./env.json", "r", encoding="utf-8") as env:
        ENV_CONST = json.load(env)
    staff_tree = build_staff_tree(ENV_CONST)  # 组织架构
    staff = staff_tree.find_staff("oa_account", oa_account)
    if staff is not None:  # 如果用户的oa账号在组织架构内
        if staff.id == eid:  # oa必须和eid对应上
            staff_list = staff.get_descendants_list(attr="name")
            if staff.position in UPLOAD_AUTH_POS:  # 如果登录用户的岗位有上传权限
                upload_auth = True
            else:
                upload_auth = False
        else:
            staff_list = []
            upload_auth = False
    else:
        staff_list = []
        upload_auth = False

    return staff_list, upload_auth


if __name__ == "__main__":
    # df = get_df_hr()
    # df = df.loc[:, ["eid", "直属上级id", "姓名"]]
    # print(df["岗位名称"].unique())
    with open("../env.json", "r", encoding="utf-8") as env:
        ENV_CONST = json.load(env)

    staff_tree = build_staff_tree(ENV_CONST)
    user = staff_tree.find_staff("name", "王宝龙")
    print(user.name, user.position, user.oa_account, user.id)
