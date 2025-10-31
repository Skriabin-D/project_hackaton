'''
Основной файл, в котором происходит запрос города отправления, города прибытия, а на выход выдаются возможные маршруты
'''
from fast_route import find_shortest_paths

def main():
    depart_town = input('Введите город отправления: ')
    arrive_town = input('Введите город прибытия: ')
    date = input('Введите дату отъезда (в формате ГГГГ-ММ-ДД): ')
    print(find_shortest_paths(depart_town,arrive_town,date))

if __name__ == '__main__':
    main()
