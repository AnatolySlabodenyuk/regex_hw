import csv
import re
from functools import wraps
from datetime import datetime


def logger(path):
    def __logger(old_function):
        @wraps(old_function)
        def new_function(*args, **kwargs):
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            old_function_name = old_function.__name__
            result = old_function(*args, **kwargs)

            log_entry = (
                f"{date_now} | "
                f"Имя функции: {old_function_name} | "
                f"Аргументы: {args} {kwargs} | "
                f"Возвращено: {result}\n"
            )

            with open(path, mode='a', encoding='utf-8') as f:
                f.write(log_entry)

            return result

        return new_function

    return __logger


@logger("log.log")
def process_full_name(contacts_list):
    """
    Функция приводит ФИО к нужному виду
    """
    update_full_name_list = []
    for contact in contacts_list:
        full_name_list = contact[:3]
        current_full_name_list = ' '.join(full_name_list).strip().split()

        while len(current_full_name_list) < 3:
            current_full_name_list.append("")

        update_full_name_list.append(current_full_name_list + contact[3:])

    return update_full_name_list


@logger("log.log")
def process_phone_number(contacts_list, subst=r"+7(\2)\3-\4-\5 \6\7"):
    """
    Функция приводит номер к нужному виду согласно шаблону
    """
    update_phone_number_list = []
    regex = r"(\+7|8)\s*\(?(\d{3})\)?[-\s]?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})\s*\(?(доб.)?\s*(\d{4})?\)?"

    for contact in contacts_list:
        phone_number_raw = contact[5].strip()
        if phone_number_raw:
            current_phone_number = re.sub(regex, subst, phone_number_raw).strip()
            contact[5] = current_phone_number

        update_phone_number_list.append(contact)

    return update_phone_number_list


@logger("log.log")
def merge_duplicates(contacts_list):
    """
    Функция объединяет дубликаты в одну запись
    """
    contacts_dict = {}

    for contact in contacts_list:
        full_name = tuple(contact[:3])

        if full_name in contacts_dict:
            existing_contact = contacts_dict[full_name]
            for i in range(len(contact)):
                if contact[i].strip():
                    existing_contact[i] = contact[i].strip()
        else:
            contacts_dict[full_name] = contact[:]

    return list(contacts_dict.values())


if __name__ == '__main__':
    with open("phonebook_raw.csv", encoding="utf-8") as f:
        rows = csv.reader(f, delimiter=",")
        header = next(rows)
        contacts_list = list(rows)

    contacts_list = process_full_name(contacts_list)
    contacts_list = process_phone_number(contacts_list)
    contacts_list = merge_duplicates(contacts_list)

    with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerow(header)
        datawriter.writerows(contacts_list)
