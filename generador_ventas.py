import pandas as pd
import random
from datetime import datetime, timedelta

menu = {
    "Café Americano": 1.50, "Café Latte": 2.50, "Capuccino": 2.50,
    "Té Helado": 2.00, "Agua Embotellada": 1.00, "Refresco": 1.50,
    "Sandwich de Pollo": 4.50, "Sandwich Vegetariano": 4.00, 
    "Croissant": 2.00, "Galleta con Chispas": 1.20,
    "Muffin de Arándanos": 2.20, "Ensalada César": 5.00, "Empanada de Carne": 2.00
}
products = list(menu.keys())


start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
days_in_year = (end_date - start_date).days + 1


DECLINE_START = 1.0   # peso relativo al inicio del periodo
DECLINE_END   = 0.8   # peso relativo al final  (~-20 %)

day_weights = [
    DECLINE_START + (DECLINE_END - DECLINE_START) * (d / (days_in_year - 1))
    for d in range(days_in_year)
]

num_registros = 20000
data = []

for _ in range(num_registros):
    # Seleccionar día con probabilidad ponderada (más peso → más probable)
    random_day = random.choices(range(days_in_year), weights=day_weights, k=1)[0]
    current_date = start_date + timedelta(days=random_day)
    hour = random.randint(7, 19) 
    time_str = f"{hour:02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
    
    
    product = random.choice(products)
    unit_price = menu[product]
    quantity = random.choices([1, 2, 3, 4], weights=[0.7, 0.2, 0.07, 0.03])[0]
    total = round(unit_price * quantity, 2)
    
    data.append([current_date.strftime("%Y-%m-%d"), time_str, product, quantity, unit_price, total])


df = pd.DataFrame(data, columns=["Fecha", "Hora", "Nombre de Producto", "Cantidad", "Precio Unitario", "Valor Total"])

df = df.sort_values(by=["Fecha", "Hora"]).reset_index(drop=True)
df.insert(0, "ID de Compra", [f"CAF-{i+1:05d}" for i in range(len(df))])

df.to_csv("ventas_cafeteria.csv", index=False)