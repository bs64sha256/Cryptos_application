# импорт модулей
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from hashlib import sha256
from base64 import b64encode
from random import randrange
from time import sleep
from pyperclip import copy

import tkinter as tk
import os

var = 0 # счетчик количества файлов
k = 1.0 # коэффициент строки вставки журнала
log = '' # строка сохранения логов

def main():
    # дочернее окно с логами
    def open_logs():
        global log
        log_list = tk.Toplevel()

        log_list.geometry('500x500+0+0')
        log_list.resizable(False, False)
        log_list.title('Журнал')
        log_list.attributes('-toolwindow', True)
        log_list.attributes('-alpha', 0.9)

        list_logs = ScrolledText(log_list, wrap='word')
        list_logs.pack(expand=True, fill=tk.BOTH)
        list_logs.insert('1.0', log)
        list_logs['state'] = 'disabled'

        log_list.mainloop()
    # копирование логов в буфер обмена
    def copy_text():
        copy(log)

    # преобразование строки пароля в двоичную запись битов
    def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
        bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    # получение полного пути посредством файловых диалогов
    def get_obj():
        if obj_comb.get() == 'Директория':
            path_etr.delete(0, tk.END)
            path = filedialog.askdirectory()
            path_etr.insert(0, path)
        else:
            path_etr.delete(0, tk.END)
            path = filedialog.askopenfilename()
            path_etr.insert(0, path)

    # AES шифрование файла
    def aes_encrypt(file, key):
        global k, log
        import pyAesCrypt
        try:
            key = str(key)
            buffer = 512 * 1024
            pyAesCrypt.encryptFile(str(file), str(file) + '.encrypted', key, buffer)
            os.remove(file)
            logs['state'] = 'normal'
            logs.insert(str(k), f'файл зашифрован - {file}\n')
            logs['state'] = 'disabled'
            log += f'файл зашифрован - {file}\n'
            k += 1.0
            if var == 0: progress_bar['value'] += 100
            else: progress_bar['value'] += 100 / var
        except Exception:
            logs['state'] = 'normal'
            logs.insert(str(k), f'[ОШИБКА] ошибка шифрования файла - {file}\n')
            logs['state'] = 'disabled'
            log += f'[ОШИБКА] ошибка шифрования файла - {file}\n'
            k += 1.0
            if var == 0: progress_bar['value'] += 100
            else: progress_bar['value'] += 100 / var

    # AES расшифровывание файла
    def aes_decrypt(file, key):
        global k, log
        import pyAesCrypt
        try:
            key = str(key)
            buffer = 512 * 1024
            pyAesCrypt.decryptFile(str(file), str(os.path.splitext(file)[0]), key, buffer)
            os.remove(file)
            logs['state'] = 'normal'
            logs.insert(str(k), f'файл дешифрован - {file}\n')
            logs['state'] = 'disabled'
            log += f'файл дешифрован - {file}\n'
            k += 1.0
            if var == 0: progress_bar['value'] += 100
            else: progress_bar['value'] += 100 / var
        except Exception:
            logs['state'] = 'normal'
            logs.insert(str(k), f'[ОШИБКА] ошибка дешифрования файла - {file}\n')
            logs['state'] = 'disabled'
            log += f'[ОШИБКА] ошибка дешифрования файла - {file}\n'
            k += 1.0
            if var == 0: progress_bar['value'] += 100
            else: progress_bar['value'] += 100 / var

    # перечисление всех файлов в директории для шифрования
    def directory_encryption_walk(directory, key):
        global var
        for name in os.listdir(directory):
            path = os.path.join(directory, name)

            if os.path.isfile(path): var += 1
            else: var += 0

            if os.path.isfile(path):
                if alg_comb.get() == 'AES256-CBC': aes_encrypt(path, key)
                else: pass
            else: directory_encryption_walk(path, key)

    # перечисление всех файлов в директории для дешифрования
    def directory_decryption_walk(directory, key):
        global var
        for name in os.listdir(directory):
            path = os.path.join(directory, name)

            if os.path.isfile(path): var += 1
            else: var += 0

            if os.path.isfile(path):
                if alg_comb.get() == 'AES256-CBC': aes_decrypt(path, key)
                else: pass
            else: directory_decryption_walk(path, key)

    # генерация хеш ключа из пароля
    def generate_key(password):
        target = str(hex(int(text_to_bits(str(password)), 2)))
        encoded_target = b64encode(target.encode('ascii'))
        key = sha256(encoded_target).hexdigest()
        return key

    # генерация случайного пароля по алфавиту
    def generate_password():
        pas_etr.delete(0, tk.END)
        elements = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM!@#%*&^()?{}[]|/~'
        target = ''
        for i in range(randrange(12, 16)):
            target += elements[randrange(len(elements))]
        pas_etr.insert(0, target)

    # функция запуска
    def run():
        global k, log, var
        var = 0
        progress_bar['value'] = 0
        sleep(0.5)
        if path_etr.get():
            if pas_etr.get():
                if obj_comb.get() == 'Директория':
                    if progress_bar['value'] > 0: progress_bar['value'] = 0.0

                    if mode_comb.get() == 'Зашифровать': directory_encryption_walk(path_etr.get(), generate_key(pas_etr.get()))
                    else: directory_decryption_walk(path_etr.get(), generate_key(pas_etr.get()))
                else:
                    if progress_bar['value'] > 0: progress_bar['value'] = 0.0

                    if mode_comb.get() == 'Зашифровать': aes_encrypt(path_etr.get(), generate_key(pas_etr.get()))
                    else: aes_decrypt(path_etr.get(), generate_key(pas_etr.get()))
            else:
                logs['state'] = 'normal'
                logs.insert(str(k), '[ОШИБКА] Введите пароль шифрования\n')
                logs['state'] = 'disabled'
                log += '[ОШИБКА] Введите пароль шифрования\n'
                k += 1.0
        else:
            logs['state'] = 'normal'
            logs.insert(str(k), '[ОШИБКА] Введите путь к объекту\n')
            logs['state'] = 'disabled'
            log += '[ОШИБКА] Введите путь к объекту\n'
            k += 1.0

    root = tk.Tk()

    default_alg = tk.StringVar(value='AES256-CBC')
    default_obj = tk.StringVar(value='Директория')
    default_mode = tk.StringVar(value='Зашифровать')

    ttk.Style().theme_use('xpnative')

    root.title('Cryptos application V: 1.0.0 DEMO')
    root.geometry('400x395+50+50')
    root.resizable(False, False)
    # вкладки
    note = ttk.Notebook()
    note.pack(expand=True, fill=tk.BOTH)
    main_frame = ttk.Frame(note)
    main_frame.pack(expand=True, fill=tk.BOTH)
    note.add(main_frame, text='Шифрование/дешифрование')

    # виджеты
    alg_lbl = ttk.Label(main_frame, text='Алгоритм шифрования:')
    alg_lbl.place(x=10, y=10)
    alg_comb = ttk.Combobox(main_frame, values=['AES256-CBC'], width=29, state="readonly", cursor='hand2', textvariable=default_alg)
    alg_comb.place(x=162, y=10)
    obj_lbl = ttk.Label(main_frame, text='Объект шифрования:')
    obj_lbl.place(x=10, y=40)
    obj_comb = ttk.Combobox(main_frame, values=['Директория', 'Файл'], width=31, state="readonly", cursor='hand2', textvariable=default_obj)
    obj_comb.place(x=148, y=40)
    mode_lbl = ttk.Label(main_frame, text='Действие над объектом:')
    mode_lbl.place(x=10, y=70)
    mode_comb = ttk.Combobox(main_frame, values=['Зашифровать', 'Расшифровать'], width=29, state="readonly", cursor='hand2', textvariable=default_mode)
    mode_comb.place(x=162, y=70)
    path_lbl = ttk.Label(main_frame, text='Путь:')
    path_lbl.place(x=10, y=100)
    path_etr = ttk.Entry(main_frame, width=30)
    path_etr.place(x=50, y=100)
    path_btn = ttk.Button(main_frame, text='Выбрать', width=15, cursor='hand2', command=get_obj)
    path_btn.place(x=275, y=100)
    pas_lbl = ttk.Label(main_frame, text='Пароль:')
    pas_lbl.place(x=10, y=130)
    pas_etr = ttk.Entry(main_frame, width=22)
    pas_etr.place(x=70, y=130)
    pas_btn = ttk.Button(main_frame, text='Сгенерировать', width=20, cursor='hand2', command=generate_password)
    pas_btn.place(x=240, y=130)
    start_btn = ttk.Button(main_frame, text='Начать', width=53, cursor='hand2', command=run)
    start_btn.place(x=10, y=160)
    log_lbl = ttk.Label(main_frame, text='Журнал событий:')
    log_lbl.place(x=10, y=190)
    copy_btn = ttk.Button(main_frame, text='Копировать', width=17, cursor='hand2', command=copy_text)
    copy_btn.place(x=120, y=190)
    open_btn = ttk.Button(main_frame, text='Открыть', width=17, cursor='hand2', command=open_logs)
    open_btn.place(x=255, y=190)
    logs = ScrolledText(main_frame, width=40, height=6, wrap='word', state='disabled')
    logs.place(x=10, y=220)
    progress_lbl = ttk.Label(main_frame, text='Прогресс:')
    progress_lbl.place(x=10, y=335)
    progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=310, maximum=100.0)
    progress_bar.place(x=80, y=340)

    root.mainloop()


if __name__ == '__main__':
    main()
