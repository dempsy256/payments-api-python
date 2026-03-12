from src.utils.validators import validate_amount, validate_currency, validate_email, generate_id
from src.repos.fake_payment_repo import FakePaymentRepository

class PaymentService:
    def __init__(self, repo: FakePaymentRepository):
        self.repo = repo
        self.STATUS_PENDING = 'pending'
        self.STATUS_SUCCEEDED = 'succeeded'
        self.STATUS_FAILED = 'failed'

    def create_customer(self, name: str, email: str):
        # Enforce name length boundaries
        if not name or len(name) < 1 or len(name) > 100:
            raise ValueError("Invalid name length")
        if not validate_email(email):
            raise ValueError("Invalid email")
        if self.repo.find_customer_by_email(email):
            raise ValueError("Email already exists")

        customer = {
            "id": generate_id("cus"),
            "name": name,
            "email": email
        }
        return self.repo.save_customer(customer)

    def create_payment(self, customer_id: str, amount: int, currency: str):
        if not validate_amount(amount):
            raise ValueError("Invalid amount")
        if not validate_currency(currency):
            raise ValueError("Invalid currency")
        if not self.repo.find_customer_by_id(customer_id):
            raise ValueError("Customer not found")

        payment = {
            "id": generate_id("pay"),
            "customer_id": customer_id,
            "amount": amount,
            "currency": currency,
            "status": self.STATUS_PENDING
        }
        return self.repo.save_payment(payment)
    
    def capture_payment(self, payment_id: str):
        payment = self.repo.find_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        if payment["status"] != self.STATUS_PENDING:
            raise ValueError("Payment cannot be captured")
            
        # Update status and save it back to our fake database
        payment["status"] = self.STATUS_SUCCEEDED
        self.repo.save_payment(payment)
        
        return payment
    
    def create_refund(self, payment_id: str, amount: int):
        payment = self.repo.find_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        # Validate that we don't refund more than the original payment
        if amount > payment["amount"]:
            raise ValueError("Refund amount exceeds payment amount")
            
        refund = {
            "id": generate_id("ref"),
            "paymentId": payment_id,
            "amount": amount
        }
        return self.repo.save_refund(refund)
    
    def get_all_payments(self):
        return self.repo.get_all_payments()
    
    def get_customer(self, customer_id: str):
        customer = self.repo.find_customer_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        return customer

    def get_customer_payments(self, customer_id: str):
        # Must verify the customer exists first, otherwise it's a 404!
        if not self.repo.find_customer_by_id(customer_id):
            raise ValueError("Customer not found")
        return self.repo.find_payments_by_customer_id(customer_id)

    def get_payment(self, payment_id: str):
        payment = self.repo.find_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        return payment

    def fail_payment(self, payment_id: str):
        payment = self.repo.find_payment_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        if payment["status"] != self.STATUS_PENDING:
            raise ValueError("Payment cannot be failed")
            
        payment["status"] = self.STATUS_FAILED
        self.repo.save_payment(payment)
        return payment

    def get_refund(self, refund_id: str):
        refund = self.repo.find_refund_by_id(refund_id)
        if not refund:
            raise ValueError("Refund not found")
        return refund