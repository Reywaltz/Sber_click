from dataclasses import dataclass
from internal.models.customer import Customer, Storage, CustomerFull
from pkg.postgres.db import DB


customer_fields = "username, tg_id"
insert_customer = f"INSERT INTO customer ({customer_fields}) VALUES (%s, %s)"
update_customer = "UPDATE customer set username=%s, tg_id=%s where id=%s"
delete_customer = "DELETE FROM customer where id = %s"


@dataclass
class CustomerRepo(Storage):

    db: DB

    def insert(self, customer: Customer):
        cursor = self.db.session.cursor()
        try:
            cursor.execute(insert_customer, (customer.username,
                                             customer.tg_id))
            self.db.session.commit()

        except Exception as e:
            self.db.session.rollback()
            raise e

    def delete(self, customer_id: int):
        cursor = self.db.session.cursor()
        try:
            cursor.execute(delete_customer, (customer_id,))
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def update(self, customer: CustomerFull) -> int:
        try:
            cursor = self.db.session.cursor()
            cursor.execute(update_customer, (customer.username,
                                             customer.tg_id,
                                             customer.id))
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def getall(self):
        ...


def new_CustomerRepo(db: DB) -> CustomerRepo:
    return CustomerRepo(db=db)
