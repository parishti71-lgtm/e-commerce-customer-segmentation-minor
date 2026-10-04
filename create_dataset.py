import csv
from datetime import datetime, timedelta
from pathlib import Path

headers = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]

base_date = datetime(2024, 1, 1)

rows = [
    ["INV1001", "A100", "Wireless Mouse", 2, base_date + timedelta(days=1), 25.50, 1001, "United Kingdom"],
    ["INV1002", "A101", "Mechanical Keyboard", 1, base_date + timedelta(days=2), 55.00, 1002, "United Kingdom"],
    ["INV1003", "A102", "USB Hub", 3, base_date + timedelta(days=3), 18.75, 1003, "France"],
    ["INV1004", "A103", "Monitor Stand", 2, base_date + timedelta(days=4), 40.00, 1001, "United Kingdom"],
    ["INV1005", "A104", "Laptop Sleeve", 4, base_date + timedelta(days=5), 22.00, 1004, "Germany"],
    ["INV1006", "A105", "Office Chair", 1, base_date + timedelta(days=6), 120.00, 1005, "Spain"],
    ["INV1007", "A106", "Notebook", 10, base_date + timedelta(days=7), 3.50, 1006, "Belgium"],
    ["INV1008", "A107", "Desk Lamp", 2, base_date + timedelta(days=8), 35.00, 1007, "United Kingdom"],
    ["INV1009", "A108", "Webcam", 1, base_date + timedelta(days=9), 70.00, 1008, "Italy"],
    ["INV1010", "A109", "Bluetooth Speaker", 2, base_date + timedelta(days=10), 48.20, 1002, "United Kingdom"],
    ["INV1011", "A110", "Printer Paper", 5, base_date + timedelta(days=11), 9.25, 1009, "Netherlands"],
    ["INV1012", "A111", "Pen Set", 12, base_date + timedelta(days=12), 7.80, 1010, "France"],
    ["INV1013", "A112", "Coffee Mug", 6, base_date + timedelta(days=13), 4.90, 1003, "France"],
    ["INV1014", "A113", "Eraser Pack", 20, base_date + timedelta(days=14), 1.20, 1011, "Germany"],
    ["INV1015", "A114", "Headphones", 1, base_date + timedelta(days=15), 63.00, 1012, "United Kingdom"],
    ["INV1016", "A115", "Tablet Stand", 2, base_date + timedelta(days=16), 28.25, 1004, "Germany"],
    ["INV1017", "A116", "Portable SSD", 1, base_date + timedelta(days=17), 95.00, 1013, "United States"],
    ["INV1018", "A117", "Gaming Mouse", 3, base_date + timedelta(days=18), 29.99, 1001, "United Kingdom"],
    ["INV1019", "A118", "USB-C Cable", 8, base_date + timedelta(days=19), 6.75, 1014, "Spain"],
    ["INV1020", "A119", "Water Bottle", 4, base_date + timedelta(days=20), 12.50, 1015, "Belgium"],
    ["INV1021", "A120", "Flash Drive", 5, base_date + timedelta(days=21), 14.10, 1006, "Belgium"],
    ["INV1022", "A121", "Laptop Cooling Pad", 2, base_date + timedelta(days=22), 34.00, 1007, "United Kingdom"],
    ["INV1023", "A122", "Smartphone Case", 3, base_date + timedelta(days=23), 16.40, 1016, "Italy"],
    ["INV1024", "A123", "Desk Organizer", 5, base_date + timedelta(days=24), 18.50, 1009, "Netherlands"],
    ["INV1025", "A124", "Bluetooth Earbuds", 2, base_date + timedelta(days=25), 44.00, 1017, "United States"],
    ["INV1026", "A125", "Projector", 1, base_date + timedelta(days=26), 250.00, 1018, "France"],
    ["INV1027", "A126", "Keyboard Cover", 4, base_date + timedelta(days=27), 10.20, 1019, "Germany"],
    ["INV1028", "A127", "USB Fan", 6, base_date + timedelta(days=28), 15.60, 1002, "United Kingdom"],
    ["INV1029", "A128", "Wall Clock", 2, base_date + timedelta(days=29), 22.00, 1008, "Italy"],
    ["INV1030", "A129", "Desk Calendar", 12, base_date + timedelta(days=30), 2.90, 1020, "Spain"],
]

output_path = Path(__file__).resolve().parent / "Online Retail.csv"
with output_path.open("w", newline="", encoding="utf-8") as dataset_file:
    writer = csv.writer(dataset_file)
    writer.writerow(headers)
    writer.writerows(
        [
            *row[:4],
            row[4].strftime("%Y-%m-%d %H:%M:%S"),
            *row[5:],
        ]
        for row in rows
    )

print(f"Created {output_path.name} in {output_path.parent}.")
