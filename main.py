import re
import sys
import csv


header = {'lastname': 0, 'firstname': 1, 'surname': 2, 'organization': 3, 'position': 4, 'phone': 5,
          'email': 6}

def fixing_duplicates(list_) -> list:
    result = []
    dict_name = {}
    for s in list_:
        name = tuple([s[header['lastname']], s[header['firstname']]])
        dict_name[name] = dict_name.get(name, 0) + 1

    # сгруппируем только дубликаты
    dict_temp = {}
    for res in list_:
        name = tuple([res[header['lastname']], res[header['firstname']]])
        if dict_name[name] == 1:
            result.append(res)
            continue
        dict_temp.setdefault(name, []).append(res)

    # для каждой группы объединяем записи по 'surname'
    dict_next = {}
    for _, list_v in dict_temp.items():
        name_ = ''
        for lst in list_v:
            surn = lst[header['surname']]
            if surn and name_ == '':
                name_ = surn
            dict_next.setdefault(surn, []).append(lst)
        if name_:
            lst_ = dict_next.get('', [])
            if lst_:
                dict_next[name_] = dict_next[name_] + lst_
                dict_next.pop('', [])

    # для каждой группы дубликатов — объединяем записи
    for _, list_v in dict_next.items():
        str_ = list_v[0]
        if len(list_v) > 1:
            for s in list_v[1:]:
                for idx in (header['organization'], header['position'], header['phone'], header['email']):
                    if not str_[idx]:
                        str_[idx] = s[idx]
        result.append(str_)
    return result


def read_file(path_file) -> list:
    # читаем адресную книгу в формате CSV в список contacts_list
    try:
        with open(path_file, encoding="utf-8", newline="") as f:
            rows = csv.reader(f, delimiter=",")
            return list(rows)
    except FileNotFoundError:
        return []


def save_file(path_file, data) -> bool:
    # код для записи файла в формате CSV
    try:
        with open(path_file, "w", encoding="utf-8", newline="") as f:
            datawriter = csv.writer(f, delimiter=',')
            datawriter.writerows(data)
            return True
    except Exception:
        return False


def main():
    FILE_READ = 'files/phonebook_raw.csv'
    FILE_WRITE = 'files/phonebook.csv'

    contacts_list = read_file(FILE_READ)
    if not contacts_list:
        return
    # TODO 1: выполните пункты 1-3 ДЗ
    pattern = re.compile(r"(?:\+7|8)\s*"
                         r"\(?(?P<code>\d{3})\)?[-\s]*"
                         r"(?P<section1>\d{3})[-\s]*"
                         r"(?P<section2>\d{2})[-\s]*"
                         r"(?P<section3>\d{2})"
                         r"(?:.*?(?:доб\.|доб)\s*(?P<extension_number>\d{4})\)?)?",
                         flags=re.IGNORECASE)

    for i, image in enumerate(contacts_list[1:], 1):
        full_name = ' '.join([image[header[k]] for k in ('lastname', 'firstname', 'surname')]).strip()
        list_name = full_name.split()
        contacts_list[i][:len(list_name)] = list_name

        phone = image[header['phone']]
        if phone:
            p = pattern.search(phone)
            if p:
                repl = r'+7(\g<code>)\g<section1>-\g<section2>-\g<section3>'
                repl += r' доб.\g<extension_number>' if p.group('extension_number') else ''
                phone = pattern.sub(repl, phone)
                contacts_list[i][header['phone']] = phone
            else:
                contacts_list[i][header['phone']] = ''

    result_list = fixing_duplicates(contacts_list)

    # TODO 2: сохраните получившиеся данные в другой файл
    save_file(FILE_WRITE, result_list)


if __name__ == "__main__":
    main()
    sys.exit(0)
