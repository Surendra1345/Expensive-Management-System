from fastapi import FastAPI

from api import login,roles,departments,employees,categories,expensive_claim,expensive_line_items,status_history,reimbursement_payment,budget_request,partial_reimbursement,audit_log

app=FastAPI()
 
app.include_router(login.router)
app.include_router(roles.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(categories.router)
app.include_router(expensive_claim.router)
app.include_router(expensive_line_items.router)
app.include_router(status_history.router)
app.include_router(reimbursement_payment.router)
app.include_router(partial_reimbursement.router)
app.include_router(budget_request.router)
app.include_router(audit_log.router)
