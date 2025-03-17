import csv
import time
from datetime import datetime
from models import db, Inventory
from app import app

# CSV file name
CSV_FILE = "Cleaned_Inventory_Data.csv"

def clean_value(value, default="Unknown"):
    """Returns a cleaned value or a default if empty."""
    return value.strip() if value and value.strip() else default

def generate_unique_serial():
    """Creates a truly unique serial number using a timestamp."""
    return f"SN-{int(time.time() * 1000)}"  # Milliseconds to ensure uniqueness

def parse_date(date_str):
    """Parses a date string into a date object, returns None if invalid."""
    if date_str.strip():
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"⚠️ Invalid date: {date_str} - Defaulting to None")
            return None
    return None

def ensure_unique_serial(serial_number):
    """Ensures the generated serial number does not exist in the database."""
    while Inventory.query.filter_by(serial_number=serial_number).first():
        serial_number = generate_unique_serial()
    return serial_number

def import_inventory():
    with app.app_context():  # Ensure Flask context is active
        print("✅ Connecting to inventory.db...")

        # Open CSV file
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            counter = 1  # Counter for missing asset tags

            for row in reader:
                # Clean and retrieve data
                asset_tag = clean_value(row['asset_tag'], f"UNKNOWN-{counter}")
                site_name = clean_value(row['site_name'])
                room_number = clean_value(row['room_number'], "N/A")
                room_name = clean_value(row['room_name'])
                asset_type = clean_value(row['asset_type'])
                model = clean_value(row['model'])
                notes = clean_value(row['notes'], "No Notes")
                assigned_to = clean_value(row['assigned_to'], "Unassigned")
                date_assigned = parse_date(row['date_assigned'])
                date_decommissioned = parse_date(row['date_decommissioned'])

                # Check if serial number exists, if not generate a new one
                serial_number = clean_value(row['serial_number'])
                if serial_number == "Unknown":
                    serial_number = generate_unique_serial()
                
                serial_number = ensure_unique_serial(serial_number)  # Make sure it's unique

                # Check if the item already exists (using asset_tag)
                existing_item = Inventory.query.filter_by(asset_tag=asset_tag).first()

                if existing_item:
                    # 🔄 Update the existing record
                    existing_item.site_name = site_name
                    existing_item.room_number = room_number
                    existing_item.room_name = room_name
                    existing_item.asset_type = asset_type
                    existing_item.model = model
                    existing_item.serial_number = ensure_unique_serial(serial_number)  # Ensure uniqueness
                    existing_item.notes = notes
                    existing_item.assigned_to = assigned_to
                    existing_item.date_assigned = date_assigned
                    existing_item.date_decommissioned = date_decommissioned
                    print(f"🔄 Updated existing asset: {asset_tag}")

                else:
                    # 🆕 Insert a new record
                    new_item = Inventory(
                        site_name=site_name,
                        room_number=room_number,
                        room_name=room_name,
                        asset_tag=asset_tag,
                        asset_type=asset_type,
                        model=model,
                        serial_number=ensure_unique_serial(serial_number),  # Ensure uniqueness
                        notes=notes,
                        assigned_to=assigned_to,
                        date_assigned=date_assigned,
                        date_decommissioned=date_decommissioned
                    )
                    db.session.add(new_item)
                    print(f"✅ Inserted new asset: {asset_tag}")

                counter += 1  # Increment counter for missing asset tags

        # Commit all changes to the database
        db.session.commit()
        print("✅ Inventory data successfully imported.")

# Run the import script
if __name__ == "__main__":
    import_inventory()