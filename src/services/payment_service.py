from src.utils.validators import validate_amount, validate_currency, validate_email, generate_id
from src.repos.fake_payment_repo import FakePaymentRepository

class PaymentService:
    def __init__(self, repo: FakePaymentRepository):
        self.repo = repo
        self.STATUS_PENDING = 'pending'
        self.STATUS_SUCCEEDED = 'succeeded'
        self.STATUS_FAILED = 'failed'

    def create_customer(self, name: str, email: str):
        if not name or not name.strip():
            raise ValueError("Name is required")
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
        if not self.repo.find_customer_by_id(customer_id):
            raise ValueError("Customer not found")
        if not validate_amount(amount):
            raise ValueError("Invalid amount")
        if not validate_currency(currency):
            raise ValueError("Invalid currency")

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