from api_request import path

def main():
    depart_town = input('Введите город отправления ')
    arrive_town = input('Введите город прибытия ')
    date = input('Введите дату отъезда ')
    print(path(depart_town, arrive_town, date))

if __name__ == '__main__':
    main()
