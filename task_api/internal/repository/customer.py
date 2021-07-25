from dataclasses import dataclass

from internal.models.customer import Customer, CustomerFull, Storage
from psycopg2.extensions import connection

customer_fields = "name, tg_id, tg_name, tg_chat"
insert_customer = f"INSERT INTO customer ({customer_fields})\
                  VALUES (%s, %s, %s, %s)"
update_customer = "UPDATE customer set name=%s, tg_id=%s, tg_name=%s,\
                  tg_chat=%s where id=%s"
delete_customer = "DELETE FROM customer where id = %s"


@dataclass
class CustomerRepo(Storage):

    db: connection

    def insert(self, customer: Customer):
        cursor = self.db.cursor()
        try:
            cursor.execute(insert_customer, (customer.name,
                                             customer.tg_id,
                                             customer.tg_name,
                                             customer.tg_chat))
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, customer_id: int):
        cursor = self.db.cursor()
        try:
            cursor.execute(delete_customer, (customer_id,))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def update(self, customer: CustomerFull) -> int:
        try:
            cursor = self.db.cursor()
            cursor.execute(update_customer, (customer.name,
                                             customer.tg_id,
                                             customer.tg_name,
                                             customer.tg_chat,
                                             customer.id,))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e


def new_CustomerRepo(db) -> CustomerRepo:
    return CustomerRepo(db=db)
