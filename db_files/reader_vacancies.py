import csv


class VacanciesReader:
    def __init__(self, name_csv_file, **kwargs):
        self.__name_csv_file = name_csv_file
        self.__vacancies = []
        self.__count = 0
        self.__set_vacancies()

    def __set_vacancies(self):
        with open(self.__name_csv_file, encoding='utf-8') as file:
            file_reader = csv.reader(file, delimiter=',')
            for row in file_reader:
                if self.__count != 0 and len(row) > 0:
                    self.__vacancies.append({'title': row[0],
                                             'company': row[1],
                                             'location': row[2],
                                             'link': row[3],
                                             'salary': 666})
                self.__count += 1

    @property
    def get_vacancies(self):
        return self.__vacancies

    @property
    def get_count_vacancies(self):
        return self.__count
