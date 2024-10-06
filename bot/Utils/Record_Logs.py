from datetime import datetime


class RecordLogs:
    @staticmethod
    def log_admin_action(user_id: int, admin_action: str):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('admin_logs.txt', 'a') as f:
            f.write(f"{current_time} - Администратор {user_id} {admin_action}\n")

    @staticmethod
    def log_user_action(user_id: int, user_action: str):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('user_logs.txt', 'a') as f:
            f.write(f"{current_time} - пользователь {user_id} {user_action}\n")
