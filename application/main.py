from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Banking Platform API",
    version="1.0.0"
)

accounts = [
    {
        "id": 1001,
        "customer_name": "John Doe",
        "account_type": "SAVINGS",
        "balance": 5000.00
    },
    {
        "id": 1002,
        "customer_name": "Jane Smith",
        "account_type": "CURRENT",
        "balance": 12500.50
    },
    {
        "id": 1003,
        "customer_name": "Alex Johnson",
        "account_type": "SAVINGS",
        "balance": 8200.75
    }
]


@app.get("/")
def root():
    return {
        "application": "Banking Platform",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/accounts")
def get_accounts():
    return accounts


@app.get("/api/accounts/{account_id}")
def get_account(account_id: int):
    for account in accounts:
        if account["id"] == account_id:
            return account

    raise HTTPException(
        status_code=404,
        detail="Account not found"
    )