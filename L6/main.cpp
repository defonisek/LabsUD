#include <iostream>
#include <string>
#include <cstring>

EXEC SQL INCLUDE sqlca;

void show_menu(bool is_admin){
    std::cout << "\nМеню:\n";
    std::cout << "1. Просмотреть все товары\n";
    std::cout << "2. Поиск по названию\n";
    if(is_admin){ // UI не выводит эти поля обычному юзеру, но ограничение на использование
        std::cout << "3. Добавить товар\n"; // функций происходит в коде
        std::cout << "4. Обновить товар\n";
        std::cout << "5. Удалить товар\n";
        std::cout << "6. Очистить таблицу\n";
        std::cout << "7. Создать пользователя\n";
    }
    std::cout << "0. Выход\n";
}

int main(){
    EXEC SQL BEGIN DECLARE SECTION;
    char dbname[32] = "book_shop";
    char user[32], password[32];
    EXEC SQL END DECLARE SECTION;

    std::cout << "Логин: ";
    std::cin >> user;
    std::cout << "Пароль: ";
    std::cin >> password;

    EXEC SQL CONNECT TO :dbname USER :user USING :password;
    if(sqlca.sqlcode != 0){
        std::cerr << "Ошибка подключения!\n";
    }
    EXEC SQL BEGIN DECLARE SECTION;
    bool is_admin;
    EXEC SQL END DECLARE SECTION;
    
    EXEC SQL SELECT pg_has_role(:user, 'admin', 'MEMBER') INTO :is_admin;
    
    if (sqlca.sqlcode != 0) {
        std::cerr << "Ошибка проверки прав: " << sqlca.sqlerrm.sqlerrmc << "\n";
        is_admin = false;
    }
    int choice;
    do{
        show_menu(is_admin);
        std::cin >> choice;
        
        EXEC SQL BEGIN DECLARE SECTION;
        char search_term[100];
        int id, stock;
        double price;
        char name[100], category[50], description[200];
        char new_user[32], new_pass[32];
        EXEC SQL END DECLARE SECTION;
        switch(choice){
            case 1:{
                EXEC SQL DECLARE cur CURSOR FOR 
                SELECT * FROM products;
                EXEC SQL OPEN cur;
                std::cout << "\nСписок товаров:\nID | Название | Категория | Цена | Остаток\n";
                while(true){
                    EXEC SQL FETCH cur INTO :id, :name, :category, :price, :stock, :description;
                    if(sqlca.sqlcode) break;
                    std::cout << id << " | " << name << " | " << category 
                              << " | " << price << " | " << stock << "\n";
                }
                EXEC SQL CLOSE cur;
                break;
            }
            
            case 2:{
                std::cout << "Введите поисковый запрос: ";
                std::cin.ignore();
                std::cin.getline(search_term, 100);
                EXEC SQL DECLARE search_cur CURSOR FOR 
                SELECT * FROM search_products(:search_term);
                EXEC SQL OPEN search_cur;
                std::cout << "\nРезультаты поиска:\nID | Название | Категория | Цена | Остаток\n";
                while(true){
                    EXEC SQL FETCH search_cur INTO :id, :name, :category, :price, :stock, :description;
                    if(sqlca.sqlcode) break;
                    std::cout << id << " | " << name << " | " << category 
                              << " | " << price << " | " << stock << "\n";
                }
                EXEC SQL CLOSE search_cur;
                break;
            }
            
            case 3:{
                if(!is_admin) break;
                std::cout << "Введите название: ";
                std::cin.ignore();
                std::cin.getline(name, 100);
                std::cout << "Категория (book/stationery/souvenir): ";
                std::cin.getline(category, 50);
                std::cout << "Цена: ";
                std::cin >> price;
                std::cout << "Остаток: ";
                std::cin >> stock;
                std::cin.ignore();
                std::cout << "Описание: ";
                std::cin.getline(description, 200);
                try{
                    EXEC SQL SELECT add_product(:name, :category, :price, :stock, :description);
                    EXEC SQL COMMIT;
        
                    if(sqlca.sqlcode == 0) {
                        std::cout << "Данные добавлены!\n";
                    } 
                    else{
                        std::cerr << "Ошибка SQL: " << sqlca.sqlerrm.sqlerrmc 
                        << " (код: " << sqlca.sqlcode << ")\n";
                    }
                } 
                catch(const std::exception& e){
                    std::cerr << "Исключение: " << e.what() << "\n";
                EXEC SQL ROLLBACK;
                }
                break;
            }
            
            case 4:{
                if(!is_admin) break;
                std::cout << "Введите ID товара: ";
                std::cin >> id;
                std::cout << "Новое название: ";
                std::cin.ignore();
                std::cin.getline(name, 100);
                std::cout << "Новая цена: ";
                std::cin >> price;
                std::cout << "Новый остаток: ";
                std::cin >> stock;
                EXEC SQL SELECT update_product(:id, :name, :price, :stock);
                EXEC SQL COMMIT; 
                if(sqlca.sqlcode == 0)
                    std::cout << "Товар обновлен!\n";
                break;
            }
            
            case 5:{
                if(!is_admin) break;
                std::cout << "Введите название для удаления: ";
                std::cin.ignore();
                std::cin.getline(name, 100);
                EXEC SQL SELECT delete_by_name(:name);
                EXEC SQL COMMIT; 
                if(sqlca.sqlcode == 0)
                    std::cout << "Удалено " << sqlca.sqlerrd[2] << " записей\n";
                break;
            }
            
            case 6:{
                if(!is_admin) break;
                std::cout << "Вы уверены? (y/n): ";
                char confirm;
                std::cin >> confirm;
                if(confirm == 'y' || confirm == 'Y') {
                    EXEC SQL CALL truncate_products();
                    EXEC SQL COMMIT; 
                    std::cout << "Таблица очищена!\n";
                }
                break;
            }
            
            case 7:{
                if(!is_admin) break;
                char is_admin_flag;
                EXEC SQL BEGIN DECLARE SECTION;
                int is_admin_int;
                EXEC SQL END DECLARE SECTION;
                std::cout << "Введите логин: ";
                std::cin.ignore();
                std::cin.getline(new_user, 32);
                std::cout << "Введите пароль: ";
                std::cin.getline(new_pass, 32);
                std::cout << "Дать права админа? (y/n): ";
                std::cin >> is_admin_flag;
                is_admin_int = (is_admin_flag == 'y' || is_admin_flag == 'Y') ? 1 : 0;
                EXEC SQL CALL create_user(:new_user, :new_pass, :is_admin_int);
                EXEC SQL COMMIT; 
                if(sqlca.sqlcode == 0)
                    std::cout << "Пользователь создан!\n";
                break;
            }
        }
    }while(choice != 0);

    EXEC SQL DISCONNECT;
    return 0;
}