import time
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection parameters
DB_PARAMS = {
    'database': 'project',
    'user': 'postgres',
    'password': 'vijaya',
    'host': 'localhost',
    'port': '5432'
}

def connect_db():
    retries = 3
    wait_time = 2  # Initial wait time between retries in seconds
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            logging.info("Database connection successful")
            return conn
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"Database connection failed, attempt {attempt + 1} of {retries}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  # Increase wait time for the next retry
            else:
                logging.error("Database connection failed after multiple attempts: " + str(e))
                messagebox.showerror("Database Connection Error", str(e))
                return None

def execute_sql(sql, params=None, commit=False):
    conn = connect_db()
    if conn is not None:
        try:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            if commit:
                conn.commit()
                return True
            return cur.fetchall() if cur.description else None
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", str(e))
            return None
        finally:
            conn.close()
    return None

def refresh_table_data(tree, query):
    for row in tree.get_children():
        tree.delete(row)
    rows = execute_sql(query)
    for row in rows:
        tree.insert('', tk.END, values=row)

class DatabaseApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("CS-623 Project")

        # Setup Tabs
        tab_control = ttk.Notebook(root)
        self.tab_manage = ttk.Frame(tab_control)
        self.tab_data = ttk.Frame(tab_control)
        tab_control.add(self.tab_manage, text='Console')
        tab_control.add(self.tab_data, text='Data Viewer')
        tab_control.pack(expand=1, fill="both")

        # Management Tab
        self.setup_management_tab()

        # Data Tab
        self.setup_data_tab()

    
    def setup_management_tab(self):
        # Commands for setup, seed, clear, and delete tables
        ttk.Button(self.tab_manage, text="Setup Tables", command=self.setup_tables).pack(pady=10)
        ttk.Button(self.tab_manage, text="Seed Data", command=self.seed_database).pack(pady=10)
        ttk.Button(self.tab_manage, text="Clear Data", command=self.clear_data).pack(pady=10)
        ttk.Button(self.tab_manage, text="Delete Tables", command=self.delete_tables).pack(pady=10)

        # Section to delete a department
        delete_frame = ttk.Frame(self.tab_manage)
        delete_frame.pack(side='top', fill='x', padx=10, pady=10)

        # Section to delete a product
        product_delete_frame = ttk.LabelFrame(delete_frame, text="Delete Product", padding=(10, 10))
        product_delete_frame.pack(side='left', fill='x', padx=20, pady=10, expand=True)
        ttk.Label(product_delete_frame, text="Product ID:").pack(side='top', fill='x')
        product_id_entry = ttk.Entry(product_delete_frame)
        product_id_entry.pack(side='top', fill='x', pady=(0, 5))
        ttk.Button(product_delete_frame, text="Delete", command=lambda: self.delete_product(product_id_entry.get())).pack(side='top')

        # Section to delete a department
        department_delete_frame = ttk.LabelFrame(delete_frame, text="Delete Department", padding=(10, 10))
        department_delete_frame.pack(side='right', fill='x', padx=20, pady=10, expand=True)
        ttk.Label(department_delete_frame, text="Department ID:").pack(side='top', fill='x')
        department_id_entry = ttk.Entry(department_delete_frame)
        department_id_entry.pack(side='top', fill='x', pady=(0, 5))
        ttk.Button(department_delete_frame, text="Delete", command=lambda: self.delete_department(department_id_entry.get())).pack(side='top')
        
        # Frame for Rename
        rename_frame = ttk.Frame(self.tab_manage)
        rename_frame.pack(fill='none', padx=10, pady=10, expand=True)
        
        # Section to rename a product
        rename_product_frame = ttk.LabelFrame(self.tab_manage, text="Rename Product", padding=(10, 10))
        rename_product_frame.pack(side='left', fill='none', padx=20, pady=10, expand=True)

        # Old Product ID
        ttk.Label(rename_product_frame, text="Old Product ID:").pack(side='top', fill='x', expand=True)
        old_prod_id_entry = ttk.Entry(rename_product_frame)
        old_prod_id_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        # New Product ID
        ttk.Label(rename_product_frame, text="New Product ID:").pack(side='top', fill='x', expand=True)
        new_prod_id_entry = ttk.Entry(rename_product_frame)
        new_prod_id_entry.pack(side='top', fill='x', expand=True, pady=(0, 10))

        # Button to trigger the rename operation
        ttk.Button(rename_product_frame, text="Change", command=lambda: self.rename_product(old_prod_id_entry.get(), new_prod_id_entry.get())).pack(side='top')

        # Section to rename a department
        rename_department_frame = ttk.LabelFrame(self.tab_manage, text="Rename Department", padding=(10, 10))
        rename_department_frame.pack(side='right', fill='none', padx=20, pady=10, expand=True)

        # Old Department ID
        ttk.Label(rename_department_frame, text="Old Department ID:").pack(side='top', fill='x', expand=True)
        old_dep_id_entry = ttk.Entry(rename_department_frame)
        old_dep_id_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        # New Department ID
        ttk.Label(rename_department_frame, text="New Department ID:").pack(side='top', fill='x', expand=True)
        new_dep_id_entry = ttk.Entry(rename_department_frame)
        new_dep_id_entry.pack(side='top', fill='x', expand=True, pady=(0, 10))

        # Button to trigger the rename operation
        ttk.Button(rename_department_frame, text="Change", command=lambda: self.rename_department(old_dep_id_entry.get(), new_dep_id_entry.get())).pack(side='top')

        #Frame for Updates
        update_frame = ttk.Frame(self.tab_manage)
        update_frame.pack(side='bottom', fill='none', padx=10, pady=10, expand=True)

        # Main frame for adding sections
        add_frame = ttk.Frame(update_frame)
        add_frame.pack(fill='x', padx=10, pady=10, expand=True)
        
        # Section to add a product and stock
        add_product_frame = ttk.LabelFrame(add_frame, text="Add Product", padding=(10, 10))
        add_product_frame.pack(side='left', fill='x', padx=20, pady=10, expand=True)

        ttk.Label(add_product_frame, text="Product ID:").pack(side='top', fill='x', expand=True)
        prod_id_entry = ttk.Entry(add_product_frame)
        prod_id_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_product_frame, text="Name:").pack(side='top', fill='x', expand=True)
        prod_name_entry = ttk.Entry(add_product_frame)
        prod_name_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_product_frame, text="Price:").pack(side='top', fill='x', expand=True)
        price_entry = ttk.Entry(add_product_frame)
        price_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_product_frame, text="Dep ID:").pack(side='top', fill='x', expand=True)
        dep_id_entry = ttk.Entry(add_product_frame)
        dep_id_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_product_frame, text="Quantity:").pack(side='top', fill='x', expand=True)
        quantity_entry = ttk.Entry(add_product_frame)
        quantity_entry.pack(side='top', fill='x', expand=True, pady=(0, 10))

        ttk.Button(add_product_frame, text="Add Product", command=lambda: self.add_product_and_stock(
            prod_id_entry.get(), prod_name_entry.get(), price_entry.get(), dep_id_entry.get(), quantity_entry.get())).pack(side='top')

        # Section to add a department and stock
        add_department_frame = ttk.LabelFrame(add_frame, text="Add Department", padding=(10, 10))
        add_department_frame.pack(side='right', fill='x', padx=20, pady=10, expand=True)

        ttk.Label(add_department_frame, text="Dep ID:").pack(side='top', fill='x', expand=True)
        dep_id_d_entry = ttk.Entry(add_department_frame)
        dep_id_d_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_department_frame, text="Address:").pack(side='top', fill='x', expand=True)
        location_entry = ttk.Entry(add_department_frame)
        location_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_department_frame, text="Volume:").pack(side='top', fill='x', expand=True)
        volume_entry = ttk.Entry(add_department_frame)
        volume_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_department_frame, text="Prod ID for Stock:").pack(side='top', fill='x', expand=True)
        prod_id_for_stock_entry = ttk.Entry(add_department_frame)
        prod_id_for_stock_entry.pack(side='top', fill='x', expand=True, pady=(0, 5))

        ttk.Label(add_department_frame, text="Quantity:").pack(side='top', fill='x', expand=True)
        quantity_d_entry = ttk.Entry(add_department_frame)
        quantity_d_entry.pack(side='top', fill='x', expand=True, pady=(0, 10))

        ttk.Button(add_department_frame, text="Add Department", command=lambda: self.add_department_and_stock(
            dep_id_d_entry.get(), location_entry.get(), volume_entry.get(), prod_id_for_stock_entry.get(), quantity_d_entry.get())).pack(side='top')
        
    
    def setup_data_tab(self):
        # Displaying data in tables
        self.tree_product = ttk.Treeview(self.tab_data, columns=('prod', 'name', 'price'), show="headings")
        self.tree_product.heading('prod', text='Product ID')
        self.tree_product.heading('name', text='Name')
        self.tree_product.heading('price', text='Price')
        self.tree_product.pack(side="top", fill="x")

        self.tree_department = ttk.Treeview(self.tab_data, columns=('dep', 'addr', 'volume'), show="headings")
        self.tree_department.heading('dep', text='Department ID')
        self.tree_department.heading('addr', text='Address')
        self.tree_department.heading('volume', text='Volume')
        self.tree_department.pack(side="top", fill="x")

        self.tree_stock = ttk.Treeview(self.tab_data, columns=('prod', 'dep', 'quantity'), show="headings")
        self.tree_stock.heading('prod', text='Product ID')
        self.tree_stock.heading('dep', text='Department ID')
        self.tree_stock.heading('quantity', text='Quantity')
        self.tree_stock.pack(side="top", fill="x")

        # Button to refresh data
        ttk.Button(self.tab_data, text="Refresh Data", command=self.refresh_data).pack(pady=10)

    
    def setup_tables(self):
        sql_commands = [
            """CREATE TABLE IF NOT EXISTS Product (
                prod VARCHAR(10) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL NOT NULL)""",
            """CREATE TABLE IF NOT EXISTS Department (
                dep VARCHAR(10) PRIMARY KEY,
                addr VARCHAR(255) NOT NULL,
                volume INTEGER NOT NULL)""",
            """CREATE TABLE IF NOT EXISTS Stock (
                prod VARCHAR(10),
                dep VARCHAR(10),
                quantity INTEGER NOT NULL,
                PRIMARY KEY (prod, dep),
                FOREIGN KEY (prod) REFERENCES Product(prod) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (dep) REFERENCES Department(dep) ON DELETE CASCADE ON UPDATE CASCADE)"""
        ]
        
        conn = connect_db()
        
        if conn is None:
            messagebox.showerror("Database Error", "Failed to connect to the database")
            return

        try:
            cur = conn.cursor()
            conn.autocommit = False  # Start transaction control
            for sql in sql_commands:
                cur.execute(sql)
            conn.commit()  # Commit all DDL operations as a single transaction
            messagebox.showinfo("Success", "Tables created successfully")
        except Exception as e:
            conn.rollback()  # Rollback transaction on error
            messagebox.showerror("Database Error", f"Failed to setup tables: {str(e)}")
        finally:
            conn.close()


    
    def seed_database(self):
        sqls = [
        "INSERT INTO Product (prod, name, price) VALUES ('p1', 'tape', 2.5), ('p2', 'tv', 250), ('p3', 'vcr', 80)","INSERT INTO Department (dep, addr, volume) VALUES ('d1', 'New York', 9000), ('d2', 'Syracuse', 6000), ('d3', 'New York', 2000)","INSERT INTO Stock (prod, dep, quantity) VALUES ('p1', 'd1', 1000), ('p1', 'd2', -100), ('p1', 'd3', 1200), ('p3', 'd1', 3000), ('p3', 'd3', 2000), ('p2', 'd3', 1500), ('p2', 'd1', -400), ('p2', 'd2', 2000)"
        ]
        conn = connect_db()
        try:
            cur = conn.cursor()
            conn.autocommit = False
            for sql in sqls:
                cur.execute(sql)
            conn.commit()
            messagebox.showinfo("Success", "Data seeded successfully")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    
    def clear_data(self):
        sqls = ["DELETE FROM Stock", "DELETE FROM Product", "DELETE FROM Department"]
        conn = connect_db()
        try:
            cur = conn.cursor()
            conn.autocommit = False
            for sql in sqls:
                cur.execute(sql)
            conn.commit()
            messagebox.showinfo("Success", "All data cleared successfully")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()


    
    def delete_tables(self):
        sql_commands = [
            "DROP TABLE IF EXISTS Stock",
            "DROP TABLE IF EXISTS Product",
            "DROP TABLE IF EXISTS Department"
        ]
        conn = connect_db()
        if conn is None:
            messagebox.showerror("Database Error", "Failed to connect to the database")
            return

        try:
            cur = conn.cursor()
            conn.autocommit = False  # Start transaction control
            for sql in sql_commands:
                cur.execute(sql)
            conn.commit()  # Commit all DROP operations as a single transaction
            messagebox.showinfo("Success", "All tables deleted successfully")
        except Exception as e:
            conn.rollback()  # Rollback transaction on error
            messagebox.showerror("Database Error", f"Failed to delete tables: {str(e)}")
        finally:
            conn.close()

        
    
    def delete_product(self, prod_id):
        if prod_id:
            sql = "DELETE FROM Product WHERE prod = %s"
            conn = connect_db()
            if conn is None:
                messagebox.showerror("Database Error", "Failed to connect to the database")
                return

            try:
                cur = conn.cursor()
                conn.autocommit = False  # Start transaction control
                cur.execute(sql, (prod_id,))
                conn.commit()  # Commit operation
                messagebox.showinfo("Success", "Product deleted successfully")
            except Exception as e:
                conn.rollback()  # Rollback transaction on error
                messagebox.showerror("Database Error", f"Failed to delete product: {str(e)}")
            finally:
                conn.close()
        else:
            messagebox.showwarning("Input Required", "Please enter a Product ID")


    
    def delete_department(self, dep_id):
        if dep_id:
            sql = "DELETE FROM Department WHERE dep = %s"
            conn = connect_db()
            if conn is None:
                messagebox.showerror("Database Error", "Failed to connect to the database")
                return

            try:
                cur = conn.cursor()
                conn.autocommit = False  # Start transaction control
                cur.execute(sql, (dep_id,))
                conn.commit()  # Commit operation
                messagebox.showinfo("Success", "Department deleted successfully")
            except Exception as e:
                conn.rollback()  # Rollback transaction on error
                messagebox.showerror("Database Error", f"Failed to delete department: {str(e)}")
            finally:
                conn.close()
        else:
            messagebox.showwarning("Input Required", "Please enter a Department ID")

            
    def rename_product(self, old_prod_id, new_prod_id):
        sql = "UPDATE Product SET prod = %s WHERE prod = %s"
        conn = connect_db()
        if conn is None:
            messagebox.showerror("Database Error", "Failed to connect to the database")
            return
        try:
            cur = conn.cursor()
            conn.autocommit = False  # Start transaction control
            cur.execute(sql, (new_prod_id, old_prod_id))
            if cur.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Success", f"Product ID updated successfully from {old_prod_id} to {new_prod_id}")
            else:
                conn.rollback()
                messagebox.showinfo("Error", f"No product found with ID {old_prod_id}, no updates made.")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error updating product ID: {str(e)}")
        finally:
            conn.close()


    def rename_department(self, old_dep_id, new_dep_id):
        sql = "UPDATE Department SET dep = %s WHERE dep = %s"
        conn = connect_db()
        if conn is None:
            messagebox.showerror("Database Error", "Failed to connect to the database")
            return
        try:
            cur = conn.cursor()
            conn.autocommit = False  # Start transaction control
            cur.execute(sql, (new_dep_id, old_dep_id))
            if cur.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Success", f"Department ID updated successfully from {old_dep_id} to {new_dep_id}")
            else:
                conn.rollback()
                messagebox.showinfo("Error", f"No department found with ID {old_dep_id}, no updates made.")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Error updating department ID: {str(e)}")
        finally:
            conn.close()
    
    def add_product_and_stock(self, prod_id, prod_name, price, dep_id, quantity):
        # Check if the department exists directly within this function
        department_check_sql = "SELECT EXISTS(SELECT 1 FROM Department WHERE dep = %s)"
        department_exists = execute_sql(department_check_sql, (dep_id,))
        
        if not department_exists or not department_exists[0][0]:
            messagebox.showerror("Error", "Department ID does not exist. Please add the department first.")
            return
        
        sql_product = "INSERT INTO Product (prod, name, price) VALUES (%s, %s, %s)"
        sql_stock = "INSERT INTO Stock (prod, dep, quantity) VALUES (%s, %s, %s)"
        
        conn = connect_db()
        if conn is None:
            messagebox.showerror("Database Error", "Failed to connect to the database")
            return

        try:
            cur = conn.cursor()
            conn.autocommit = False  # Start transaction control
            
            cur.execute(sql_product, (prod_id, prod_name, float(price)))  # Insert product
            cur.execute(sql_stock, (prod_id, dep_id, int(quantity)))      # Insert stock entry
            
            conn.commit()  # Commit both operations as a single transaction
            messagebox.showinfo("Success", "Product and stock added successfully")
        except Exception as e:
            conn.rollback()  # Rollback transaction on error
            messagebox.showerror("Database Error", f"Failed to add product and stock: {str(e)}")
        finally:
            conn.close()



    def add_department_and_stock(self, dep_id, location, volume, prod_id, quantity):
        # Check if the product exists directly within this function
        product_check_sql = "SELECT EXISTS(SELECT 1 FROM Product WHERE prod = %s)"
        product_exists = execute_sql(product_check_sql, (prod_id,))

        if not product_exists or not product_exists[0][0]:
            messagebox.showerror("Error", "Product ID does not exist. Please add the product first.")
            return

        sql_department = "INSERT INTO Department (dep, addr, volume) VALUES (%s, %s, %s)"
        sql_stock = "INSERT INTO Stock (prod, dep, quantity) VALUES (%s, %s, %s)"

        conn = connect_db()
        if conn is None:
            messagebox.showerror("Database Error", "Failed to connect to the database")
            return

        try:
            cur = conn.cursor()
            conn.autocommit = False  # Start transaction control
            
            # Insert into Department
            cur.execute(sql_department, (dep_id, location, int(volume)))

            # Insert into Stock
            cur.execute(sql_stock, (prod_id, dep_id, int(quantity)))

            conn.commit()  # Commit both operations as a single transaction
            messagebox.showinfo("Success", "Department and stock added successfully")
        except Exception as e:
            conn.rollback()  # Rollback transaction on error
            messagebox.showerror("Database Error", f"Failed to add department and stock: {str(e)}")
        finally:
            conn.close()



    def refresh_data(self):
        # This function will refresh the data in the tree views
        self.refresh_table_data(self.tree_product, "SELECT * FROM Product")
        self.refresh_table_data(self.tree_department, "SELECT * FROM Department")
        self.refresh_table_data(self.tree_stock, "SELECT * FROM Stock")
        
    
    def refresh_table_data(self, tree, query):
        # Clear existing data
        for row in tree.get_children():
            tree.delete(row)
        # Fetch new data
        rows = execute_sql(query)
        if rows:
            for row in rows:
                tree.insert('', tk.END, values=row)
        else:
            # Log if no data found or there was an error
            print("No data found or error fetching data")


if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()

