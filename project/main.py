from api_request import path
import graphs as gp

def main():
    depart_town = input('Введите город отправления: ')
    arrive_town = input('Введите город прибытия: ')
    date = input('Введите дату отъезда (в формате ГГГГ-ММ-ДД): ')
    print(gp.graph(depart_town, arrive_town, date))

if __name__ == '__main__':
    main()
