class FakePaymentRepository:
    def __init__(self):
        self.customers = {}
        self.payments = {}
        self.refunds = {}

    def save_customer(self, customer: dict):
        self.customers[customer['id']] = customer
        return customer

    def find_customer_by_id(self, customer_id: str):
        return self.customers.get(customer_id)

    def find_customer_by_email(self, email: str):
        for customer in self.customers.values():
            if customer.get('email') == email:
                return customer
        return None

    def save_payment(self, payment: dict):
        self.payments[payment['id']] = payment
        return payment

    def clear(self):
        self.customers.clear()
        self.payments.clear()
        self.refunds.clear()