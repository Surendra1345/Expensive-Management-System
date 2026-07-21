from api.Authentication.database import engine, Base


import Authentication.models as models

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")