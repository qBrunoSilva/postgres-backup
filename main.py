import subprocess
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

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

    def send_notify(self, subject, body):
        sendMail = SendMail()
        sendMail.send_mail(subject, body)

    def verify_and_crate_folder(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def remove_folder(self, dir):
        if os.path.exists(dir):
            shutil.rmtree(dir)

    def save_log(self, log_text):
        print(log_text)

        self.verify_and_crate_folder("./logs")

        with open(f'./logs/logs.txt', 'a') as f:
            f.writelines(f'{time.strftime("%d/%m/%Y")} - {log_text}\n')

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
            s3 = SendS3()
            upload_success = s3.upload_file(f'{folder_name}/{self.file_name}')

            if not upload_success:
                self.send_notify(
                    subject='Backup database error', body=f"""
                                    <div>
                                        <p style="font-size: 14px; margin:0">[OK] Backup <b>{folder_name}/{self.file_name}</b> generated successful</p>
                                        <p style="color: red; font-size: 14px; margin:0">[FAIL] Uploading file <b>{self.file_name}</b> to S3</p>
                                    </div>
                                    """)
                self.save_log(
                    f"""[WARNING] Success to backing up database {self.database_name} more don't upload to S3. Administrator has be notified by email at {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}""")

            self.save_log(
                f'[OK] Backing up database {self.database_name} finished at {datetime.now().strftime("%d/%m/%Y - %H:%M:%S")}')
            self.remove_folder(f'{self.database_backup_dir}/{folder_name}')
        else:
            self.send_notify(subject="Backup database error",
                             body=f"""
                            <div>
                                <p style="color: red; font-size: 14px; margin:0">[FAIL] Backup <b>{folder_name}/{self.file_name}</b> generated</p>
                                <p style="color: red; font-size: 14px; margin:0">[FAIL] Uploading file <b>{self.file_name}</b> to S3</p>
                            </div>
                            """)

            self.save_log(
                f'[FAIL] Backing failed at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')


if (__name__ == "__main__"):
    backup = BackupDB()
    backup.create_backup()
