from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from src.repos.fake_payment_repo import FakePaymentRepository
from src.services.payment_service import PaymentService

app = FastAPI(title="Fake Payment Server")

repo = FakePaymentRepository()
service = PaymentService(repo)

# --- Pydantic Models ---
class CustomerCreate(BaseModel):
    name: str
    email: str

class PaymentCreate(BaseModel):
    customer_id: str
    amount: int
    currency: str

# --- Routes ---
@app.post("/customers", status_code=status.HTTP_201_CREATED)
def create_customer(customer_data: CustomerCreate):
    try:
        return service.create_customer(customer_data.name, customer_data.email)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Email already exists":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

@app.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate):
    try:
        return service.create_payment(
            payment_data.customer_id, 
            payment_data.amount, 
            payment_data.currency
        )
    except ValueError as e:
        error_msg = str(e)
        # Match the specific error strings from your payment_service.py
        if error_msg == "Customer not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        
        # Catch other errors like "Invalid amount" or "Invalid currency"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)