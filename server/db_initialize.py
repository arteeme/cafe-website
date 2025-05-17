from db import SessionLocal, engine, Base
from models import Table, MenuItem, Category
import datetime

def initialize_database():
    """Initialize database with some example data."""
    db = SessionLocal()
    
    # Check if tables already exist in the database
    tables_count = db.query(Table).count()
    menu_count = db.query(MenuItem).count()
    
    if tables_count == 0:
        print("Adding tables to the database...")
        # Add sample tables
        tables = [
            Table(table_number=1, capacity=2, location='окно', 
                  description='Уютный столик у окна для двоих', 
                  image='/images/table1.jpg'),
            Table(table_number=2, capacity=4, location='центр', 
                  description='Стандартный столик в центре зала', 
                  image='/images/table2.jpg'),
            Table(table_number=3, capacity=6, location='угол', 
                  description='Просторный столик в углу для большой компании', 
                  image='/images/table3.jpg'),
            Table(table_number=4, capacity=2, location='окно', 
                  description='Столик у окна с прекрасным видом', 
                  image='/images/table4.jpg'),
            Table(table_number=5, capacity=4, location='центр', 
                  description='Удобный столик в центре зала', 
                  image='/images/table5.jpg'),
            Table(table_number=6, capacity=8, location='отдельная комната', 
                  description='Столик в отдельном помещении для больших групп', 
                  image='/images/table6.jpg'),
        ]
        
        db.add_all(tables)
        db.commit()
        print(f"Added {len(tables)} tables to the database.")
    else:
        print(f"Database already has {tables_count} tables. Skipping...")
    
    # Add menu items if none exist
    if menu_count == 0:
        print("Adding menu items to the database...")
        
        # Create categories if they don't exist
        categories = ['завтрак', 'основное', 'суп', 'десерт', 'напиток']
        for category_name in categories:
            if not db.query(Category).filter(Category.name == category_name).first():
                db.add(Category(name=category_name))
        db.commit()
        
        # Add menu items
        menu_items = [
            # Завтраки
            MenuItem(
                name='Омлет с овощами', 
                description='Воздушный омлет с томатами, сладким перцем и зеленым луком', 
                price=250, 
                category='завтрак',
                image='/images/omelet.jpg',
                is_available=True
            ),
            MenuItem(
                name='Каша овсяная', 
                description='Питательная овсяная каша с фруктами и медом', 
                price=180, 
                category='завтрак',
                image='/images/oatmeal.jpg',
                is_available=True
            ),
            # Основные блюда
            MenuItem(
                name='Стейк из говядины', 
                description='Сочный стейк из мраморной говядины с овощами гриль', 
                price=760, 
                category='основное',
                image='/images/steak.jpg',
                is_available=True
            ),
            MenuItem(
                name='Паста Карбонара', 
                description='Классическая итальянская паста с беконом и сливочным соусом', 
                price=450, 
                category='основное',
                image='/images/carbonara.jpg',
                is_available=True
            ),
            # Супы
            MenuItem(
                name='Борщ', 
                description='Традиционный борщ со сметаной и пампушками', 
                price=320, 
                category='суп',
                image='/images/borscht.jpg',
                is_available=True
            ),
            MenuItem(
                name='Крем-суп грибной', 
                description='Нежный крем-суп из белых грибов и шампиньонов', 
                price=350, 
                category='суп',
                image='/images/mushroom_soup.jpg',
                is_available=True
            ),
            # Десерты
            MenuItem(
                name='Чизкейк', 
                description='Нежный чизкейк с ягодным соусом', 
                price=280, 
                category='десерт',
                image='/images/cheesecake.jpg',
                is_available=True
            ),
            MenuItem(
                name='Тирамису', 
                description='Классический итальянский десерт с маскарпоне и кофе', 
                price=320, 
                category='десерт',
                image='/images/tiramisu.jpg',
                is_available=True
            ),
            # Напитки
            MenuItem(
                name='Латте', 
                description='Кофе с молоком и нежной молочной пенкой', 
                price=180, 
                category='напиток',
                image='/images/latte.jpg',
                is_available=True
            ),
            MenuItem(
                name='Свежевыжатый апельсиновый сок', 
                description='Сок из свежих апельсинов', 
                price=220, 
                category='напиток',
                image='/images/orange_juice.jpg',
                is_available=True
            ),
        ]
        
        db.add_all(menu_items)
        db.commit()
        print(f"Added {len(menu_items)} menu items to the database.")
    else:
        print(f"Database already has {menu_count} menu items. Skipping...")
    
    db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    initialize_database()
    print("Database initialization completed!") 