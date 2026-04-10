from Database_Data.Database import init_db, execute_sql, close_db
from Agent.EnvironmentAgent import EnvironmentAgent
from Agent.SqlAgent import SqlAgent
from Agent.TestAgent import TestAgent

def main():
    print("正在连接数据库")
    try:
        init_db(
            host="192.168.200.130",
            port=3306,
            user="root",
            password="root"
        )
    except Exception:
        print("连接失败")
        return
    print("连接成功！输入 SQL 语句执行（输入 quit 退出）\n")
    # try:
    #     while True:
    #         sql = input("mysql> ").strip()
    #         if sql.lower() in ("quit", "exit", "q"):
    #             break
    #         if sql:
    #             result = execute_sql(sql)
    #             print(result)
    # finally:
    #     close_db()


if __name__ == "__main__":
    try:
        main()
        agent = EnvironmentAgent().create_agent()
        result = agent.invoke({"messages": [{"role": "user", "content": "请你只为sql_agent这个数据库更新对应环境文件"}]})
        # agent = SqlAgent().create_agent()
        # result = agent.invoke({"messages": [{"role": "user", "content": """

        # """}]})
        print("Agent 执行结果:\n")
        for msg in result.get("messages", []):
            msg_type = getattr(msg, 'type', None)
            content = getattr(msg, "content", None)
            print(f"[type]: {msg_type}")
            print(f"[content]: {content}")
            print("---")
    finally:
        close_db()    