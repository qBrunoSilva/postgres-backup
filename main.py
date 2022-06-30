import os
import shutil
import subprocess
from datetime import datetime

from dotenv import load_dotenv

from modules.discord_message import DiscordBot
from modules.send_mail import SendMail
from modules.send_s3 import SendS3

load_dotenv()

time = datetime.now()
folder_name = time.strftime("%d-%m-%Y")


class BackupDB():
    def __init__(self) -> None:
        self.database_name = os.environ.get("DATABASE")
        self.database_user = os.environ.get("POSTGRES_USER")
        self.database_password = os.environ.get("POSTGRES_PASSWORD")
        self.database_backup_dir = os.environ.get("BACKUP_DIR")  # /backup/

        os.putenv('PGPASSWORD', self.database_password)

        self.file_name = f'{self.database_name}_{time.strftime("%d-%m-%Y-%H-%M")}.sql'

    def send_email_notify(self, subject, body):
        sendMail = SendMail()
        sendMail.send_mail(subject, body)

    def send_discord_message(self, message, message_type: str):
        bot = DiscordBot()
        if message_type == 'success':
            bot.send_success_message(message)

        if message_type == 'warning':
            bot.send_warning_message(message)

        if message_type == 'error':
            bot.send_fail_message(message)

    def verify_and_crate_folder(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def remove_folder_and_zip_file(self, dir):
        if os.path.exists(dir):
            shutil.rmtree(dir)

        if os.path.isfile(f'{dir}.zip'):
            os.remove(f'{dir}.zip')

    def save_log(self, log_text, message_type: str):
        self.send_discord_message(log_text, message_type)
        self.verify_and_crate_folder("./logs")

        print(log_text)

        with open(f'./logs/logs.txt', 'a') as f:
            f.writelines(f'{time.strftime("%d/%m/%Y")} - {log_text}\n')

    def create_zip_file(self, dir):
        print(f'Creating zip file {dir}.zip')
        shutil.make_archive(f'{dir}', 'zip', dir)
        print(f'Zip file {dir}.zip created')

        return f'{dir}.zip'

    def create_backup(self):
        self.verify_and_crate_folder(self.database_backup_dir)
        self.verify_and_crate_folder(
            f'{self.database_backup_dir}/{folder_name}')

        print(
            f'Backing up database {self.database_name} started at {datetime.now().strftime("%d/%m/%Y/ - %H:%M:%S")}')

        command = f'pg_dump -U {self.database_user} -h localhost -f {self.database_backup_dir}/{folder_name}/{self.file_name} {self.database_name}'

        print(f"Executing command: {command}")

        result = subprocess.call(command, shell=True)

        if result == 0:
            self.create_zip_file(f"{self.database_backup_dir}/{folder_name}")
            s3 = SendS3()

            upload_success = s3.upload_file(
                f'{folder_name}.zip')

            if not upload_success:
                self.send_email_notify(
                    subject='Backup database error', body=f"""
                                    <div>
                                        <p style="font-size: 14px; margin:0">[OK] Backup <b>{folder_name}/{self.file_name}</b> generated successful</p>
                                        <p style="color: red; font-size: 14px; margin:0">[FAIL] Uploading file <b>{self.file_name}</b> to S3</p>
                                    </div>
                                    """)
                return self.save_log(
                    f"""[WARNING] Success to backing up database {self.database_name} more don't upload to S3. Administrator has be notified by email at {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}""", "warning")

            self.save_log(
                f'[OK] Backing up database {self.database_name} finished at {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}', "success")

            return self.remove_folder_and_zip_file(f'{self.database_backup_dir}/{folder_name}')
        else:
            self.send_email_notify(subject="Backup database error",
                                   body=f"""
                            <div>
                                <p style="color: red; font-size: 14px; margin:0">[FAIL] Backup <b>{folder_name}/{self.file_name}</b> generated</p>
                                <p style="color: red; font-size: 14px; margin:0">[FAIL] Uploading file <b>{self.file_name}</b> to S3</p>
                            </div>
                            """)

            return self.save_log(
                f'[FAIL] Backing failed at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', "error")


if (__name__ == "__main__"):
    backup = BackupDB()
    backup.create_backup()
